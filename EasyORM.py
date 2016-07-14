# coding=utf-8
from functools import partial
from util.Database_helper import connect_hold, get_database_connection
import sqlite3


class Field(object):
    """
    A class to specified a field of the database
    """
    def __init__(self, value, column_type, primary_key, default):
        self.value = value
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s,%s:%s>' % (self.__class__.__name__, self.column_type, self.value)


class TextField(Field):
    def __init__(self, value=None, primary_key=False, default=None, data_type='text'):
        super().__init__(value, data_type, primary_key, default)


class RealField(Field):
    def __init__(self, value=None, primary_key=False, default=None, data_type='real'):
        super().__init__(value, data_type, primary_key, default)


class CtlModelMetaclass(type):
    """
    Metaclass to get the information ORM needed, table name, database type, fields...
    """
    def __new__(cls, name, bases, attrs):
        if name == "Model":
            return type.__new__(cls, name, bases, attrs)
        table_name = attrs.get('__table__', None) or name
        table_type = attrs.get('__table_type', None) or "sqlite"
        mappings = {}
        fields = []
        primary_key = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                print ("found mapping %s --> %s" % (k, v))
                mappings[k] = v
                if v.primary_key:
                    primary_key = k
                else:
                    fields.append(k)
        # Information in object Attributes
        attrs['__mappings__'] = mappings
        attrs['__table__'] = table_name
        attrs['__table_type__'] = table_type
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        attrs['__create_implement__'] = False
        attrs['__insert__'] = None
        attrs['__db_connection'] = None
        attrs['__db_cursor__'] = None
        attrs['__setup__'] = False
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=CtlModelMetaclass):
    """
    A model class to implement some sql helper function(_create, _insert, save)
    For now, only sqlite is supported.
    If you want to add some more, Please modify the _*_adapter function.

    """
    def __getattr__(self, key):
        """
        Base class "dict", like proxy pattern to route the request.
        """
        try:
            return self[key]
        except KeyError:
            raise AttributeError("object has not attribute -> %s" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def __init__(self):
        """
        Need to implement the Base class __init__ function.
        """
        super(self.__class__, self).__init__()
        # Adapter to the table type implemented in the class. Default is sqlite
        self._create_adapter = partial(self._create_adapter, table_type=self.__table_type__)
        self._insert_adapter = partial(self._insert_adapter, table_type=self.__table_type__)
        if self.__table_type__ == "sqlite":
            self.__class__.conn = sqlite3.connect(self.__table__ + ".db")

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

    def _insert_adapter(self, statement, table_type):
        """ Factory to create raw sql insert table statement base on the database type"""
        if table_type == "sqlite":

            # define a helper function
            def insert_format(l):
                res = []
                for s in l:
                    if isinstance(s, str):
                        res.append("'" + s + "'")
                    else:
                        res.append(str(s))
                return ",".join(res)

            insert_sql = insert_format(statement)
            raw_insert_sql = "INSERT INTO %s VALUES (%s)" % (self.__table__, insert_sql)
        elif table_type == "mysql":
            # TODO
            raise NotImplementedError("Mysql database still not be supported")
        else:
            raise NotImplementedError("Only sqlite database is supported!")
        return raw_insert_sql

    def _create(self):
        """ return raw sql create statement"""
        temp = [self.__primary_key__ + " " + self.__mappings__[
            self.__primary_key__].column_type + " " + "primary key"] + \
               [field + " " + self.__mappings__[field].column_type for field in self.__fields__]
        raw_create_sql = self._create_adapter(temp)
        self.__class__.__create_implement__ = True
        return raw_create_sql

    def _insert(self):
        """ return raw sql insert statement"""
        if self.__setup__ is False:
            self.setup()
            self.__setup__ = True
        values = [self.get(field, None) for field in self.__fields__]
        values.insert(0, self.get(self.__primary_key__))
        raw_insert_sql = self._insert_adapter(values)
        if not self.__class__.__create_implement__:
            # the table is not created yet
            return [self._create()] + [raw_insert_sql]
        return [raw_insert_sql]

    def save(self):
        """
        save the raw sql to the database
        """
        with connect_hold(get_database_connection(self.__table__+".db", "sqlite")) as c:
            for exec_sql in self._insert():
                c.execute(exec_sql)

    @classmethod
    def query(cls, query_string):
        raw_sql = "select * from {table_name} where {query}".format(table_name=cls.__table__, query=query_string)
        with connect_hold(get_database_connection(cls.__table__+".db", "sqlite")) as c:
            c.execute(raw_sql)
            return c.fetchall()

    @classmethod
    def raw_sql(cls, sql_string):
        """
        execute the raw sql statement in sql_string
        """
        with connect_hold(get_database_connection(cls.__table__+".db", "sqlite")) as c:
            c.execute(sql_string)
            return c.fetchall()


class CtlModel(Model):
    __table__ = "test"
    __table_type__ = "sqlite"

    name = TextField(primary_key=True)
    libcell = TextField()
    skew_latch = RealField()
    tail_edge_rise = RealField()
    test_mode_port = TextField()
    rise = RealField()
    length = RealField()
    test_mode_active = TextField()
    clock_port = TextField()
    fall = RealField()
    active = TextField()
    shift_enable_port = TextField()
    tail_clock_port = TextField()
    sdi = TextField()
    sdo = TextField()
    skew_safe = RealField()
