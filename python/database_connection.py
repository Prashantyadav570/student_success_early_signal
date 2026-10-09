import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


@st.cache_resource
def get_engine():

    db = st.secrets["database"]

    connection_url = URL.create(
        drivername="postgresql+psycopg2",
        username=db["username"],
        password=db["password"],
        host=db["host"],
        port=int(db["port"]),
        database=db["database"]
    )

    engine = create_engine(
        connection_url,
        pool_pre_ping=True,
        connect_args={"sslmode": "require"}
    )

    return engine


if __name__ == "__main__":
    try:
        engine = get_engine()

        with engine.connect() as connection:
            result = connection.execute(text("SELECT version();"))
            print("Database connection successful!")
            print(result.fetchone())

    except Exception as e:
        print("Database connection failed!")
        print(type(e).__name__)
        print(e)