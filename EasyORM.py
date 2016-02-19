class Field(object):

    def __init__(self,value,column_type,primary_key,default):
        self.value = value
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s,%s:%s>' %(self.__class__.__name__, self.column_type, self.value)


class TextField(Field):

    def __init__(self, value = None, primary_key = False, default = None, data_type = 'text'):
        super().__init__(value,data_type,primary_key,default)


class RealField(Field):

    def __init__(self, value = None, primary_key = False, default = None, data_type = 'real'):
        super().__init__(value,data_type,primary_key,default)


def insert_format(l):
    res = []
    for s in l:
        if isinstance(s,str):
            res.append("'"+s+"'")
        else:
            res.append(str(s))
    return ",".join(res)

class CtlModelMetaclass(type):

    def __new__(cls,name,bases,attrs):
        if name == "Model":
            return type.__new__(cls,name,bases,attrs)
        table_name = attrs.get('__table__',None) or name
        mappings = {}
        fields = []
        primary_key = None
        for k,v  in attrs.items():
            if isinstance(v, Field):
                print("found mapping %s --> %s" %(k, v))
                mappings[k] = v
                if v.primary_key:
                    primary_key = k
                else:
                    fields.append(k)
#        if not primary_key:
#            raise StandardError("no primary_key found")
        attrs['__mappings__'] = mappings
        attrs['__table__'] = table_name
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        attrs['__create_implement__'] = False
        attrs['__insert__'] = None
        return type.__new__(cls,name,bases,attrs)


class Model(dict, metaclass=CtlModelMetaclass):

    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError("object has not attribute -> %s" %key)

    def __setattr__(self,key,value):
        self[key] = value


    def create(self):
        temp = [ self.__primary_key__ + " " + self.__mappings__[self.__primary_key__].column_type+ " " + "primary key" ] +\
                        [field + " " + self.__mappings__[field].column_type for field in self.__fields__]
        raw_create_sql = "CREATE TABLE %s (%s)" %(self.__table__, ",".join(temp))
        self.__class__.__create_implement__ = True
        #print(raw_create_sql)
        return raw_create_sql



    def insert(self):
        values = [self.get(field,None) for field in self.__fields__]
        values.insert(0, self.get(self.__primary_key__))
        insert_sql = insert_format(values)
        raw_insert_sql = "INSERT INTO %s VALUES (%s)" %(self.__table__, insert_sql)
        if not self.__class__.__create_implement__:
            return [self.create()] + [raw_insert_sql]
        #print(raw_insert_sql)
        return [raw_insert_sql]


class CtlModel(Model):
    __table__ = "test"

    name                =   TextField(primary_key = True)
    libcell             =   TextField()
    skew_latch          =   RealField()
    tail_edge_rise      =   RealField()
    test_mode_port      =   TextField()
    rise                =   RealField()
    length              =   RealField()
    test_mode_active    =   TextField()
    clock_port          =   TextField()
    fall                =   RealField()
    active              =   TextField()
    shift_enable_port   =   TextField()
    tail_clock_port     =   TextField()
    sdi                 =   TextField()
    sdo                 =   TextField()
    skew_safe           =   RealField()




