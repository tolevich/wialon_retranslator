from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

import config

Base = declarative_base()

# создаем объект engine для подключения к БД
engine = create_engine(config.POSTGRESQL_CONNECTION_STRING)
Session = sessionmaker(autocommit=False, bind=engine)


@contextmanager
def session_scope():
    """Контекстный менеджер для управления сессией базы данных."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        if session is not None:
            session.rollback()
    finally:
        if session is not None:
            session.close()
