
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Update this path if your CSV is in a different folder.
PROJECT_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = PROJECT_DIR / "Data" / "student_success_cleaned.csv"

# Use the same credentials as your successful connection test.
DB_USERNAME = "postgres.qhazarymxnodpzgofetk"
DB_PASSWORD = "Prashant#@@#21"
DB_HOST = "aws-0-ap-northeast-1.pooler.supabase.com"

url = URL.create(
    "postgresql+psycopg2",
    username=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=5432,
    database="postgres",
)

engine = create_engine(
    url,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
)

try:
    df = pd.read_csv(CSV_PATH)

    print("CSV file:", CSV_PATH)
    print("CSV rows:", len(df))
    print("CSV columns:")
    print(df.columns.tolist())
    print("\nFirst 3 rows:")
    print(df.head(3).to_string(index=False))

    with engine.connect() as conn:
        for table in (
            "students",
            "student_performance",
            "risk_predictions",
            "interventions",
        ):
            count = conn.execute(
                text(f'SELECT COUNT(*) FROM public."{table}"')
            ).scalar_one()
            print(f"{table}: {count} rows")

except Exception as error:
    print("Inspection failed:")
    print(error)

finally:
    engine.dispose()
