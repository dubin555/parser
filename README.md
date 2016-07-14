
## A simple ORM to parser the CTL model

### From a CTL model to select the scan chain from sqlite

#### TODO List

- [x] Create, insert, query into sqlite database
- [x] Trace the raw sql statement
- [x] Support included from ctl file or manually from shell or script
- [ ] Mysql not support yet
- [ ] Migrate database between sqlite and mysql

#### Change history

> * Add database type convert factory mode for sql insert, create

```python
    def _create_adapter(self, statement, table_type):
        """ Factory to create raw sql create table statement base on the database type"""
        if table_type == "sqlite":
            raw_create_sql = "CREATE TABLE %s (%s)" % (self.__table__, ",".join(statement))
        elif table_type == "mysql":
            # TODO
            raise NotImplementedError("Mysql database still not be supported")
        else:
            raise NotImplementedError("Other database still not be supported")
        return raw_create_sql

    def __init__(self):
        """
        Need to implement the Base class __init__ function.
        """
        super(self.__class__, self).__init__()
        # Adapter to the table type implemented in the class. Default is sqlite
        self._create_adapter = partial(self._create_adapter, table_type=self.__table_type__)
        self._insert_adapter = partial(self._insert_adapter, table_type=self.__table_type__)
```

> * Add context manager help function for connection of database 

```python
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


    @classmethod
    def raw_sql(cls, sql_string):
        """
        execute the raw sql statement in sql_string
        """
        with connect_hold(get_database_connection(cls.__table__+".db", "sqlite")) as c:
            c.execute(sql_string)
            return c.fetchall()
```

