import random
import re
from typing import List, Dict

import nltk
from docx import Document


def initialize_nlp_resources() -> Dict:
    """
    Initialize required NLP resources without using global variables.
    """
    nltk.download('wordnet', quiet=True)
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
    nltk.download('stopwords', quiet=True)

    return {
        "lemmatizer": nltk.stem.WordNetLemmatizer(),
        "stop_words": set(nltk.corpus.stopwords.words('english')),
    }


def get_wordnet_pos(treebank_tag: str) -> str:
    if treebank_tag.startswith('J'):
        return nltk.corpus.wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return nltk.corpus.wordnet.VERB
    elif treebank_tag.startswith('N'):
        return nltk.corpus.wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return nltk.corpus.wordnet.ADV
    return nltk.corpus.wordnet.NOUN


def get_synonyms(word: str, pos: str, lemmatizer, stop_words: set) -> List[str]:
    return [
        lemma.name() for syn in nltk.corpus.wordnet.synsets(word, pos)
        for lemma in syn.lemmas()
        if lemma.name() != word and lemma.name() not in stop_words
    ]


def change_word_order(words: List[str], probability: float = 0.1) -> List[str]:
    if len(words) < 4 or random.random() > probability:
        return words
    idx1, idx2 = random.sample(range(len(words)), 2)
    words[idx1], words[idx2] = words[idx2], words[idx1]
    return words


def enhance_sentence_structure(sentence: str) -> str:
    return _apply_sentence_modifications(sentence)


def _apply_sentence_modifications(sentence: str) -> str:
    clauses = [
        "which suggests that", "since it appears that", "although it is clear that",
        "because it has been shown that"
    ]
    pronouns = ['that', 'which', 'who', 'whom', 'whose']
    appositives = [
        ", a phenomenon well-known in the field", ", an aspect often overlooked",
        ", a term coined by experts"
    ]
    conjunction_replacements = {
        'and': ['moreover', 'furthermore', 'additionally'],
        'but': ['however', 'nevertheless', 'on the contrary'],
        'or': ['alternatively', 'or else', 'either'],
    }
    intro_phrases = ['In fact, ', 'Notably, ', 'Furthermore, ', 'Consequently, ']

    if random.random() < 0.3:
        clause = random.choice(clauses)
        pos = random.randint(5, len(sentence) - 5)
        sentence = sentence[:pos] + ' ' + clause + ' ' + sentence[pos:]

    if random.random() < 0.25 and 'is' in sentence:
        pronoun = random.choice(pronouns)
        insert_pos = sentence.find('is')
        sentence = sentence[:insert_pos] + ' ' + pronoun + ' ' + sentence[insert_pos:]

    if random.random() < 0.2:
        pattern = r'(\w+)( is| was| has been| have been)( \w+)'
        match = re.search(pattern, sentence)
        if match:
            verb, tense, object = match.groups()
            if verb not in ["is", "was"]:
                sentence = re.sub(pattern, f"{object} {tense} {verb}ed", sentence, 1)

    if random.random() < 0.15:
        insert_pos = random.randint(5, len(sentence) - 5)
        sentence = sentence[:insert_pos] + random.choice(appositives) + sentence[insert_pos:]

    for conj, replacements in conjunction_replacements.items():
        if conj in sentence:
            sentence = re.sub(
                rf'\b{re.escape(conj)}\b',
                lambda m: random.choice(replacements),
                sentence,
                1
            )

    if random.random() < 0.3:
        if '.' in sentence:
            sentence = re.sub(r'\.$', lambda m: ';' if random.random() < 0.5 else '.', sentence)
        elif ',' in sentence:
            sentence = re.sub(r',', lambda m: ';' if random.random() < 0.5 else ',', sentence, 1)

    if random.random() < 0.2 and len(sentence) > 30:
        pos = random.randint(10, len(sentence) - 10)
        first_part = sentence[:pos].rstrip()
        second_part = sentence[pos:].lstrip()
        if first_part and second_part:
            sentence = f"{first_part}. {second_part}"

    if random.random() < 0.15:
        sentence = random.choice(intro_phrases) + sentence
    return sentence


def paraphrase_text(text: str, lemmatizer, stop_words) -> str:
    sentences = nltk.sent_tokenize(text)
    new_sentences = []

    for sentence in sentences:
        words = nltk.word_tokenize(sentence)
        tagged = nltk.pos_tag(words)
        new_words = []

        for word, tag in tagged:
            if word.isalnum():
                wn_pos = get_wordnet_pos(tag)
                lemma = lemmatizer.lemmatize(word, pos=wn_pos)
                synonyms = get_synonyms(lemma, wn_pos, lemmatizer, stop_words)
                new_words.append(random.choice(synonyms) if synonyms else word)
            else:
                new_words.append(word)

        new_words = change_word_order(new_words)
        new_sentence = enhance_sentence_structure(' '.join(new_words))
        new_sentences.append(new_sentence)

    return ' '.join(new_sentences)


def read_file(file_path: str) -> str:
    try:
        if file_path.lower().endswith('.docx'):
            with open(file_path, 'rb') as file:
                doc = Document(file)
                return ' '.join([paragraph.text for paragraph in doc.paragraphs])
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        else:
            raise ValueError("Unsupported file format. Use .docx or .txt")
    except Exception as e:
        raise IOError(f"Error reading file: {str(e)}")


def process_document(file_path: str) -> str:
    nlp_resources = initialize_nlp_resources()
    lemmatizer = nlp_resources["lemmatizer"]
    stop_words = nlp_resources["stop_words"]

    try:
        content = read_file(file_path)
        return paraphrase_text(content, lemmatizer, stop_words)
    except (ValueError, IOError) as e:
        print(f"Processing error: {e}")
        return ""


if __name__ == "__main__":
    file_path = 'path/to/your/file.docx'
    try:
        processed_text = process_document(file_path)
        if processed_text:
            print(f"Processed text:\n{processed_text}")
        else:
            print("No text was processed or an error occurred.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
