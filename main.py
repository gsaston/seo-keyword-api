from flask import Flask, request, jsonify
import spacy
from fuzzywuzzy import fuzz
import re

# Load language models
models = {
    "de": spacy.load("de_core_news_sm"),
    "fi": spacy.load("fi_core_news_sm")
}

def normalize(text):
    text = text.lower()
    text = re.sub(r"[’'‘]", "'", text)
    text = re.sub(r"[^a-zäöåüßæøA-Z\s]", " ", text)
    return text.strip()

def lemmatize(text, lang):
    nlp = models.get(lang)
    if not nlp:
        return normalize(text)
    doc = nlp(text)
    return normalize(" ".join([token.lemma_ for token in doc]))

app = Flask(__name__)

@app.route("/analyse", methods=["POST"])
def analyse():
    data = request.json
    text = data.get("text", "")
    keywords = data.get("keywords", [])
    lang = data.get("lang", "de")

    lemmatised_text = lemmatize(text, lang)
    used = []
    missing = []

    for keyword in keywords:
        kw_norm = normalize(keyword)
        if kw_norm in lemmatised_text:
            used.append(keyword)
        elif fuzz.partial_ratio(kw_norm, lemmatised_text) > 85:
            used.append(keyword + " (fuzzy)")
        else:
            missing.append(keyword)

    return jsonify({
        "used": used,
        "missing": missing
    })

@app.route("/", methods=["GET"])
def health_check():
    return "API is running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
