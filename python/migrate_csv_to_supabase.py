
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# --------------------------------------------------
# 1. Database connection
# Copy the actual values from your working
# test_cloud_database.py file.
# --------------------------------------------------

DB_USERNAME = "postgres.qhazarymxnodpzgofetk"
DB_PASSWORD = "Prashant#@@#21"
DB_HOST = "aws-0-ap-northeast-1.pooler.supabase.com"

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USERNAME,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=5432,
    database="postgres",
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"},
)


# --------------------------------------------------
# 2. Locate and read the cleaned CSV
# --------------------------------------------------

project_dir = Path(__file__).resolve().parent.parent
csv_path = project_dir / "Data" / "student_success_cleaned.csv"

if not csv_path.exists():
    raise FileNotFoundError(f"CSV not found: {csv_path}")

df = pd.read_csv(csv_path)

print(f"CSV rows found: {len(df)}")

# Required columns
required_columns = [
    "student_id",
    "name",
    "gender",
    "course",
    "semester",
    "attendance",
    "internal_marks",
    "assignment_completion",
    "previous_gpa",
    "failed_subjects",
    "study_hours",
    "previous_semester_marks",
    "practical_marks",
    "class_participation",
    "risk_level",
]

missing_columns = set(required_columns) - set(df.columns)

if missing_columns:
    raise ValueError(f"Missing CSV columns: {sorted(missing_columns)}")

if df["student_id"].isna().any():
    raise ValueError("CSV contains missing student IDs.")

if df["student_id"].duplicated().any():
    raise ValueError("CSV contains duplicate student IDs.")

# --------------------------------------------------
# 3. Split the CSV into the two database tables
# --------------------------------------------------

student_columns = [
    "student_id",
    "name",
    "gender",
    "course",
    "semester",
]

performance_columns = [
    "student_id",
    "attendance",
    "internal_marks",
    "assignment_completion",
    "previous_gpa",
    "failed_subjects",
    "study_hours",
    "previous_semester_marks",
    "practical_marks",
    "class_participation",
]

students_df = df[student_columns].copy()
performance_df = df[performance_columns].copy()

# --------------------------------------------------
# 4. Import safely in one transaction
# Stop if either destination table already has data.
# This prevents accidental duplicate imports.
# --------------------------------------------------

try:
    with engine.begin() as conn:

        students_count = conn.execute(
            text("SELECT COUNT(*) FROM public.students")
        ).scalar_one()

        performance_count = conn.execute(
            text("SELECT COUNT(*) FROM public.student_performance")
        ).scalar_one()

        if students_count != 0 or performance_count != 0:
            raise RuntimeError(
                "Import cancelled: students or student_performance "
                "already contains data. No rows were imported."
            )

        students_df.to_sql(
            name="students",
            con=conn,
            schema="public",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )

        print("Student records inserted.")

        performance_df.to_sql(
            name="student_performance",
            con=conn,
            schema="public",
            if_exists="append",
            index=False,
            method="multi",
            chunksize=500,
        )

        print("Performance records inserted.")

    # The transaction commits only after both inserts succeed.
    print("Database transaction committed successfully.")

    # --------------------------------------------------
    # 5. Verify the final counts
    # --------------------------------------------------

    with engine.connect() as conn:
        for table in (
            "students",
            "student_performance",
            "risk_predictions",
            "interventions",
        ):
            count = conn.execute(
                text(f"SELECT COUNT(*) FROM public.{table}")
            ).scalar_one()

            print(f"{table}: {count} rows")

    print("Migration completed successfully!")

except Exception as error:
    print("Migration failed; database transaction was rolled back.")
    print(f"Reason: {error}")
    raise

finally:
    engine.dispose()
