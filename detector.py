import math
from collections import Counter
from typing import Tuple

import nltk
from docx import Document
from nltk.corpus import wordnet
from nltk.tag import pos_tag
from nltk.tokenize import sent_tokenize, word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Check and download necessary NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('taggers/averaged_perceptron_tagger')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('wordnet')


def get_wordnet_pos(treebank_tag: str) -> str:
    """Convert Treebank POS tags to WordNet POS tags."""
    pos_map = {'J': wordnet.ADJ, 'V': wordnet.VERB, 'N': wordnet.NOUN, 'R': wordnet.ADV}
    return pos_map.get(treebank_tag[0], wordnet.NOUN)


def read_file(file_path: str) -> str:
    """Read content from either .docx or .txt file."""
    try:
        if file_path.lower().endswith('.docx'):
            doc = Document(file_path)
            return ' '.join(paragraph.text for paragraph in doc.paragraphs)
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        else:
            raise ValueError("Unsupported file format. Use .docx or .txt.")
    except Exception as e:
        raise IOError(f"Error reading file: {e}")


def check_synonym_use(text: str) -> float:
    """Check for unusual use of synonyms indicating potential manipulation."""
    sentences = sent_tokenize(text)
    unusual_synonym_count = 0
    total_words = 0

    for sentence in sentences:
        words = word_tokenize(sentence)
        for word, tag in pos_tag(words):
            if word.isalnum():
                wn_pos = get_wordnet_pos(tag)
                synonyms = {lemma.name() for syn in wordnet.synsets(word, pos=wn_pos) for lemma in syn.lemmas()}
                if len(synonyms) > 1 and any(syn != word and syn in words for syn in synonyms):
                    unusual_synonym_count += 1
                total_words += 1

    return unusual_synonym_count / total_words if total_words > 0 else 0.0


def check_sentence_structure(text: str) -> float:
    """Analyze sentence structure for signs of manipulation."""
    sentences = sent_tokenize(text)
    if not sentences:
        return 0.0

    def calculate_structure_score(sentence: str) -> float:
        score = 0
        if ';' in sentence or len(sentence) > 50:
            score += 1
        if sentence.count(',') > 1:  # Updated check to avoid invalid periods detection
            score += 1
        if any(tag.startswith('IN') for _, tag in pos_tag(word_tokenize(sentence))):
            score += 0.5
        return score

    complexity_scores = [calculate_structure_score(sentence) for sentence in sentences]
    return sum(complexity_scores) / len(sentences)


def check_word_order(text: str) -> float:
    """Check for unusual entropy in word order within sentences."""
    sentences = sent_tokenize(text)
    entropy_scores = []

    for sentence in sentences:
        words = word_tokenize(sentence)
        if len(words) > 3:
            word_freq = Counter(words)
            entropy = -sum(freq / len(words) * math.log2(freq / len(words)) for freq in word_freq.values())
            entropy_scores.append(entropy)

    return (sum(entropy_scores) / len(entropy_scores) - 2.0) if entropy_scores else 0.0


def check_conjunction_use(text: str) -> float:
    """Check for the use of complex conjunctions in the text."""
    complex_conjunctions = [
        'moreover', 'furthermore', 'additionally', 'however', 'nevertheless',
        'on the contrary', 'alternatively', 'or else', 'either'
    ]
    sentences = sent_tokenize(text)
    if not sentences:
        return 0.0

    conjunction_count = sum(
        1 for sentence in sentences if any(conj in word_tokenize(sentence) for conj in complex_conjunctions))
    return conjunction_count / len(sentences)


def tfidf_similarity(original_text: str, manipulated_text: str) -> float:
    """Calculate cosine similarity between original and manipulated text."""
    try:
        vectorizer = TfidfVectorizer().fit_transform([original_text, manipulated_text])
        if vectorizer.shape[0] == 2:  # Confirm 2 texts are passed
            return cosine_similarity(vectorizer.toarray())[0, 1]
        else:
            raise ValueError("TF-IDF vectorizer did not encode exactly 2 documents.")
    except Exception as e:
        raise ValueError(f"Error calculating TF-IDF similarity: {e}")


def detect_manipulation(file_path: str, original_file_path: str = None) -> Tuple[float, str]:
    """Detect potential text manipulation based on various metrics from files."""
    try:
        text = read_file(file_path)
        original_text = read_file(original_file_path) if original_file_path else None

        # Compute individual scores
        synonym_score = check_synonym_use(text)
        structure_score = check_sentence_structure(text)
        order_score = check_word_order(text)
        conjunction_score = check_conjunction_use(text)
        tfidf_score = tfidf_similarity(original_text, text) if original_text else 0.0

        # Weighted total score
        total_score = (
                synonym_score * 0.25 +
                structure_score * 0.20 +
                order_score * 0.20 +
                conjunction_score * 0.15 +
                tfidf_score * 0.20
        )

        result = "Text appears manipulated." if total_score > 0.3 else "Text appears natural."
        return total_score, result
    except (IOError, ValueError) as e:
        raise ValueError(f"Error detecting manipulation: {e}")