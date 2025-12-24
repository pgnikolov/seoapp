import re
import string
from typing import List, Dict, Any, Set
from collections import Counter
import math
from langdetect import detect, DetectorFactory
from nltk.corpus import stopwords
import nltk

# За стабилни резултати при детекция на език
DetectorFactory.seed = 0

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class KeywordAnalyzer:
    def __init__(self, pages: List[Dict[str, Any]], target_lang: str = None):
        self.pages = pages
        self.target_lang = target_lang
        self.stopwords_cache = {}
        
    def get_stopwords(self, lang: str) -> Set[str]:
        if lang in self.stopwords_cache:
            return self.stopwords_cache[lang]
        
        try:
            if lang == 'bg':
                # NLTK няма вградени български стоп думи в стандартния списък понякога,
                # или са под друго име. За всеки случай дефинираме базови.
                stop_words = set(["и", "в", "на", "с", "по", "че", "за", "да", "са", "от", "като", "със", "във", "през", "тук", "тази", "това", "тези", "който", "която", "които", "към", "ще", "не", "но", "а", "ли", "или"])
            else:
                stop_words = set(stopwords.words('english' if lang == 'en' else lang))
        except:
            stop_words = set(stopwords.words('english'))
            
        self.stopwords_cache[lang] = stop_words
        return stop_words

    def clean_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.lower()
        # Махаме пунктуация
        text = text.translate(str.maketrans('', '', string.punctuation))
        # Нормализираме whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def generate_ngrams(self, text: str, n: int) -> List[str]:
        words = text.split()
        if len(words) < n:
            return []
        return [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]

    def get_intent(self, phrase: str) -> str:
        """
        Проста евристика за определяне на намерението (intent).
        """
        commercial_signals = ['цена', 'купи', 'price', 'buy', 'shop', 'магазин', 'порчъка', 'order', 'евтино', 'cheap']
        informational_signals = ['как', 'how', 'защо', 'why', 'какво', 'what', 'ръководство', 'guide', 'съвети', 'tips', 'информация', 'info']
        navigational_signals = ['вход', 'login', 'контакти', 'contacts', 'за нас', 'about', 'support', 'поддръжка']
        
        phrase_lower = phrase.lower()
        if any(s in phrase_lower for s in commercial_signals):
            return "commercial"
        if any(s in phrase_lower for s in informational_signals):
            return "informational"
        if any(s in phrase_lower for s in navigational_signals):
            return "navigational"
        
        return "informational" # Default

    def analyze(self) -> List[Dict[str, Any]]:
        """
        Основна логика за точкуване и извличане.
        """
        all_phrases = {} # phrase -> data
        
        # 1. Първо определяме езика на целия сайт (базирано на началната страница или мнозинството)
        combined_text = " ".join([p.get('title', '') + " " + p.get('body', '')[:500] for p in self.pages])
        detected_lang = self.target_lang or 'en'
        try:
            detected_lang = detect(combined_text)
        except:
            pass
        
        stop_words = self.get_stopwords(detected_lang)
        
        # Тегла за различните зони
        weights = {
            'title': 4.0,
            'h1': 3.0,
            'h2': 2.0,
            'h3': 2.0,
            'meta_description': 1.5,
            'anchor': 2.0,
            'body': 1.0
        }

        # 2. Обработка на всяка страница
        doc_counts = Counter() # На колко страници се появява фразата
        
        for page in self.pages:
            page_phrases = {} # phrase -> score components
            
            # Извличаме текст от различни зони
            zones = {
                'title': [page.get('title', '')],
                'meta_description': [page.get('meta_description', '')],
                'h1': page.get('h1', []),
                'h2': page.get('h2', []),
                'h3': page.get('h3', []),
                'body': [page.get('body', '')],
                'anchor': [l.get('anchor', '') for l in page.get('links', [])]
            }
            
            for zone, texts in zones.items():
                weight = weights[zone]
                for raw_text in texts:
                    clean_txt = self.clean_text(raw_text)
                    if not clean_txt:
                        continue
                        
                    for n in range(1, 5): # 1-4 grams
                        ngrams = self.generate_ngrams(clean_txt, n)
                        for gram in ngrams:
                            # Филтри
                            words = gram.split()
                            # Махаме фрази само от стоп думи
                            if all(w in stop_words for w in words):
                                continue
                            # Махаме само цифри
                            if all(w.isdigit() for w in words):
                                continue
                            # Къси токени
                            if any(len(w) < 2 for w in words) and n == 1:
                                continue
                            
                            if gram not in page_phrases:
                                page_phrases[gram] = {
                                    'score': 0,
                                    'occurrences': 0,
                                    'source_mix': Counter(),
                                    'top_page': page['url']
                                }
                            
                            page_phrases[gram]['score'] += weight
                            page_phrases[gram]['occurrences'] += 1
                            page_phrases[gram]['source_mix'][zone] += 1
            
            # Обновяваме глобалните статистики
            for gram, data in page_phrases.items():
                if gram not in all_phrases:
                    all_phrases[gram] = {
                        'phrase': gram,
                        'total_score': 0,
                        'total_occurrences': 0,
                        'pages_count': 0,
                        'top_page': data['top_page'],
                        'top_page_score': 0,
                        'source_mix': Counter(),
                        'intent': self.get_intent(gram),
                        'language': detected_lang
                    }
                
                all_phrases[gram]['total_score'] += data['score']
                all_phrases[gram]['total_occurrences'] += data['occurrences']
                all_phrases[gram]['pages_count'] += 1
                all_phrases[gram]['source_mix'].update(data['source_mix'])
                
                if data['score'] > all_phrases[gram]['top_page_score']:
                    all_phrases[gram]['top_page_score'] = data['score']
                    all_phrases[gram]['top_page'] = data['top_page']

        # 3. TF-IDF и финално точкуване
        num_docs = len(self.pages)
        final_list = []
        
        for gram, data in all_phrases.items():
            # TF-IDF like boost: log(N / df)
            idf = math.log10(num_docs / data['pages_count']) if num_docs > 0 else 1
            # Бонус за присъствие на повече страници (site-wide relevance)
            site_wide_boost = 1 + (0.1 * data['pages_count'])
            
            # Финална формула (експериментална)
            final_score = data['total_score'] * (1 + idf) * site_wide_boost
            
            # Филтър: премахваме фрази, които се появяват само веднъж и то само в body
            if data['total_occurrences'] == 1 and data['source_mix'].get('body', 0) == 1:
                # Но ги оставяме ако са в Title или H1
                if not (data['source_mix'].get('title', 0) > 0 or data['source_mix'].get('h1', 0) > 0):
                    continue

            data['score'] = final_score
            final_list.append(data)

        # 4. Нормализиране на резултата 0-100
        if not final_list:
            return []
            
        max_s = max(item['score'] for item in final_list)
        for item in final_list:
            item['score'] = round((item['score'] / max_s) * 100, 2)
            item['source_mix'] = dict(item['source_mix'])
            # Премахваме помощните полета
            del item['total_score']
            del item['top_page_score']
            item['occurrences'] = item.pop('total_occurrences')

        # Сортиране по резултат
        final_list.sort(key=lambda x: x['score'], reverse=True)
        
        return final_list
