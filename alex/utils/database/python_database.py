import codecs
import os
import random

class PythonDatabase(object):
    '''In this project, this database class is also working as a ways of finding out the good interface, prototype of database for SDS apps'''
    '''Python database helper - every data is saved in Python data structure, which can also load table from text file
        Properties:
            - self.tables: list of dict representation for a table, each dict has four keys: 
                - file=full path to the text file, 
                - name=name of table automatically set equal as filename but with out extension (e.g. city for city.csv)
                - fields= list of fields of the table
                rows which is a list of tuple, each tuple reprsent a recod.

        - standard text database file is a TSV file with:
                table name as filename
                fields in the first line 
                recoreds in the following line
    '''
    def __init__(self, cfg, *args, **kwargs):
        '''Open connection to database'''
        self._config = cfg.config['database']
        self._name = self.__class__.__name__
        #above can be moved to abstract class
        files = self._config[self._name]['files']
        self._tables = {}
        self.read_table_from_file(files)

    def get_table_names(self):
        '''Returns list of table names'''
        return self._table.keys()

    def get_field_list(self, table):
        '''Returns field list of given table'''
        return self._tables[table]['fields']
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
    def get_field_values(self, table, field):
        '''Return set of distinct values in given table and field'''
        pass
    def row_iterator(self, table):
        '''Return iterator over all rows in given table'''
        pass
    def get_random_element(self, lst):
        '''Return an random element from given list'''
        return lst[random.randint(0, len(lst))]
    def read_table_from_file(self, files):
        '''Read each text file in standard format and save them in dict(fileName, fields, list of tupe which  each tuple is a record in the table)'''
        if isinstance(files, str):#load only one file, can be used when complement a table to current database
            files = [files]
        for fin in files:
            d = {'file': fin}
            name  = os.path.split(fin)[1]
            name = name[0:name.rfind('.')]
            with codecs.open(fin, 'r', encoding='utf-8') as f:
                line = f.readline()
                d['fields'] = line.split()
                d['rows'] = []
                for line in f.readlines():
                    #TODO all of empty values in each row will bi ignored, raise bugs or incorrect
                    row = line.strip().split('\t')
                    row = tuple(row)
                    d['rows'].append(row)
            self._tables[name] = d
       
    
    #-------------definetion for specific apps
#----------for testing---------------
if __name__ == '__main__':
    import autopath
import pdb
from alex.utils.config import Config

cfg = None

def get_config():
    global cfg
    #pdb.set_trace()
    cfg = Config.load_configs(['../../applications/PublicTransportInfoEN/ptien.cfg'])#, '../applications/PublicTransportInfoEN/ptien_hdc_slu.cfg'])
    cfg['Logging']['system_logger'].info("Voip Hub\n" + "=" * 120)

def test1():
    db = PythonDatabase(cfg)
    #print 'hello'

def main():
    test1()

if __name__ == '__main__':
    get_config()
    main()
