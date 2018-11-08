import pymorphy2
import re
import json
import pandas as pd
from pyquery import PyQuery
from sqlalchemy import create_engine
from nltk.stem.porter import PorterStemmer


def normalize_saying_list(saying_list):
    return [morph.parse(word)[0].normalized[0] for word in saying_list]


def stem_saying_list(saying_list):
    return [porter.stem(word.lower()) for word in saying_list]


with open('config.json') as f:
    CONFIG = json.load(f)


# get russian sayings and write them to database
engine = create_engine(CONFIG['database_url'], isolation_level="AUTOCOMMIT")
morph = pymorphy2.MorphAnalyzer()

html = 'https://ru.wikiquote.org/wiki/%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B5_%D0%BF%D0%BE%D1%81%D0%BB%D0%BE%D0%B2%D0%B8%D1%86%D1%8B'
pq = PyQuery(html)
tag = pq('div#mw-content-text')
sayings_text = tag.text().split('\n')[4:-6]
sayings_text = [x.replace('\xa0', ' ') for x in sayings_text]
saying_lists = [re.sub(r'[^\w\s]', '', x).split(' ') for x in sayings_text]
saying_lists = list(map(normalize_saying_list, saying_lists))

sayings = pd.DataFrame({'text': sayings_text, 'words': saying_lists, 'language': 'RU'})
sayings.to_sql("sayings", con=engine, if_exists='append', index=False)
engine.dispose()

# get english sayings and write them to database
engine = create_engine(CONFIG['database_url'], isolation_level="AUTOCOMMIT")
porter = PorterStemmer()

html = 'https://en.wikiquote.org/wiki/English_proverbs_(alphabetically_by_proverb)'
pq = PyQuery(html)
tag = pq('div#mw-content-text')
sayings_text = tag.text().split('\n')

stop_words = ['\"', '\'', 'trasnlation', 'meaning', 'proverb', 'note', 'variant',
              'version', 'alternatively', 'variation']
sayings_text = [x for x in sayings_text if not any(char.isdigit() for char in x)]
sayings_text = [x for x in sayings_text if not any(word in x.lower() for word in stop_words)]
sayings_text = sayings_text[3:-2]
saying_lists = [re.sub(r'[^\w\s]', '', x).split(' ') for x in sayings_text]
saying_lists = list(map(stem_saying_list, saying_lists))

# write to database
sayings = pd.DataFrame({'text': sayings_text, 'words': saying_lists, 'language': 'EN'})
sayings.to_sql("sayings", con=engine, if_exists='append', index=False)
engine.dispose()
