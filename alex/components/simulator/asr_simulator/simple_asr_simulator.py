import autopath
import pdb

import random
from alex.utils.config import Config
from alex.components.slu.da import DialogueActItem, DialogueActConfusionNetwork, DialogueAct

from alex.utils.sample_distribution import sample_from_dict, sample_from_list
from alex.components.simulator.base import ASRSimulator
from alex.utils.support_functions import override_dicts

class SimpleASRSimulator(ASRSimulator):
    '''Simple ASR simulator'''
    def __init__(self, cfg):
        self.full_config = cfg
        self._name = self.__class__.__name__
        self.config = cfg['asr_simulator'][self._name]
        self.system_logger = self.full_config['Logging']['system_logger']

        self.domain = ''
    
    def simulate_asr(self, user_da):
        '''Returns N-best list ASR hypothesis given correct user_da and grammar or data etc.'''
        for da_item in user_da:
            ret = self.simulate_one_da_item(da_item)
            print ret

    def simulate_one_da_item(self, da_item):
        original_da_type = da_item.dat
        original_slot = da_item.name
        original_value = da_item.value

        #get the da_types/acts will be confused
        act_confusion = self.config['act_confusion']
        da_types = original_da_type
        if original_da_type in act_confusion.keys():
            da_types = sample_from_dict(act_confusion[original_da_type])
        if isinstance(da_types, str):#only one datype will be generate
            da_types = [da_types]

        #Confusing things
        for da_type in da_types:#for every dalougue act (type) which  will be considerd or confused, such as inform, affirm
            #TODO check if this da_type is action without slot then don run the remaining
            #get slots will be confused
            '''Continue Here definition for acts'''
            slot_confusion = self.config['slot_confusion']
            slots = original_slot
            if original_slot in slot_confusion.keys():
                slots = sample_from_dict(slot_confusion[original_slot])
            if isinstance(slots, str):#only one slot
                slots = [slots]
            
            da_items = []#confusing slot and its values
            for slot in slots:#for every slot
                confusion_des = self._get_confusion_description(slot, da_type)
                print '---', da_type, slot
                confusion_type = self._sample_confusion_type(confusion_des['confusion_types'])
                correct_position = 0
                if confusion_type == 'silence':
                    da_item = DialogueActItem('silence')
                    da_items.append(da_item)
                else:
                    length = confusion_des['max_length']
                    length = random.randint(1, length)
            
                    correct_position = 0 #this postion for the confusion type = correct
                    if confusion_type == 'correct':
                        correct_position = 0
                    elif confusion_type == 'offlist':
                        correct_position = -1
                    elif confusion_type == 'onlist':
                        correct_position = self._sample_onlist_position(confusion_des, length) #sample
                    else:
                        raise NotImplementedError('confusion_type=%s was not implemented.'%confusion_type)   
                    print da_type, slot, confusion_type, correct_position
                #pdb.set_trace()
    
    def _sample_confusion_type(self, confusion_des):
        return sample_from_dict(confusion_des)

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

    def _sample_dialogue_act_item_hypotheses(self):
        pass

#-----------for developing------
cfg = None

def get_config():
    global cfg
    cfg = Config.load_configs(['config_asr_simulator.py'], log=False)

def main():
    get_config()
    #db = PythonDatabase(cfg)
    asr = SimpleASRSimulator(cfg)
    
    da = DialogueAct('inform(to_stop=Central Park)')
    asr.simulate_asr(da)

if __name__ == '__main__':
    main()
