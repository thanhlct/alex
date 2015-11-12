class SQLiteDatabase(object):
    '''SQLite database helper'''
    def __init__(self, params):
        '''Open connection to database'''
        pass
    def get_table_list(self):
        '''Returns list of table names'''
        pass
    def get_field_list(self, table):
        '''Returns field list of given table'''
        pass
    def execute_non_query(self, query):
        '''Executes an SQL statment which don't return records such as INSERT, DELETE etc.'''
        pass
    def execute_reader(self, query):
        '''Executes an SQL statment which return records such as SELECT'''
        pass
    def get_random_row(self, table):
        '''Returns a random row from given table'''
        pass
    def get_hit_number(sefl, query):
        '''Return number of hit in database for the given query'''
        pass
    def get_field_size(self, table, field):
        '''Return number of distinct values in given table and field'''
        pass
    def row_iterator(self, table):
        '''Return iterator over all rows in given table'''
        pass
    @classmethod
    def create_databse(cls, dbfile, source_files):
        '''Create database file from tables save in text source files'''
        pass
