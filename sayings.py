import pymorphy2
import re
import json
import pandas as pd
from pyquery import PyQuery
from sqlalchemy import create_engine


def normalize_saying_list(saying_list):
    return [morph.parse(x)[0].normalized[0] for x in saying_list]


with open('config.json') as f:
    CONFIG = json.load(f)

engine = create_engine(CONFIG['database_url'], isolation_level="AUTOCOMMIT")

# get russian sayings and write them to database
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
