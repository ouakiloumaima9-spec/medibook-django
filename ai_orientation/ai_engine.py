"""
Moteur IA d'orientation vers une spécialité médicale.
Approche pédagogique et explicable : TF-IDF + similarité cosinus.
Le module propose uniquement une orientation indicative, jamais un diagnostic médical.
"""
import re
import unicodedata
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

FRENCH_STOPWORDS = {
    'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'au', 'aux', 'et', 'ou', 'mais', 'donc', 'or', 'ni', 'car',
    'que', 'qui', 'quoi', 'je', 'tu', 'il', 'elle', 'on', 'nous', 'vous', 'ils', 'elles', 'me', 'te', 'se', 'mon',
    'ma', 'mes', 'ton', 'ta', 'tes', 'son', 'sa', 'ses', 'notre', 'votre', 'leur', 'leurs', 'ce', 'cet', 'cette',
    'ces', 'ca', 'cela', 'est', 'sont', 'ai', 'as', 'avons', 'avez', 'ont', 'suis', 'es', 'sommes', 'etes', 'avoir',
    'etre', 'plus', 'moins', 'tres', 'trop', 'peu', 'beaucoup', 'dans', 'sur', 'sous', 'avec', 'sans', 'pour', 'par',
    'en', 'depuis', 'pendant', 'quand', 'comme', 'aussi', 'meme', 'pas', 'ne', 'non', 'oui', 'si', 'alors', 'jai',
    'cest', 'sest', 'nest', 'mal', 'douleur', 'parfois', 'souvent', 'toujours', 'jamais', 'jour', 'nuit', 'semaine',
    'mois', 'niveau', 'avoir', 'ressens', 'sentir', 'sens', 'probleme'
}

SYNONYMS = {
    'tete': ['cephalee', 'migraine', 'cerveau', 'neurologique'],
    'cephalee': ['tete', 'migraine'],
    'migraine': ['tete', 'cephalee'],
    'vertige': ['etourdissement', 'malaise', 'equilibre'],
    'coeur': ['cardiaque', 'palpitation', 'thoracique', 'poitrine'],
    'poitrine': ['thoracique', 'cardiaque', 'coeur', 'pectoral'],
    'palpitation': ['coeur', 'cardiaque', 'tachycardie'],
    'essoufflement': ['dyspnee', 'souffle', 'respiration'],
    'tension': ['hypertension', 'pression', 'cardiaque'],
    'peau': ['cutane', 'dermatologique', 'epiderme'],
    'bouton': ['acne', 'pustule', 'eruption', 'peau'],
    'tache': ['taches', 'peau', 'cutane', 'dermatologie', 'pigmentation'],
    'taches': ['tache', 'peau', 'cutane', 'dermatologie', 'pigmentation'],
    'cou': ['peau', 'dermatologie', 'zone_cervicale'],
    'eczema': ['allergie', 'rougeur', 'peau', 'demangeaison'],
    'rougeur': ['rouge', 'eruption', 'inflammation', 'peau'],
    'demangeaison': ['prurit', 'gratter', 'peau', 'eczema'],
    'enfant': ['bebe', 'nourrisson', 'pediatrique', 'fils', 'fille'],
    'bebe': ['enfant', 'nourrisson', 'pediatrique'],
    'vaccin': ['vaccination', 'injection', 'pediatrique', 'enfant'],
    'yeux': ['oeil', 'vue', 'oculaire', 'vision', 'ophtalmologique'],
    'oeil': ['yeux', 'oculaire', 'vue'],
    'vue': ['vision', 'yeux', 'oculaire'],
    'dent': ['dentaire', 'dentiste', 'bouche', 'gencive'],
    'dents': ['dent', 'dentaire', 'bouche'],
    'carie': ['dent', 'dentaire'],
    'oreille': ['otite', 'audition', 'orl', 'tympan'],
    'gorge': ['angine', 'pharynx', 'orl', 'amygdale'],
    'nez': ['sinus', 'sinusite', 'rhume', 'orl', 'nasal'],
    'grossesse': ['enceinte', 'gynecologique', 'maternite'],
    'enceinte': ['grossesse', 'gynecologique', 'maternite'],
    'regles': ['menstruation', 'gynecologique', 'cycle'],
    'fievre': ['temperature', 'frissons', 'grippe', 'infection'],
    'fatigue': ['epuisement', 'asthenie', 'lassitude', 'malaise'],
    'rhume': ['nez', 'grippe', 'virus', 'orl'],
    'toux': ['gorge', 'respiratoire', 'rhume'],
    'nausee': ['vomir', 'vomissement', 'estomac', 'gastrique'],
    'diarrhee': ['estomac', 'digestif', 'intestin'],
    'ventre': ['estomac', 'abdomen', 'digestif'],
}


def normalize(text):
    text = text.lower().strip()
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def remove_stopwords(text):
    return ' '.join(word for word in text.split() if word not in FRENCH_STOPWORDS and len(word) > 2)


def expand_with_synonyms(text):
    words = text.split()
    expanded = list(words)
    for word in words:
        expanded.extend(SYNONYMS.get(word, []))
    return ' '.join(expanded)


def preprocess(text):
    return expand_with_synonyms(remove_stopwords(normalize(text)))


class SpecialtyOrientationEngine:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.vectorizer = TfidfVectorizer(lowercase=False, ngram_range=(1, 2), min_df=1, sublinear_tf=True)
        self.specialties = []
        self.matrix = None
        self._trained = False
        self._initialized = True

    def train(self, force=False):
        if self._trained and not force:
            return
        from doctors.models import Specialty
        self.specialties = list(Specialty.objects.filter(is_active=True).exclude(keywords=''))
        if not self.specialties:
            self.matrix = None
            self._trained = True
            return
        corpus = [preprocess(f'{s.name} {s.description} {s.keywords}') for s in self.specialties]
        self.matrix = self.vectorizer.fit_transform(corpus)
        self._trained = True

    def predict(self, motif_text, top_k=3):
        self.train()
        if not self.specialties or self.matrix is None:
            return []
        processed = preprocess(motif_text)
        if not processed:
            return []
        query_vec = self.vectorizer.transform([processed])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = np.argsort(scores)[::-1][:top_k]
        results = []
        for idx in top_indices:
            if scores[idx] >= 0.03:
                results.append({'specialty': self.specialties[idx], 'score': round(float(scores[idx]) * 100, 2)})
        return results


engine = SpecialtyOrientationEngine()
