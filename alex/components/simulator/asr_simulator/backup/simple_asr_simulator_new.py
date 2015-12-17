import autopath
import pdb

import random
from statlib.stats import lbetai

from alex.utils.config import Config
from alex.components.slu.da import DialogueActItem, DialogueActConfusionNetwork, DialogueAct, DialogueActNBList

from alex.utils.sample_distribution import sample_from_dict, sample_from_list, sample_dirichlet_from_dict
from alex.components.simulator.base import ASRSimulator
from alex.utils.support_functions import override_dicts, iscallable
from alex.utils.database.python_database import PythonDatabase

class SimpleASRSimulator(ASRSimulator):
    '''Simple ASR simulator'''
    def __init__(self, cfg, db):
        self.full_config = cfg
        self._name = self.__class__.__name__
        self.config = cfg['asr_simulator'][self._name]
        self.system_logger = self.full_config['Logging']['system_logger']

        self.domain = self.full_config['domain']
        self.db = db
        self.prob_combine_fun = self.config['prob_combine_fun']
        if self.prob_combine_fun is None:
            self.prob_combine_fun = lambda p1, p2: p1*p2
    
    def simulate_asr(self, user_da):
        '''Returns N-best list ASR hypothesis given correct user_da and grammar or data etc.'''
        self._sampled_da_items = []
        for da_item in user_da:
            self._sampled_da_items.append(self.simulate_one_da_item(da_item))
        
        #return self._sampled_da_items
        
        #print 'get sample da_items', self._sampled_da_items
        #self._nbest_list = DialogueActNBList()
        #self._build_da_nbest_list(0, None, None)
        #print 'get nbest-listobject'

        #return self._nbest_list
    
        return self._build_confusion_network(self._sampled_da_items)

    def _build_confusion_network(self, sampled_da_items):
        confusion_net = DialogueActConfusionNetwork()
        for da_items, probs in sampled_da_items:
            for dai, prob in zip(da_items, probs):
                confusion_net.add_merge(prob, dai)

        return confusion_net

    def _build_da_nbest_list(self, i, da, prob):
        if i<len(self._sampled_da_items):
            da_items, probs = self._sampled_da_items[i]
            for dai_index in range(len(da_items)):
                if da is None:
                    da_new = DialogueAct()
                    da_new.append(da_items[dai_index])
                    self._build_da_nbest_list(i+1, da_new, probs[dai_index])
                else:
                    da_new = DialogueAct()
                    da_new.extend(da)
                    da_new.append(da_items[dai_index])
                    self._build_da_nbest_list(i+1, da_new, prob*probs[dai_index])#TODO check the equation and fix it when we there is more types of confusion
        else:
            self._nbest_list.add(da, prob)

    def simulate_one_da_item(self, da_item):
        #TODO: The current way of sample prob is not really fit with action and slot confusion, just for value confusion
        print '--Simulate da_item:', da_item
        original_da_type = da_item.dat
        original_slot = da_item.name
        original_value = da_item.value

        #get the da_types/acts will be confused
        da_types, da_types_probs = self._get_confused_acts(original_da_type)
        print zip(da_types, da_types_probs)
        #print '------FInish test, da confused: '
        #print da_types, '|||',  da_types_probs
        #pdb.set_trace()

        #Confusing things
        da_items = []#all item confused for this da_item
        da_items_probs = []
        #Each confused action have a prob of 1 for its all confused elements and will be combined/recalculate later
        for index, da_type in enumerate(da_types):#for every dalougue act (type) which  will be considerd or confused, such as inform, affirm 
            #get the act_out definitions and check is this actionneed slot
            #print 'build ', da_type
            act_out_des = self.domain['dialogue_act_definitions'][da_type]
            if 'act_without_slot' in act_out_des.keys() and act_out_des['act_without_slot']:
                da_item = DialogueActItem(da_type)
                da_items.append(da_item)
                da_items_probs.append(self.prob_combine_fun(1.0, da_types_probs[index]))
                continue
            #get slots will be confused
            slot_confusion = self.config['slot_confusion']
            slots = original_slot
            if original_slot in slot_confusion.keys():
                slots = sample_from_dict(slot_confusion[original_slot])
            if not isinstance(slots, list):#only one slot
                slots = [slots]
            #print 'check confused slots'
            #pdb.set_trace() 
            for slot in slots:#for every slot
                if act_out_des['value_included']==False:
                    da_items.append(DialogueActItem(da_type, slot))
                    da_items_probs.append(self.prob_combine_fun(1.0,da_types_probs[index]))
                    continue
                    
                confusion_des = self._get_confusion_description(slot, da_type)
                items, probs = self._get_confused_slot_values(confusion_des, slot, original_value)
                for item, prob in zip(items, probs):
                    da_items.append(DialogueActItem(da_type, slot, item))
                    da_items_probs.append(self.prob_combine_fun(prob,da_types_probs[index]))
                             
        #print 'Get final resul for a dialogue_item:', da_items
        print '***sampled dialogue acts:'
        for dai, prob in zip(da_items, da_items_probs):
            print dai, '\t', prob
            
        return da_items, da_items_probs

    def _get_confused_slot_values(self, confusion_des, slot, true_value): 
        confusable_values = self._get_slot_values(slot)  
        items, probs = self._get_confused_values(confusion_des, true_value, confusable_values)

        return items, probs

    def _get_confused_acts(self, da_type):
        act_confusion = self.config['act_confusion']
        confusion_des = act_confusion['default']['confusion_matrix']
        if da_type in act_confusion.keys():
            confusion_des = override_dicts(act_confusion[da_type]['confusion_matrix'], confusion_des)

        #confusion_des = confusion_des['confusion_matrix']
        confusable_values = confusion_des['confusable_acts']
        if da_type not in confusable_values:
            confusable_values.append(da_type)

        acts, probs = self._get_confused_values(confusion_des, da_type, confusable_values)
        return acts, probs

    def _get_confused_values(self, confusion_des, true_value, confusable_values):
        items = []
        probs = []

        confusion_type = self._sample_confusion_type(confusion_des)
        print 'confusion_type:', confusion_type,

        if confusion_type == 'silence':#can be never used since it is similar to the act confusion
            items.append('silence')
            probs.append(1.0)
        else:
            length = confusion_des['max_length']
            length = random.randint(1, length)
            if length>len(confusable_values):
                #pdb.set_trace()
                length=len(confusable_values)

            correct_position = 0 #this postion for the confusion type = correct
            if confusion_type == 'correct':
                correct_position = 0
            elif confusion_type == 'offlist':
                correct_position = -1
            elif confusion_type == 'onlist':
                correct_position = self._sample_onlist_position(confusion_des, length) #sample
            else:
                raise NotImplementedError('confusion_type=%s was not implemented.'%confusion_type)
            
            print 'length=', length
            items = self._sample_nbest_list_values(confusable_values, true_value, correct_position, length)
            probs = self._sample_nbest_list_probs(confusion_des, confusion_type, length)
        return items, probs

    def _sample_nbest_list_values(self, values, true_value, correct_position, length):
        items = []

        sample_length = length
        if correct_position == -1:#Plus one in the case of sampled value equal to correct value
            sample_length = length + 1

        row_ids = random.sample(xrange(len(values)), sample_length)
        for i in range(length):
            item = None
            if i==correct_position:
                item = true_value
            else:
                while True:
                    row_id = row_ids.pop(0)
                    if values[row_id] != true_value:
                        item = values[row_id]
                        break
            items.append(item)
        return items 

    def _sample_confusion_type(self, confusion_des):
        return sample_from_dict(confusion_des['confusion_types'])

    def _get_confusion_description(self, slot, da_type):
        slot_confusion_des = self.config['default']
        if slot in self.config.keys():
            slot_confusion_des = self.config[slot]

        refine_key = da_type + '_confusion_matrix'
        if refine_key in slot_confusion_des.keys():#this da_type is refined for this slot
            refine = slot_confusion_des[refine_key]
            slot_confusion_des = override_dicts(refine, slot_confusion_des['default_confusion_matrix'])
        else:
            slot_confusion_des = slot_confusion_des['default_confusion_matrix']

        return slot_confusion_des

    def _sample_onlist_position(self, confusion_des, length):
        alpha = confusion_des['onlist_fraction_alpha']
        beta = confusion_des['onlist_fraction_beta']
        x = random.betavariate(alpha, beta)
        position = int((length-1)*x)+1
        if position ==length:
            position -=1
        return position

    def _sample_nbest_list_probs(self, confusion_des, confusion_type, length):
        '''Sample probabilities for n-bestlist hypotehsis.'''
        sample_probs = sample_dirichlet_from_dict(confusion_des['probability_generator'][confusion_type])
        probs = [sample_probs['correct']]
        if length==1:
            pass
        else:
            if length==2:
                onlist_fractions = [1.0]
            else:
                onlist_fractions = self._get_onlist_fractions(confusion_des, length)
            for i in range(1, length):
                probs.append(sample_probs['onlist']*onlist_fractions[i-1])
        return probs

    def _get_onlist_fractions(self, confusion_des, length):
        frac = []; prev = 0.0
        step_size = 1.0/(length-1.0)
        alpha = confusion_des['onlist_fraction_alpha']
        beta = confusion_des['onlist_fraction_beta']
        for i in range(length-1):
            x = step_size*(i+1)
            b = lbetai(alpha, beta, x)
            frac.append(b-prev)
            prev = b
        return frac
 
#-----------------------------General function for processing domain
    def _get_slot_values(self, slot):
        '''Get a all distinct values for the given slot.'''
        values = set()
        tables_fields = self._get_slot_mapping(slot)
        for tbf in tables_fields:#sample a value of each table which the slot is connected
            if iscallable(tbf):#slot have values generated dynamic from one or several funs
                values = values.union(tbf())
            else:
                tb, f = tbf
                values = values.union(self.db.get_field_values(tb, f))
        return list(values)

#-----------------------------General function for domain, which is currently copy from user simulator
    def _get_slot_mapping(self, slot):
        '''Return a full set of table field mapping for the given slot.'''
        assert slot in self.domain['slot_table_field_mapping'].keys(), "Have not defined the slot_table_field_mapping for the slot=%s"%(slot)
        return self.domain['slot_table_field_mapping'][slot]

#-----------for developing------
cfg = None
db = None

def get_config():
    global cfg
    cfg = Config.load_configs(['config_asr_simulator.py'], log=False)

def print_nbest_list(nbest_list):
    print '-'*20, 'da_items'
    print nbest_list
    print '-'*20, 'nblist ='
    for prob, da in nbest_list.get_da_nblist():
        print str(da), '\t', prob
    print '-'*20, 'best hyp='
    print nbest_list.get_best_da_hyp()

def print_asr_results(asr):
    for items, probs in asr:
        for item, prob in zip(items, probs):
            print prob, '\t', item

def test1():
    asr = SimpleASRSimulator(cfg, db)

    da = DialogueAct('deny(to_stop=thanh)')
    #da = DialogueAct('inform(task=find_connection)')
    #da = DialogueAct('inform(to_stop=Central Park)')
    #da = DialogueAct('inform(from_stop=Thanh)&inform(to_stop=Central Park)')
    #da = DialogueAct('affirm()')
    #da = DialogueAct('affirm()&inform(to_stop=Central Park)')
    for i in range(1):
        asr_results  = asr.simulate_asr(da)
        print_nbest_list(asr_results)

    #print_asr_results(asr_results)
    #confusion_net = asr.simulate_asr(da)
    #print confusion_net
    #print_nbest_list(confusion_net)
    #pdb.set_trace()

def main():
    global db
    get_config()
    db = PythonDatabase(cfg)
    test1()

if __name__ == '__main__':
    main()
