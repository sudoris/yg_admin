# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from app_config.config_env import env
from app_config.config import database_url


# 是否印出 sql script 設定
sql_echo = True
echo_pool = True
if env == 'app':
    sql_echo = False
    echo_pool = False
# -------------------------

# https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
"""
SQLAlchemy Engine 參數
http://docs.sqlalchemy.org/en/latest/core/engines.html

Connect Pool
https://sanyuesha.com/2019/01/02/sqlalchemy-pool-mechanism/
"""
engine = create_engine(database_url, pool_recycle=1800, pool_size=30, max_overflow=10, echo=sql_echo, echo_pool=echo_pool, pool_pre_ping=True)


Base = declarative_base()


def row_to_dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d


def get_db_session():
    db_session = scoped_session(sessionmaker(autocommit=False,
                                             autoflush=False,
                                             bind=engine))
    return db_session

