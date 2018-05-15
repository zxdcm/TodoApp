from peewee import IntegerField


class EnumField(IntegerField):
    '''
    Enum like field support for Peewee ORM
    Probably temp solution
    https://github.com/coleifer/peewee/issues/630
    '''
    def init(self, choices, *args, **kwargs):
        self.to_db = {v:k for k, v in choices}
        self.from_db = {k:v for k, v in choices}
        super(IntegerField, self).init(*args, **kwargs)

    def db_value(self, value):
        return self.to_db[value]

    def python_value(self, value):
        return self.from_db[value]


STATUS = [(0, 'Is not done yet'),
           (1, 'done'),
           (2, 'canceled'),
           (3, 'removed'),
           (4, 'assigned'),]