import os
from sqlalchemy import create_engine, text

engine = create_engine(os.getenv("DATABASE_URL"))
with engine.connect() as conn:
    for table in ("predictions", "diagnostics_confirmes"):
        try:
            n = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"{table} : {n} lignes")
        except Exception as e:
            print(f"{table} : absente ({e})")