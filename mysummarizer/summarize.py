import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import numpy as np
from collections import defaultdict
import math

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
def ensure_nltk_data():
    required = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'wordnet']
    for package in required:
        try:
            nltk.data.find(f'corpora/{package}' if package in ['stopwords', 'wordnet'] else f'taggers/{package}')
        except LookupError:
            nltk.download(package)

ensure_nltk_data() 

class AdvancedTextRankSummarizer:
    def __init__(self, language='english'):
        self.language = language
        self.stop_words = set(stopwords.words(language))
        self.lemmatizer = WordNetLemmatizer()

    def preprocess_text(self, text):
        sentences = sent_tokenize(text)
        cleaned_sentences = []
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            pos_tags = nltk.pos_tag(words)
            words = [self.lemmatizer.lemmatize(word) for word, pos in pos_tags
                     if word.isalnum() and word not in self.stop_words and pos in {'NN', 'JJ', 'NNP'}]
            cleaned_sentences.append(words)
            print("Cleaned sentenses:",cleaned_sentences)
        return sentences, cleaned_sentences

    def calculate_tf(self, sentence):
        tf_dict = {}
        if not sentence:
            return tf_dict
        for word in sentence:
            tf_dict[word] = tf_dict.get(word, 0) + 1
        for word, count in tf_dict.items():
            tf_dict[word] = count / len(sentence)
        return tf_dict

    def findsentlen(self, sentence):
        sentences = sent_tokenize(sentence)
        if len(sentences) < 3:
            # Fallback: estimate sentence count based on word count (roughly 15 words per sentence)
            estimated_sentences = max(1, len(sentence.split()) // 15)
            return estimated_sentences
        return len(sentences)

    def calculate_idf(self, cleaned_sentences):
        idf_dict = {}
        num_docs = len(cleaned_sentences)
        for sentence in cleaned_sentences:
            for word in set(sentence):
                idf_dict[word] = idf_dict.get(word, 0) + 1
        for word, count in idf_dict.items():
            idf_dict[word] = math.log(num_docs / count) if count else 0
        return idf_dict

    def calculate_tfidf(self, sentence, idf_dict):
        tf_dict = self.calculate_tf(sentence)
        tfidf_dict = {word: tf * idf_dict.get(word, 0) for word, tf in tf_dict.items()}
        print("TF-IDF for sentence:",sentence,tfidf_dict)
        return tfidf_dict

    def calculate_similarity(self, sent1, sent2, idf_dict):
        tfidf1 = self.calculate_tfidf(sent1, idf_dict)
        tfidf2 = self.calculate_tfidf(sent2, idf_dict)

        all_words = set(tfidf1.keys()).union(set(tfidf2.keys()))
        vec1 = np.array([tfidf1.get(word, 0) for word in all_words])
        vec2 = np.array([tfidf2.get(word, 0) for word in all_words])

        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0
        return np.dot(vec1, vec2) / (norm1 * norm2)

    def build_similarity_matrix(self, cleaned_sentences):
        n = len(cleaned_sentences)
        similarity_matrix = np.zeros((n, n))
        idf_dict = self.calculate_idf(cleaned_sentences)
        for i in range(n):
            for j in range(i + 1, n):
                similarity = self.calculate_similarity(cleaned_sentences[i], cleaned_sentences[j], idf_dict)
                similarity_matrix[i][j] = similarity
                similarity_matrix[j][i] = similarity
                print("similarity matrix:\n",similarity_matrix)
        return similarity_matrix

    def textrank(self, similarity_matrix, eps=1e-8, max_iter=100, damping_factor=0.85):
        n = len(similarity_matrix)
        p = np.ones(n) / n
        for _ in range(max_iter):
            prev_p = p.copy()
            for i in range(n):
                summation = np.sum(similarity_matrix[i] * prev_p / (np.sum(similarity_matrix, axis=1) + eps))
                p[i] = (1 - damping_factor) / n + damping_factor * summation
            if np.sum(np.abs(p - prev_p)) < eps:
                break
            print("textRank score:",p)
        return p

    def extract_top_sentences(self, sentences, scores, num_sentences):
        ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
        return [s for _, s in ranked_sentences[:num_sentences]]

    def keyword_extraction(self, cleaned_sentences, scores, num_keywords=5):
        word_scores = defaultdict(float)
        for i, sentence in enumerate(cleaned_sentences):
            for word in sentence:
                word_scores[word] += scores[i]
        return sorted(word_scores.items(), key=lambda x: x[1], reverse=True)[:num_keywords]

    def generate_title(self, top_sentence, keywords, max_length=7):
        words = word_tokenize(top_sentence.lower())
        important_words = [self.lemmatizer.lemmatize(word) for word in words
                           if word not in self.stop_words and word.isalnum()]
        title_words = important_words + [word for word, _ in keywords if word not in important_words]
        title_words = sorted(set(title_words), key=lambda x: words.index(x) if x in words else len(words))
        title = ' '.join(title_words[:max_length])
        title = title.title()
        print("Generated Title:",title)
        return title

    def summarize(self, text, num_sentences, num_keywords=5):
        if not text.strip():
            return "", "", []
        original_sentences, cleaned_sentences = self.preprocess_text(text)
        if not cleaned_sentences:
            return "", "", []
        similarity_matrix = self.build_similarity_matrix(cleaned_sentences)
        scores = self.textrank(similarity_matrix)
        summary = self.extract_top_sentences(original_sentences, scores, num_sentences)
        keywords = self.keyword_extraction(cleaned_sentences, scores, num_keywords)
        top_sentence = summary[0] if summary else ""
        title = self.generate_title(top_sentence, keywords)
        return title, ' '.join(summary), [word for word, _ in keywords]
