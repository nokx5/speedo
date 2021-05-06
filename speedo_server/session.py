import os

from sqlalchemy import create_engine
from sqlalchemy.engine.url import URL


from .database import tables


IS_POSTGRESQL = "PGHOST" in os.environ

if "DEBUG_SPEEDO_SQL" in os.environ:
    import logging

    logging.basicConfig()
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

if IS_POSTGRESQL:  # PGHOST set, use postgresql
    print("Postgresql database selected!")
    engine = create_engine(
        URL(
            "postgresql",
            username=os.environ["PGUSER"],
            password=os.environ["PGPASS"],
            host=os.environ["PGHOST"],
            port=os.environ.get("PGPORT", None),  # if not specified use default
            database=os.environ["PGDATABASE"],
        )
    )
else:
    print("In-memory sqlite database selected!")
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool,
    )
    engine.execute("pragma foreign_keys=on")

if os.getenv("SPEEDO_ALEMBIC", "") == "":
    tables.metadata.create_all(bind=engine)
