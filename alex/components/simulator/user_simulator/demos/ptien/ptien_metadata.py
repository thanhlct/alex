from alex.utils.sample_distribution import sample_from_list

def values_generator1(goal, slot):
    '''Generate all values for a slot'''
    return [1,2,3]
def values_generator2(goal, slot):
    return [7,8,9]

def alternative_value_fun():
    '''A generator for a slot during conversation'''
    a = ['next', 'prev', 'last', '1', '2', '3', '4', 'next hour']
    return sample_from_list(a)

config = {
    'user_simulator':{
        'SimpleUserSimulator':{
            'debug': True,
            'metadata':{
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
                    'equivalent_slots':[('to_borough', 'from_stop', 'from_city', 'from_street'), ('to_borough', 'to_stop', 'to_city', 'to_street'),
                                        ('arrival_time', 'arrival_time_rel'), ('departure_time', 'departure_time_rel'),
                                    ],
                    'sys_unaskable_slots':['number_transfer', 'duration', 'distance',],
                    'default_slots_values':[('departure_time', 'as soon as possible'), ('vehicle', 'dontcare'), ('arrival_time', 'as soon as possible')],
                    #'add_fixed_slot_to_goal': True,
                    'active_prob':1.0,#probability of observing the task being active
                    'same_table_slot_keys':[],#defining when serveral slots connected to a row in a table and we would like to get them linked together
                    'goal_post_process_fun': None,#post process function to refine the sampled goal, which will be defined for specific semantic relations
                    'goal_slot_relax_fun': None,#support function, relax the value of a slot given curretn goal, e.g. more late arrival, departure sooner
                    'reward_last_da_fun': None,
                    'reward_final_goal_fun': None,
                    'end_dialogue_post_process_fun': None,
                    'slot_used_sequence':{#higher level is only able to used when one of slot at previous level used#TODO not used in the code yet
                        0:('task',),
                        1:('from_stop', 'from_city', 'from_street', 'to_stop', 'to_city', 'to_street'),
                        #1:('from_stop', 'from_city', 'from_street', 'to_stop', 'to_city', 'to_street', 'departure_time', 'arrival_time', 'departure_tiem_rel', 'arrival_time_rel', 'vehicle'),
                        2:('departure_time', 'arrival_time', 'departure_tiem_rel', 'arrival_time_rel', 'vehicle'),
                        #only need one of slot in each level informed to get next level
                        },
                    },
                    {'fixed_slots':[('task','find_platform'),],
                    'changeable_slots':['street', 'city', 'state'],
                    'one_of_slot_set':[],
                    'sys_unaskable_slots':[],
                    'default_slots_values':[],
                    'active_prob':0.0,
                    'same_table_slot_keys': ['place'],
                    'goal_post_process_fun': None,
                    'goal_slot_relax_fun': None,
                    },
                    {'fixed_slots':[('task','weather'),],
                    'changeable_slots':['city', 'state'],
                    'one_of_slot_set':[],
                    'sys_unaskable_slots':[],
                    'default_slots_values':[],
                    'active_prob':0.0,
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

            'status_included': ['correct', 'incorect', 'unmentioned'],#'pending', 'filled', 'all'],# only for imagining
            'slot_value_from':['goal', 'sys_da'],#only for imagining
            'slot_from': ['sys_da', 'none', 'goal'],
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
                    'use_slot_sequence': True,
                },
                'oog':{
                    'slot_included': False,
                    'value_included': False,
                    'act_without_slot': True,
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
                },
                'ack':{
                    'slot_included': False,
                    'value_included': False,
                },
                'thankyou':{
                    'slot_included': False,
                    'value_included': False,
                    'act_without_slot': True,
                },
               'silence':{
                    'slot_included': False,
                    'value_included': False,
                    'act_without_slot': True,
                },
               'reqalts':{
                    'slot_included': True,
                    'value_included': True,
                    'combineable_slots': ['alternative'],
                    'slot_from': 'none',
                    'value_from': 'function',
                    'value_fun': alternative_value_fun,
                },
                'negate':{
                    'slot_included': False,
                    'value_included': False,
                    'slot_from': 'sys_da',
                    'status_included': 'incorrect',
                },
                'bye':{
                    'slot_included': False,
                    'value_included': False,
                    'act_without_slot': True,
                },
                'hello':{
                    'slot_included': False,
                    'value_included': False,
                    'act_without_slot': True,
                    #'add_to_da_prob':0.5,
                },
                'restart':{#TODO how to user this action?
                    'slot_included': False,
                    'value_included': False,
                },
                'hangup':{
                    'slot_included': False,
                    'value_included': False,
                    'act_without_slot': True,
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
                            'inform_overridden_properties':{
                                'use_slot_sequence': True,
                            },
                            'active_prob':0.9,
                        },
                        {'return_acts':['silence'],
                            'active_prob':0.05,
                        },
                        {'return_acts':['oog'],
                            'active_prob':0.05,
                        },
                 ],
                'confirm':[{#explict confirm
                            #only one action in the set or specify explicitly the apply order and stop when first appliable
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
                                        'active_prob':0.4,
                                        'inform_answer_types':{
                                            'direct_answer':1.0,
                                        },
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                    },
                                    'case2':{'return_acts':['deny'],
                                        'active_prob':0.2,
                                    },
                                    'case3':{'return_acts':['deny', 'inform'],
                                        'active_prob':0.4,
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                    },
                                }#end of seond priority answer
                            ],
                            'active_prob':1.0
                        },#end of the firs way of answer
                ],
                'implconfirm':[{'active_prob': 1.0,
                         'ordered_return_acts':[
                            {   'case1':{'return_acts':['affirm'],
                                    'active_prob':1.0,
                                    'affirm_overridden_properties':{
                                        'add_to_da_prob':0.5,
                                    }
                                },#end of first way in the firs priority answer
                            },#end of first priority answer
                            {   'case1':{'return_acts':['negate', 'inform'],
                                        'active_prob':0.7,
                                        'inform_answer_types':{
                                            'direct_answer':1.0,
                                        },
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                },
                                'case2':{'return_acts':['deny', 'inform'],
                                        'active_prob':0.3,
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                },
                            }#end of seond priority answer
                         ],
                        },#end of the first way of answer
                ],

               'iconfirm':[{'active_prob': 1.0,
                         'ordered_return_acts':[
                            {   'case1':{'return_acts':['affirm'],
                                    'active_prob':1.0,
                                    'affirm_overridden_properties':{
                                        'add_to_da_prob':0.5,
                                    }
                                },#end of first way in the firs priority answer
                            },#end of first priority answer
                            {   'case1':{'return_acts':['negate', 'inform'],
                                        'active_prob':0.7,
                                        'inform_answer_types':{
                                            'direct_answer':1.0,
                                        },
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                },
                                'case2':{'return_acts':['deny', 'inform'],
                                        'active_prob':0.3,
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                },
                            }#end of seond priority answer
                         ],
                        },#end of the first way of answer
                ], 

                'inform_Not_used':[{'active_prob': 1.0,
                         'ordered_return_acts':[
                            {   'case1':{'return_acts':['affirm'],
                                    'active_prob':1.0,
                                    'affirm_overridden_properties':{
                                        'add_to_da_prob':0.5,
                                    }
                                },#end of first way in the firs priority answer
                            },#end of first priority answer
                            {   'case1':{'return_acts':['negate', 'inform'],
                                        'active_prob':0.7,
                                        'inform_answer_types':{
                                            'direct_answer':1.0,
                                        },
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                },
                                'case2':{'return_acts':['deny', 'inform'],
                                        'active_prob':0.3,
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                },
                            }#end of seond priority answer
                         ],
                        },#end of the first way of answer
                ],
               'apology':[{'return_acts':[],
                            'active_prob':1.0,
                        },
                ],
                'silence':[{'return_acts':['silence'],
                            'active_prob':1.0
                        },
                ],
                'hello':[{'return_acts':['hello'],
                        'active_prob':0.3,
                        },
                        {'return_acts':['hello', 'inform'],
                        'active_prob':0.7,
                        'inform_answer_types':{
                                'over_answer': 0.8,
                                'complete_answer': 0.2,
                            },
                        'inform_overridden_properties':{
                                'slot_from': 'none',
                                'atleast_slots': ['task'],
                            },
                        'hello_overridden_properties':{
                                'add_to_da_prob':0.5,
                            }
                        },
                ],
                'offer':{
                    0:[{'active_prob':1.0,
                         'ordered_return_acts':[
                            {   'case1':{'return_acts':['inform'],
                                        'active_prob':1.0,
                                        'affirm_overridden_properties':{
                                            'add_to_da_prob': 0.0,
                                        },
                                        'inform_overridden_properties':{
                                            'slot_from': 'goal',
                                            'status_included': 'unmentioned',    
                                        },
                                },
                            },
                            {   'case1':{'return_acts':['affirm', 'bye'],
                                    'active_prob':0.2,
                                    'affirm_overridden_properties':{
                                        'add_to_da_prob':0.0,
                                    },
                                },#end of first way in the firs priority answer
                                'case2':{'return_acts':['affirm', 'thankyou'],
                                    'active_prob':0.4,
                                    'affirm_overridden_properties':{
                                        'add_to_da_prob':0.0,
                                    },
                                },#end of second way in the firs priority answer
                                 'case3':{'return_acts':['affirm', 'request'],
                                    'active_prob':0.2,
                                    'affirm_overridden_properties':{
                                        'add_to_da_prob':0.0,
                                    },
                                },#end of third way in the firs priority answer
                                'case4':{'return_acts':['affirm', 'reqalts'],
                                    'active_prob':0.2,
                                    'affirm_overridden_properties':{
                                        'add_to_da_prob':0.0,
                                    },
                                },#end of fourth way in the firs priority answer
                            },#end of first priority answer
                            {   'case1':{'return_acts':['negate', 'inform'],
                                        'active_prob':0.7,
                                        'inform_answer_types':{
                                            'direct_answer':1.0,
                                        },
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                },
                                'case2':{'return_acts':['deny', 'inform'],
                                        'active_prob':0.3,
                                        'inform_overridden_properties':{
                                            'slot_from': 'sys_da',
                                            'status_included': 'incorrect',
                                            'value_from': 'goal',
                                            'use_slot_sequence': True,
                                        },
                                },
                            }#end of seond priority answer
                         ],#end of the list of ordered answer
                        },#end of first way of anser
                    ],
                    1:[{'return_acts':['bye'],
                        'active_prob':0.5,
                        },
                        {'return_acts':['thankyou'],
                        'active_prob':0.5,
                        },
                    ],
                    2:[{'return_acts':['bye'],
                        'active_prob':0.5,
                        },
                        {'return_acts':['thankyou'],
                        'active_prob':0.5,
                        },
                    ],
                },
                'offer_old_unconditional':{
                    0:[{'return_acts':['bye'],#definition for goal_id=0
                        'active_prob':0.2,
                        },
                        {'return_acts':['request'],
                        'active_prob':0.2,
                        },
                        {'return_acts':['reqalts'],
                        'active_prob':0.2,
                        },
                        {'return_acts':['thankyou'],
                        'active_prob':0.4,
                        },
                    ],
                    1:[{'return_acts':['bye'],
                        'active_prob':0.5,
                        },
                        {'return_acts':['thankyou'],
                        'active_prob':0.5,
                        },
                    ],
                    2:[{'return_acts':['bye'],
                        'active_prob':0.5,
                        },
                        {'return_acts':['thankyou'],
                        'active_prob':0.5,
                        },
                    ],
                },
                'bye':[{'return_acts':['hangup'],
                        'active_prob':1.0,
                    }
                ],
            },
            'data_observation_probability':{
                'time_relative':{
                    ('now',):1.0,#key is row in the table, if table has only one field, need add comma before the end of the tuple
                },
                'time_relative_full_thanh':{
                    ('as soon as possible',):0.2,#key is row in the table, if table has only one field, need add comma before the end of the tuple
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
            },
        },#end of metatdata
        },#end of SimpleUserSimulator
    },#end of user_simulator
}#end of config
