from langchain_community.utilities import SQLDatabase
from decouple import config

DB_URL=config("DB_URL")
db = SQLDatabase.from_uri(DB_URL)
print(db.dialect)
print(db.get_usable_table_names())