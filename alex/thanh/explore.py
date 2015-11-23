import pdb
import codecs

if __name__ == '__main__':
    import autopath

from alex.utils.config import Config
from alex.components.slu.base import CategoryLabelDatabase, SLUInterface
from alex.components.slu.common import slu_factory
from alex.applications.PublicTransportInfoEN.data.ontology import ontology

from alex.utils.sample_distribution import sample_from_list

cfg = None

def export_dict_to_csv(d):
    with open('slots_values_map.csv', 'w') as f:
        for k in d.keys():
            f.write('%s, %d, %s\n'%(k, d[k]['len'], ','.join(d[k]['vals'])))
def export_dict_to_data_text(d):
    for k in d.keys():
        with codecs.open('./thanh/%s.txt'%k, 'w', 'UTF-8') as f:
            f.write('%s\n'%k)
            for v in d[k]['vals']:
                f.write('%s\n'%v)
        
def get_config():
    global cfg
    cfg = Config.load_configs(['../applications/PublicTransportInfoEN/ptien.cfg'])#, '../applications/PublicTransportInfoEN/ptien_hdc_slu.cfg'])
    cfg['Logging']['system_logger'].info("Voip Hub\n" + "=" * 120)

def get_data():
    slu_type = cfg['SLU']['type']
    db = CategoryLabelDatabase(cfg['SLU'][slu_type]['cldb_fname'])
    #pdb.set_trace()
    #db.synonym_value_category [list of tuble]"list alternative words/text", value, slot = cl = category lable
    #db.form_value_cl similar to above, [list of tuble] and similar values
    #db.form2value2cl dictionary mapping from list of anternative text to value and category, values is similar to two above but access by dictionary key
    slots = set()
    values = {}
    #pdb.set_trace()
    for t in db.form_value_cl:#beter to uses synonym_value_category, so we get more various values
        #print t[2] + ':' + t[1] + '\t' + str(t[0][0:5])
        slots.add(t[2])
        if t[2] in values.keys():
            if t[1] not in values[t[2]]['vals']:
                values[t[2]]['len'] +=1
                values[t[2]]['vals'].append(t[1]) 
        else:
            values[t[2]]= {'len':1, 'vals':[t[1]]}
    print slots
    #print values       
    #export_dict_to_csv(values) 
    export_dict_to_data_text(values)
    pdb.set_trace()
        #raw_input()

def get_slu_dialogue_acts():
    slu = slu_factory(cfg)
    das = {}
    da_types = set()
    slots = set()
    for clser in slu.parsed_classifiers:
        da = slu.parsed_classifiers[clser]
        da_types.add(da.dat)
        da.name = str(da.name)
        slots.add(da.name)
        if da.dat in das:
            if da.name not in das[da.dat]:
                das[da.dat].append(da.name)
        else:
            das[da.dat] = [da.name]
    with open('dialogue_acts_slots.csv', 'w') as f:
        f.write('%s\n'%','.join(da_types))
        f.write('%s\n\n'%','.join(slots))
        for k in das:
            f.write('%s, %s\n'%(k, ', '.join(das[k])))
    pdb.set_trace()

def write_list_textfile(lst, fname):
    with open(fname, 'w') as f:
        for i in lst:
            f.write(i + '\n')

def generate_time():
    lst = ['now', 'next hour', 'morning', 'noon', 'afternoon', 'night']
    for h in range(24):
        for m in range(0, 60, 5):
            if h<12:
                lst.append(str(h) + ':' + str(m) + ' AM')
            else:
                if h==12:
                    lst.append(str(h) + ':' + str(m) + ' PM')
                else:
                    lst.append(str(h%12) + ':' + str(m) + ' PM')
    write_list_textfile(lst, 'time.txt')

def generate_date():
    lst = ['today', 'tomorrow', 'the day after tomorrow']
    day = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    lst.extend(day)
    for d in day:
        lst.append('next ' + d)
    for d in day:
        lst.append(d + ' next week')
    months = 'January,February,March,April,May,June,July,August,Septemper,October,November,December'.split(',')
    month_len = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    i = -1
    for m in months:
        i +=1
        for d in range(1, month_len[i] +1):
            lst.append(m + ' ' + str(d))
    write_list_textfile(lst, 'date.txt') 

def file_to_list(fname):
    with codecs.open('./thanh/%s.txt'%fname, 'r', 'UTF-8') as f:
        f.readline()
        lst = []
        for line in f.readlines():
            lst.append(line.strip())
    return lst

def list_to_file(lst, fname):
    with codecs.open('./thanh/%s.txt'%fname, 'w', 'UTF-8') as f:
        for line in lst:
            f.write('%s\n'%line)

def generate_places():
    streets = file_to_list('street')
    cities = file_to_list('city')
    cities.extend(file_to_list('borough'))
    states = file_to_list('state')
    
    num = len(streets)
    city_num = sample_from_list(cities, num, True)
    state_num = sample_from_list(states, num, True)
    final = [s + '\t' + c + '\t'+ st for s, c, st in zip(streets, city_num, state_num)]
    pdb.set_trace()
    list_to_file(final, 'places.txt')

def explore_ontology():
    pdb.set_trace()

def main():
    get_config()
    #get_data()
    #get_slu_dialogue_acts()
    #generate_time()
    #generate_date()
    #generate_places()
    explore_ontology()

if __name__ == '__main__':
	main();
