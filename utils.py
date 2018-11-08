import pandas as pd
from sqlalchemy import create_engine


def get_saying(word, database_url):
    engine = create_engine(database_url, isolation_level="AUTOCOMMIT")
    sql = """
      SELECT * FROM sayings
      WHERE words @> ARRAY['%s']::text[] ORDER BY random() LIMIT 1;
    """ % word
    result = pd.read_sql_query(sql, con=engine)
    engine.dispose()
    if len(result) > 0:
        return result.text.iloc[0]
    else:
        return "Sorry, there is no a such word in the database."
