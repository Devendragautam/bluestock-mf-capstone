import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("sqlite:///data/db/bluestock_mf.db")

with open("sql/queries.sql", "r") as f:
    content = f.read()

queries = [q.strip() for q in content.split(";") if q.strip() and not q.strip().startswith("--")]

# Simple split by comment blocks so each query prints with its label
blocks = content.split("-- ")[1:]  # skip empty first split
for block in blocks:
    label, _, sql = block.partition("\n")
    sql = sql.strip().rstrip(";")
    if not sql:
        continue
    print("=" * 60)
    print(label)
    df = pd.read_sql(sql, engine)
    print(df)
    print()