import pdb
import codecs

if __name__ == '__main__':
    import autopath

from alex.utils.config import Config
from alex.components.slu.base import CategoryLabelDatabase, SLUInterface
from alex.components.slu.common import slu_factory

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

def main():
    get_config()
    get_data()
    #get_slu_dialogue_acts()

if __name__ == '__main__':
	main();
