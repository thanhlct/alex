.. image:: /../../../../alex/doc/alex-logo.png
    :alt: Alex logo

Domain independent user simulator for slot-filling spoken dialogue systems
=================================================

..  image:: https://travis-ci.org/UFAL-DSG/alex.png
    :target: https://travis-ci.org/UFAL-DSG/alex

.. image:: https://readthedocs.org/projects/alex/badge/?version=latest&style=travis
    :target: https://readthedocs.org/projects/alex/?badge=latest
    :alt: Documentation Status

.. image:: https://landscape.io/github/UFAL-DSG/alex/master/landscape.png
   :target: https://landscape.io/github/UFAL-DSG/alex/master
   :alt: Code Health

Description
-----------------
This module is intended to provide different user simulators which may play the role of users on testing and training spoken dialogue systems (SDS).
For current, this module contains only a ``SimpleUserSimulator`` working on dialogue act or semantic level. Thereforce, the document was mostly used to describe the user simulator, defining a domain, how it will be used.

Overview
-----------------
The core of user simulator is working based on a data provider and a metadata describing domain and the behaviour of users.
The data provider, roughly speaking, is a bridge helping the simulator accessing domain data-the values for slots. The interface of data provider is enclosed in this framework. An simple implementation of the provider working with text files named PythonDatabase is also included.
The metadata is a python dict encapsulate all domain specification which will be presented in details in next sections.

Addation to the code, this module is also distributing two examples of using the user simulator. One is quite trivial, appointment scheduling, where user only decides accept, delay or reject an appoinment. Another examples is the user simulator for a public transport information system, where user manage many slots (e.g. where and when to leave, destination etc.) and answer more various system acts (e.g. request, confirm, offer etc.). A short description of these examples is provided at the end of this document.

Metadata
-----------------
Apart from domain data, defining a metadata configuring the user simulator is the only thing you need to do for deloying a user simulating conversations withyour SDS.

A domain metadata may includes the following sections (each section is a key in the python dict):

- ``goals``: A list of final goal description which the user may have. :ref:`goals`
- ``slot_table_field_mapping``: A dict mapping each slot to its data sources.
- ``same_table_slot``: A dict specifying slots which must be fetched data from the same row in the same table.
- ``dialogue_act_definitions``: A dict definiing all acts which user may uses and how to build them.
- ``reply_system_acts``: A dict defining how to answer a system act.
- ``data_observation_probability``: A dict presenting the data occurring distribution.

.. _goals:

goals
-----------------
You can define multiple final goals as much as you want. The set of goals is presetned by a list of dict, in which each goal is a dict. Inside a goal definition, we may have the following sections:

- ``fixed_slots``: A list of tuples with two string elements, slot name and slot value.
- ``changeable_slots``: A list of strings including all slots which has value can be changed.
- ``one_of_slot_set``: A list of dict, each dict presents several sets of slots which are exclusively eliminating each other. In other words, only one of these sets will be active at a specific time.
- ``equivalent_slot``: A list of tuples with elementis are slots which are equivalent in meaning.
- ``sys_unaskable_slots``: A list of strings, listing all slots which system is not allowed to task users.
- ``default_slots_values``: A list of tuples with two elements, slot name and its default value.
- ``active_prob``: A real number in range of [0, 1] preseting the probability of this goal will be activating.
- ``same_table_slot_keys``: A list of string listing keys/definitions in the ``same_table_slot`` section which will be used in this goal.
- ``goal_post_process_fun``: A function doing post process for the goal, which mean after this goal being sampled the function will be called to guarantee all combination of slots and values are fit in together.
- ``goal_slot_relax_fun``: A function relaxing a slot value when get a requiremnt from system. *Not coded yet :), but this feature may be encoded in act definition*
- ``reward_last_da_fun``: A function rewarding the last system act.
- ``reward_final_goal_fun``: A function providing the final reward after a dialouge finished.
- ``end_dialogue_post_process_fun``: A function will be called after a dialogue completed.
- ``slot_used_sequence``: A dict defining a sequence of slots will be used. For examples, slots at higher level can not be informed when there is no any slots at lower level have been used in previous turns.

The following is an example including two goal, one is finding connection between two places and another is ask the weather of a city.

::
    
    metadata = {
        'goals': [
                    #the first goal finding route
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
                    'active_prob':0.8,#probability of observing the task being active
                    'same_table_slot_keys':[],#defining when serveral slots connected to a row in a table and we would like to get them linked together
                    'goal_post_process_fun': None,#post process function to refine the sampled goal, which will be defined for specific semantic relations
                    'goal_slot_relax_fun': None,#support function, relax the value of a slot given curretn goal, e.g. more late arrival, departure sooner
                    'reward_last_da_fun': None,
                    'reward_final_goal_fun': None,
                    'end_dialogue_post_process_fun': None,
                    'slot_used_sequence':{#higher level is only able to used when one of slot at previous level used
                        0:('task',),
                        1:('from_stop', 'from_city', 'from_street', 'to_stop', 'to_city', 'to_street'),
                        2:('departure_time', 'arrival_time', 'departure_tiem_rel', 'arrival_time_rel', 'vehicle'),
                        #only need one of slot in each level informed to get next level
                        },
                    },
                    
                    #The second goal, asking weather of a city
                    {'fixed_slots':[('task','weather'),],
                    'changeable_slots':['city', 'state'],
                    'one_of_slot_set':[],
                    'sys_unaskable_slots':[],
                    'default_slots_values':[],
                    'active_prob':0.2,
                    'same_table_slot_keys':['place'],
                    'goal_post_process_fun': None,
                    'goal_slot_relax_fun': None,
                    },
                ],
    }

slot_table_field_mapping
-----------------

same_table_slot
-----------------
abc

dialogue_act_definitions
-----------------
abc

reply_system_acts
-----------------
abc

data_observation)probability
-----------------
abc

License
-------
This code is released under the APACHE 2.0 license unless the code says otherwise and its license does not allow re-licensing.
The full wording of the APACHE 2.0 license can be found in the LICENSE-APACHE-2.0.TXT.

Contacts
---------------
*thanhlct@gmail.com*
