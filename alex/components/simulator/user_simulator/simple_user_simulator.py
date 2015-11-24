#----------for testing---------------
if __name__ == '__main__':
    import autopath
#-------define for specific app--------------
#import alex.utils.matlab_functions as matlab
def values_generator1(goal, slot):
    return [1,2,3]
def values_generator2(goal, slot):
    return [7,8,9]

def goal_post_process(user, goal):
    #handle the sematic relation between departure and arrival slots
    '''
    if 'arrival_time' in goal.keys():
        if goal['arrival_time'] == 'now':
            goal['arrival_time'] = 'as soon as possible'
            goal['arrival_time_relative']= 'at'
    if 'departure_time' in goal.keys():
        if goal['departure_time']=='now':
            if goal['departure_date']!='today':
                goal['departure_time'] = 'as soon as possible'    
            goal['departure_time_relative'] = 'at'
    if matlab.is_subset(['arrival_time', 'departure_time'], goal.keys()):
        ad = user.db.get_row_position('date', (goal['arrival_date'],))
        dd = user.db.get_row_position('date', (goal['departure_date'],))
        if ad<dd:
            goal['arrival_date']= user.db.get_random_row('date', dd)
    '''
    return goal

import random

from alex.components.simulator.base import UserSimulator
from alex.utils.database.python_database import PythonDatabase
from alex.components.slu.da import DialogueActItem, DialogueActConfusionNetwork, DialogueAct

from alex.utils.sample_distribution import sample_from_list, sample_from_dict, random_filter_list
import alex.utils.matlab_functions as matlab
from alex.utils.support_functions import get_dict_value, iscallable

class SimpleUserSimulator(UserSimulator):
    '''Simple user simulator'''

    def __init__(self, cfg, db):
        '''Initilise'''
        self._config = cfg.config['user_simulator']
        self.db = db
        self.goal = None
        self.metadata = self.get_metadata(self._config)
        #self._goal_dist = self._get_goal_distribution()
        self._goal_dist = self._get_dict_distribution(self.metadata['goals'])

    def _get_dict_distribution(self, lst_dict):
        '''Get dict distribution for a list of dictionary, in which each dict has the key active_prob specifying the chance of it being active'''
        d = {}
        if isinstance(lst_dict, dict):
            for key in lst_dict.keys():
                d[key] = lst_dict[key]['active_prob']
        else:
            for i in range(len(lst_dict)):
                d[i] = lst_dict[i]['active_prob']
        return d

    def new_dialogue(self):
        '''Start a new dialogue
        Sample a new user goal. Reset everything for simulating a new dialogue
        '''
        self.goal = self._get_random_goal()
        #self.dialog_turns = [] make the full history in somewhere else, not the task of user simulator
        self.unprocessed_da_queue = []
        self.act_used_slots = {}

    def _get_random_goal(self):
        '''Return a random final goal of user'''
        self.goal_id = sample_from_dict(self._goal_dist)
        goal_des = self.metadata['goals'][self.goal_id]
        goal = {}
        self.goal = goal
        sampled_slots = []

        for s, v in goal_des['fixed_slots']:#fixed slots
            goal[s] = v
            sampled_slots.append(s)

        for key in goal_des['same_table_slot_keys']:#same table slots NOTE same_table_slot was coded without testing since data hadn't faked yet
            slots_values = self._get_random_same_table_slots_values(key)
            for slot in slots_values.keys():
                if slot in goal_des['changeable_slots']:
                    sampled_slots.append(slot)
                    goal[slot] = slots_values[slot]

        for one_set in goal_des['one_of_slot_set']:#get value for  one slot set and ignore other slots
            slot_set = sample_from_dict(one_set)
            for slot in slot_set:
                goal[slot] = self._get_random_slot_value(slot)
            for key in one_set.keys():
                sampled_slots.extend(key)

        sampled_slots.extend(goal_des['sys_unaskable_slots'])
        remain_slots = matlab.subtract(goal_des['changeable_slots'], sampled_slots)
        for slot in remain_slots:#changeable slots
            goal[slot] = self._get_random_slot_value(slot)

        '''Don't fill default slots, only return when system ask
        for slot, value in goal_des['default_slots_values']:#fill the default slot which was not being filled
            if slot not in goal.keys():
                goal[slot] = value
        '''
    
        fun = get_dict_value(goal_des,'goal_post_process_fun')
        if fun is not None:
            goal = fun(self, goal)
        return goal

    def _get_random_same_table_slots_values(self, same_table_key):
        same = self.metadata['same_table_slots'][same_table_key]
        table = same['table']
        row = self._get_random_row(table)
        sv = {}
        for slot in same['slots']:
            field = self._get_field_name(slot, table)
            sv[slot]= self.db.get_row_field_value(table, row, field)
        return sv

    def _get_random_slot_value(self, slot):
        values = []
        tables_fields = self._get_slot_mapping(slot)
        for tbf in tables_fields:#sample a value of each table which the slot is connected
            if iscallable(tbf):#slot have values generated dynamic from one or several funs
                v = sample_from_list(tbf(self.goal, slot))
                values.append(v)
            else:  
                tb, f = tbf
                row = self._get_random_row(tb)
                values.append(self.db.get_row_field_value(tb, row, f))
        return sample_from_list(values)#take one in the sampled values
        
    def _get_random_row(self, table):
        if table in self.metadata['data_observation_probability'].keys():
            data_dist = self._get_data_distribution(table)
            return sample_from_dict(data_dist)
        else:
            return self.db.get_random_row(table)

    def _get_data_distribution(self, table):
        dist = {}
        tb_dist = self.metadata['data_observation_probability'][table]
        predifined_mass = 0.0
        predifined_row = 0
        for key in tb_dist.keys():
            predifined_mass += tb_dist[key]
            predifined_row += 1
        remaining_mass = 1.0 - predifined_mass
        default_prob = remaining_mass/(self.db.get_row_number(table)-predifined_row)
        for row in self.db.get_row_iterator(table):
            if row in tb_dist.keys():
                dist[row] = tb_dist[row]
            else:
                dist[row] = default_prob
        return dist
        
    def _get_field_name(self, slot, table):
        mapping = self._get_slot_mapping(slot)
        for tb, f in mapping:
            if tb==table:
                return f
        assert False, "There is no table=%s in the slot_table_field_mapping definition of the slot=%s"%(table, slot)
    def _get_slot_mapping(self, slot):
        assert slot in self.metadata['slot_table_field_mapping'].keys(), "Have not defined the slot_table_field_mapping for the slot=%s"%(slot)
        return self.metadata['slot_table_field_mapping'][slot]  

    def da_in(self, da):
        '''Recieve a system dialogue act'''
        assert self.goal is not None, 'user simulator has no goal, you have to call new_dialogue building goal first before make conversation'
        self.unprocessed_da_queue.append(da)

    def da_out(self):
        '''Samples and returns a user dialogue act based on user's current state and given system dialogue act'''
        das = []
        while(len(self.unprocessed_da_queue)>0):
            da = self.unprocessed_da_queue.pop(0)
            das.append(self._get_answer_da(da))
        #if len(das)==1:
        #    das = das[0]
        return das

    
    def _get_answer_da(self, da_in):
        da_out = DialogueAct()

        reply_sys_acts = self.metadata['reply_system_acts']
        da_metadata = self._get_dialogue_act_metadata(da_in)
        for act_in in da_metadata.keys():
            reply = reply_sys_acts[act_in]
            answer = self._sample_element_from_list_dict(reply)
            if 'ordered_return_acts' in answer:#process list of answer in order, and stop for first appliable
                for solution in answer['ordered_return_acts']:
                    case = self._sample_element_from_list_dict(solution)
                    da_items = self._build_one_answer(da_metadata[act_in], case)
                    if len(da_items)>0:
                        break
            else:
                da_items = self._build_one_answer(da_metadata[act_in], answer)
                
            ''' 
            for act_out in answer['return_acts']:#for reply without ordered answer
                answer_types = get_dict_value(answer, act_out + '_answer_types')
                answer_type = None
                if answer_types is not None:
                    answer_type = sample_from_dict(answer_types)
                da_items = self._build_dialogue_act_items(da_metadata[act_in], act_out, answer_type)
                print '---------get da item out', da_items
                da_out.extend(da_items)
            '''
            da_out.extend(da_items)
        return da_out

    def _build_one_answer(self, da_metadata, answer):
        print answer
        da_items = []
        for act_out in answer['return_acts']:#for reply without ordered answer
            answer_types = get_dict_value(answer, act_out + '_answer_types')
            answer_type = None
            if answer_types is not None:
                answer_type = sample_from_dict(answer_types)
            overridden_properties = get_dict_value(answer, act_out + '_overridden_properties')
            da_items.extend(self._build_dialogue_act_items(da_metadata, act_out, answer_type, overridden_properties))
        return da_items

    def _sample_element_from_list_dict(self, lst_dict):#should be static or class function, but this way potential for future speeup with caching
        dist = self._get_dict_distribution(lst_dict)
        index = sample_from_dict(dist)
        return lst_dict[index]
        
    def _get_dialogue_act_metadata(self, da):
        d = {}
        for item in da:
            act = item.dat
            slot = item.name
            value = item.value
            if act in d.keys():
                d[act]['slots'].append(slot)
                d[act]['values'].append(value)
                d[act]['slot_value'][slot] = value
            else:
                d[act] = {
                    'slots': [slot],
                    'values': [value],
                    'slot_value': {slot:value},
                }
        return d
                
    def _build_dialogue_act_items(self, act_in, act_out, answer_type, overridden_properties):
        print act_in
        print act_out
        print answer_type
        if act_out not in self.act_used_slots.keys():#saving this action used this slot
            self.act_used_slots[act_out] = set()

        act_out_des = self.metadata['dialogue_act_definitions'][act_out]
        act_out_des = self._override_act_descriptions(overridden_properties, act_out_des)
        da_items = []
        combined_slots = self._get_combined_slots(act_in, act_out_des, answer_type, self.act_used_slots[act_out])
        for slot in combined_slots:
            item = DialogueActItem()
            item.dat = act_out
            if act_out_des['slot_included']:
                item.name = slot
            if act_out_des['value_included']:
                if act_out_des['value_from']=='goal':
                    if slot not in self.goal.keys():#required slot not in goal
                        eq_slots = self._get_equivalent_slots(slot)
                        for s in eq_slots:#gen value from a equivalent slot
                            if s in self.goal.keys():
                                slot = s
                                break
                    if slot not in self.goal.keys():#dont have compatible slots, get from default values
                        value = self._get_default_slot_value(slot)
                        if value is not None:
                            item.value = value
                        else:
                            for s in eq_slots:#get default of equivalent slots
                                value = self._get_default_slot_value(s)
                                if value is not None:
                                    item.value = value
                                    item.name = s
                            if item.value is None:
                                raise RuntimeError('Cant find value for slot %s and its equivalents slot from goal and default slots'%slot)
                    else:
                        item.value=self.goal[slot]
                        item.name = slot
                elif act_out_des['value_from']=='sys_da':
                    item.value = act_in['slot_value']['slot']
                else:
                    raise NotImplementedError('value_from=%s unhandled yet'%act_out_des['value_from'])

            self.act_used_slots[act_out].add(slot)#save to the list of used slot for this act_out
                
            if item not in da_items:
                da_items.append(item)

        if len(combined_slots)==0 and len(da_imtes)==0:
            raise RuntimeError('Cant find any slot, value for the given dialogue act, %s'%act_out)
        '''
        if len(combined_slots)==0:
            if len(act_out_des.keys())==2 and act_out_des['slot_included']==False and act_out_des['value_included']==False:#act_out desnt need slot at all
                da_items.append(DialogueActItem(act_out))
            else:
                print 'cant build %s since not satisfy required slot combined'%act_out
                #raise RuntimeError('Cant find any slot, value for the given dialogue act, %s'%act_out)
        '''
        return da_items

    def _override_act_descriptions(self, new_des, original_des):
        if new_des is None:
            return original_des
        for key in new_des.keys():
            original_des[key] = new_des[key]
        return original_des

    def _get_default_slot_value(self, slot):
        goal_des = self.metadata['goals'][self.goal_id]
        for s , v in goal_des['default_slots_values']:
            if s==slot:
                return v
        return None

    def _get_equivalent_slots(self, slot):
        goal_des = self.metadata['goals'][self.goal_id]
        if 'equivalent_slots' in goal_des:
            for eq_slots in goal_des['equivalent_slots']:
                if slot in eq_slots:
                    return eq_slots
        return ()

    def _get_combined_slots(self, act_in, act_out_des, answer_type, used_slots):
        lst = []

        remain_slots = self.goal.keys()

        if 'combineable_slots' in act_out_des.keys():#figured out list of combineable slot in the config file, but still have to filter at status slot
            lst.extend(act_out_des['combineable_slots'])
            #return act_out_des['combineable_slots']
            remain_slots = act_out_des['combineable_slots']
            
        if 'accept_used_slot' in act_out_des.keys() and act_out_des['accept_used_slot']==False:#filter used slot
            remain_slots = matlab.subtract(remain_slots, used_slots)

        if 'slot_from' in act_out_des.keys():#take all slot in the type figured in slot_from
            if act_out_des['slot_from']=='sys_da':
                lst.extend(act_in['slots'])
            elif act_out_des['slot_from']=='none':
                pass#dont take slot from sys_da
            else:
                raise NotImplementedError('slot_from=%s unhandled yet'%act_out_des['slot_from'])
            
        #process answer_type
        if answer_type=='direct_answer':
            pass#every slot in sys_da already included
        elif answer_type=='over_answer':
            #TODO: only over or complete answer for slot not mentioned
            remain_slots = matlab.subtract(remain_slots, lst)
            lst.extend(random_filter_list(remain_slots))
        elif answer_type=='complete_answer':
            remain_slots = matlab.subtract(remain_slots, lst)
            lst.extend(remain_slots)
        elif answer_type is None:
            pass
        else:
            raise NotImplementedError('answer_type=%s unhandled yet'%answer_type)

        #process litmited slots
        if 'limited_slots' in act_out_des.keys():
            lst = matlab.subtract(lst, act_out_des['limited_slots'])

        #process status included
        if 'status_included' in act_out_des.keys():
            status_included = act_out_des['status_included']
            lst = self._filter_slot_status(act_in, lst, status_included)
        
        if 'status_in_all_slots' in act_out_des.keys() and act_out_des['status_in_all_slots']:
            if len(lst)!= len(act_in['slots']):
                lst = []#this action require all of requested slot must satisfy the given status
        return lst
    
    def _filter_slot_status(self, act_in, slots, status):
        if status=='all':
            return slots
        lst = []
        for s in slots: 
            if status=='correct' and self.goal[s]== act_in['slot_value'][s]:
                lst.append(s)
            elif status=='incorrect' and self.goal[s]!= act_in['slot_value'][s]:
                lst.append(s)
            else:
                raise NotImplementedError('status_included=%s unhandled yet'%status)
        return lst

    def reward_last_da(self):
        '''Rewards the last system dialgoue act'''
        return self.metadata[self.goal_id]['reward_last_da_fun'](self.last_da)

    def reward_final_goal(self, sys_predict):
        '''Return final reward for the current dialouge'''
        return self.metadata[self.goal_id]['reward_final_goal_fun'](self.goal, sys_predict)
        
    def end_dialogue(self):
        '''end dialgoue and post-processing'''
        fun = get_dict_value(self.metadata['goals'][self.goal_id], 'end_dialogue_post_process_fun')
        if fun is not None:
            fun(self)

    #-----------define for specific app-----------------
    def get_metadata(self, cfg):#This metadata is for user simulator, and the content is for specific apps
        metadata = {
            'slots': ['from_stop', 'to_stop', 'from_city', 'to_city', 'from_street', 'to_street', 
                    'departure_time', 'departure_date', 'arrival_time', 'arrival_date',
                    'vihecle', 'arrival_time_rel', 'depature_time_rel', 'number_transfers', 'duration',' distance',
                    'street', 'city', 'state',
                    'alternative', 'date_rel',#How to push it in to the simulator
                    'slot_fun',#only for test slots have value list generating dyanmically from fun
                ],#only for easy seeing and imagining, not being used in coding
            'goals': [
                    {'fixed_slots':[('task','find_connection'),],
                    'changeable_slots':['from_stop', 'to_stop', 'from_city', 'to_city', 'from_street', 'to_street',
                                        'departure_time', 'arrival_time', 'departure_time_rel', 'arrival_time_rel',
                                        'vehicle',
                                        'number_transfer', 'duration', 'distance',#users dont know these slot
                            ],
                    'one_of_slot_set':[
                            {('from_stop', 'to_stop'):0.3,#choose only one of these set
                            ('from_city', 'to_city'):0.2,
                            ('from_street', 'to_street'):0.3,
                            ('from_stop', 'to_street'):0.2,
                            },#end of the fist defination of one_of_slot_set
                            {():0.3,
                            ('arrival_time',):0.1,
                            ('departure_time',):0.1,
                            ('arrival_time_rel',):0.25,
                            ('departure_time_rel',):0.25,
                            },
                            {():0.5,
                            ('vehicle',):0.5,
                            },
                        ],
                    'equivalent_slots':[('from_stop', 'from_city', 'from_street'), ('to_stop', 'to_city', 'to_street'),
                                        ('arrival_time', 'arrival_time_rel'), ('departure_time', 'departure_time_rel'), 
                                    ],
                    'sys_unaskable_slots':['number_transfer', 'duration', 'distance',],
                    'default_slots_values':[('departure_time', 'as soon as possible'), ('vehicle', 'dontcare'), ('arrival_time', 'as soon as possible')],
                    #'add_fixed_slot_to_goal': True,
                    'active_prob':0.8,#probability of observing the task being active
                    'same_table_slot_keys':[],#defining when serveral slots connected to a row in a table and we would like to get them linked together
                    'goal_post_process_fun': None,#post process function to refine the sampled goal, which will be defined for specific semantic relations
                    'goal_slot_relax_fun': None,#support function, relax the value of a slot given curretn goal, e.g. more late arrival, departure sooner    
                    'reward_last_da_fun': None,
                    'reward_final_goal_fun': None,
                    'end_dialogue_post_process_fun': None,
                    'slot_used_sequence':{#higher level is only able to used when one of slot at previous level used#TODO not used in the code yet
                        0:('task', 'from_stop', 'from_city', 'from_street', 'to_stop', 'to_city', 'to_street'),
                        1:('departure_time', 'arrival_time', 'departure_tiem_rel', 'arrival_time_rel', 'vehicle'),
                        },
                    },
                    {'fixed_slots':[('task','find_platform'),],
                    'changeable_slots':['street', 'city', 'state'],
                    'one_of_slot_set':[],
                    'sys_unaskable_slots':[],
                    'default_slots_values':[],
                    'active_prob':0.15,
                    'same_table_slot_keys': ['place'],
                    'goal_post_process_fun': None,
                    'goal_slot_relax_fun': None,
                    },
                    {'fixed_slots':[('task','weather'),],
                    'changeable_slots':['city', 'state'],
                    'one_of_slot_set':[],
                    'sys_unaskable_slots':[],
                    'default_slots_values':[],
                    'active_prob':0.05,
                    'same_table_slot_keys':['place'],
                    'goal_post_process_fun': None,
                    'goal_slot_relax_fun': None,
                    },
                ],
            'slot_table_field_mapping':{'from_stop':[('stops','stop')],
                                        'to_stop':[('stops', 'stop')],
                                        'from_city':[('cities', 'city')],
                                        'to_city':[('cities', 'city')],
                                        'from_street':[('streets', 'street')],
                                        'to_street':[('streets', 'street')],
                                        'departure_time':[('time', 'time')],
                                        'departure_time_rel':[('time_relative', 'relative')],
                                        'arrival_time': [('time', 'time')],
                                        'arrival_time_rel': [('time_relative', 'relative')],
                                        'vehicle': [('vehicles', 'vehicle')],
                                        'street':[('streets', 'street'), ('places', 'street')],
                                        'city':[('cities', 'city'), ('places', 'city')],
                                        'state':[('states', 'state'), ('places', 'state')],
                                        'slot_fun':[values_generator1, values_generator2]#slot has the list of values being generated dynamically from functions, each function has to return a list of values, the list could includes only one element.
                                    },
            'same_table_slots':{'place':{'table': 'places',
                                        'slots': ['street', 'city', 'state'],
                                    },
                                'from_place':{'table':'places',#just for future when whe have such data.
                                        'slots': ['from_stop', 'from_street', 'from_city', 'from_state'],
                                    },
                                'to_place':{'table':'places',
                                        'slots': ['to_stop', 'to_street', 'to_city', 'to_state'],
                                }
                            },

            'status_included': ['correct', 'incorect', 'pending', 'filled', 'all'],# only for imagining
            'slot_value_from':['goal', 'sys_da'],#only for imagining
            'slot_from': ['sys_da', 'goal', 'none'],
            'answer_types':['direct_answer', 'over_answer', 'complete_answer'],#only for easy seeing and imagining

            'dialogue_act_definitions': {#dialogue acts which user simulator used for answering
                'request':{
                    'slot_included': True,
                    'value_included': False,
                    'combineable_slots': ['number_transfer', 'duration', 'distance']
                },
                'inform':{
                    'slot_included': True,
                    'value_included': True,
                    'slot_from': 'sys_da', #in normal case, list of slots will be informed is taken from system dialogue request act, or from goal
                    'value_from': 'goal', #in normal case, where to get values for selected slots
                    'limited_slots': [], #list of slot cant combine
                    'accept_used_slots': False,
                },
                'oog':{
                    'slot_included': False,
                    'value_included': False,
                },
                'deny':{
                    'slot_included': True,
                    'value_included': True,
                    'slot_from': 'sys_da',
                    'value_from': 'sys_da',
                    'status_included': 'incorrect',
                },
                'repeat':{
                    'slot_included': False,
                    'value_included': False,
                },
                'help':{
                    'slot_included': False,
                    'value_included': False,
                },
                'apology':{
                    'slot_included': False,
                    'value_included': False,
                },
                'confirm':{#make a question to clarify something, ?User may also make this action?? How to make it? only at the end?, since simulator always know exactly what is going on
                    'slot_included': True,
                    'value_included': True,
                    'status_included': 'filled',
                },
                'canthearyou, notunderstood':{#only available for system, not for user
                },
                'affirm':{#simply YES #something interesting here,  doesn't include slot/value, but slots consider from sys_da and they are correct
                    'slot_included': False,
                    'value_included': False,
                    'slot_from': 'sys_da',
                    'status_included': 'correct',
                    'status_in_all_slots': True,
                    #TODO add cheeck all sys_da slot?
                    #all_slot_included: True,
                },
                'ack':{
                    'slot_included': False,
                    'value_included': False,
                },
                'thankyou':{
                    'slot_included': False,
                    'value_included': False,
                },
               'silence':{
                    'slot_included': False,
                    'value_included': False,
                },
               'reqalts':{
                    'slot_included': False,
                    'value_included': False,
                },
                'negate':{
                    'slot_included': False,
                    'value_included': False,
                },
                'bye':{
                    'slot_included': False,
                    'value_included': False,
                },
                'hello':{
                    'slot_included': False,
                    'value_included': False,
                },
                'restart':{#TODO how to user this action?
                    'slot_included': False,
                    'value_included': False,
                },
                'hangup':{
                    'slot_included': False,
                    'value_included': False,
                },
                'help':{#How?
                    'slot_included': False,
                    'value_included': False,
                },
            },
            'act_formats':{#not being used
                'slot_value_correct':{
                    'slot_included': True,
                    'value_included': True,
                    'correct_slot_included': False,
                    'incorrect_slot_included': False,
                    'value_from': 'goal', #or from sys_da
                }
            },
            'reply_system_acts':{#how to combine several act types to respon an actions,list like below is quite ok, but ???
                'request':[{'return_acts':['inform'],#return acts canbe multiple act
                            'inform_answer_types':{
                                'direct_answer':0.7,
                                'over_answer':0.25,
                                'complete_answer':0.05,
                                },
                            'active_prob':0.9,
                            },
                            {'return_acts':['silence'],
                            'active_prob':0.05,
                            },
                            {'return_acts':['oog'],
                            'active_prob':0.05,
                            }
                 ],
                'confirm':[{#explict confirm
                            #TODO: only one action in the set or specify explicitly the apply order and stop when first appliable
                            #mush be dictionary since there is much more thing, affirm but dont talk etc.
                            #can we change to return_acts, what is different to keep booth? should maintain both for short config and clear distuiguish between two cases
                            'ordered_return_acts':[
                                {   'case1':{'return_acts':['affirm'],
                                        'active_prob':0.5
                                    },
                                    'case2':{'return_acts':['affirm', 'inform'],
                                        'active_prob':0.5,
                                        'inform_answer_types':{
                                            'over_answer':1.0
                                        },
                                        'inform_overridden_properties':{
                                            'slot_from': 'none',#should be none - nowhere, dont take slot form any where
                                        },
                                    },
                                },#end of first priority answer
                                {   'case1':{'return_acts':['negate', 'inform'],
                                        'active_prob':7.0,
                                        'inform_answer_types':{
                                            'direct_answer':1.0,
                                        },
                                        'inform_overrideden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                        },
                                    },
                                    'case2':{'return_acts':['deny'],
                                        'active_prob':0.1,
                                    },
                                    'case3':{'return_acts':['deny', 'inform'],
                                        'active_prob':0.2,
                                    },
                                }#end of seond priority answer
                            ],    
                            'active_prob':1.0
                        },#end of the firs way of answer
                ],
                'implconfirm':[
                ],
            },
            'data_observation_probability':{
                'tiime_relative':{
                    ('now',):0.2,#key is row in the table, if table has only one field, need add comma before the end of the tuple
                    ('next hour',):0.1,
                    ('morning',):0.1,
                    ('noon',):0.1,
                    ('afternoon',):0.1,
                    ('night',):0.1,
                    ('midnight',):0.05,
                    ('early morning',):0.05,
                    ('today',):0.1,
                    ('tomorrow',):0.05,
                    ('the day after tomorrow',):0.05,
                },
                'date':{
                    ('today',):0.5,
                    ('tomorrow',):0.025,
                    ('the day after tomorrow',):0.025,
                    ('Monday',):0.01,
                    ('Tuesday',):0.01,
                    ('Wednesday',):0.01,
                    ('Thursday',):0.01,
                    ('Friday',):0.01,
                    ('Saturday',):0.01,
                    ('Sunday',):0.01,
                    ('next Monday',):0.01,
                    ('next Tuesday',):0.01,
                    ('next Wednesday',):0.01,
                    ('next Thursday',):0.01,
                    ('next Friday',):0.01,
                    ('next Saturday',):0.01,
                    ('next Sunday',):0.01,
                    ('Monday next week',):0.01,
                    ('Tuesday next week',):0.01,
                    ('Wednesday next week',):0.01,
                    ('Thursday next week',):0.01,
                    ('Friday next week',):0.01,
                    ('Saturday next week',):0.01,
                    ('Sunday next week',):0.01,
                },
            },
            #TODO some of value in a slot can only be combined with a specific values of other slot, It shoud be push in a table but .... sometime exception
        }#end of metadata
        return metadata
    #-------------definetion for specific apps
    
#----------for testing---------------
if __name__ == '__main__':
    import autopath
import pdb
from alex.utils.config import Config
import pprint

cfg = None

def get_config():
    global cfg
    #pdb.set_trace()
    cfg = Config.load_configs(['../../../applications/PublicTransportInfoEN/ptien.cfg', '../../../applications/PublicTransportInfoEN/simulator.cfg'])
    cfg['Logging']['system_logger'].info("Voip Hub\n" + "=" * 120)

def test_user_goal(user, n):
    pp = pprint.PrettyPrinter()
    for i in range(n):
        user.new_dialogue()
        print '-------------------------Goal %d (type=%d)---------------------'%(i+1, user.goal_id+1)
        pp.pprint(user.goal)
        user.end_dialogue()
        #raw_input()
        #break

def test_reply(user):
    user.new_dialogue()
    print 'GOAL', user.goal
    act_type = 'confirm'
    slots = ['from_stop', 'from_street', 'from_city']
    act_slot = None
    act_value = None
    for slot in slots:
        if slot in user.goal.keys():
            act_slot = slot
            act_value = user.goal[slot]
            break
    #act_value='abc'
    da = DialogueAct()
    item = DialogueActItem(act_type, act_slot, act_value)
    da.append(item)
    print da
    user.da_in(da)
    dao = user.da_out()
    print dao[0]

def run1():
    db = PythonDatabase(cfg)
    user = SimpleUserSimulator(cfg, db)
    #test_user_goal(user, 100)
    test_reply(user)

def main():
    get_config()
    run1()

if __name__ == '__main__':
    main()
