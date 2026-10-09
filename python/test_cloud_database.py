from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres.qhazarymxnodpzgofetk",
    password="Prashant#@@#21",
    host="aws-0-ap-northeast-1.pooler.supabase.com",
    port=5432,
    database="postgres"
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    connect_args={"sslmode": "require"}
)


try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT version();")
        )

        print("Cloud PostgreSQL connection successful!")
        print(result.fetchone())

except Exception as e:
    print("Cloud PostgreSQL connection failed.")
    print(e)