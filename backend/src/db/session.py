import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from ..core.config import settings

Base = declarative_base()

_connector = None


def _get_connector():
    global _connector
    if _connector is None:
        from google.cloud.sql.connector import Connector

        _connector = Connector()
    return _connector


def _build_engine():
    if settings.USE_CLOUD_SQL_CONNECTOR and settings.CLOUD_SQL_CONNECTION_NAME:
        return _build_connector_engine()
    return _build_direct_engine()


def _build_connector_engine():
    connector = _get_connector()

    def getconn():
        return connector.connect(
            settings.CLOUD_SQL_CONNECTION_NAME,
            "pymysql",
            user=settings.MYSQL_USER,
            db=settings.MYSQL_DB,
            enable_iam_auth=True,
        )

    return create_engine(
        "mysql+pymysql://",
        creator=getconn,
        pool_size=3,
        max_overflow=5,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_timeout=30,
    )


def _build_direct_engine():
    import urllib.parse

    connect_args = {}
    ssl_config = {}

    def is_valid_file(path):
        return path and os.path.isfile(path) and os.path.getsize(path) > 10

    if settings.MYSQL_SSL_CA and is_valid_file(settings.MYSQL_SSL_CA):
        ssl_config["ca"] = settings.MYSQL_SSL_CA
    if settings.MYSQL_SSL_CERT and is_valid_file(settings.MYSQL_SSL_CERT):
        ssl_config["cert"] = settings.MYSQL_SSL_CERT
    if settings.MYSQL_SSL_KEY and is_valid_file(settings.MYSQL_SSL_KEY):
        ssl_config["key"] = settings.MYSQL_SSL_KEY

    if ssl_config:
        ssl_config["check_hostname"] = False
        connect_args["ssl"] = ssl_config

    password = urllib.parse.quote_plus(settings.MYSQL_PASSWORD) if settings.MYSQL_PASSWORD else ""
    url = f"mysql+pymysql://{settings.MYSQL_USER}:{password}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"
    if settings.MYSQL_QUERY:
        url += f"?{settings.MYSQL_QUERY}"

    return create_engine(
        url,
        connect_args=connect_args,
        pool_size=3,
        max_overflow=5,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_timeout=30,
    )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


from contextlib import contextmanager

@contextmanager
def get_db_context():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
