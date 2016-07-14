from contextlib import contextmanager
import sqlite3


@contextmanager
def connect_hold(database_conn):
    """
    a context to hold the connection of database, like 'with connect_hold(**) as c'
    """
    c = database_conn.cursor()
    try:
        yield c
    finally:
        c.close()
        database_conn.commit()
        database_conn.close()


def get_database_connection(database_name, database_type):
    """Return connection from sqlite database"""
    if database_type != "sqlite":
        raise NotImplementedError("Only sqlite database is supported for now")
    return sqlite3.connect(database_name)