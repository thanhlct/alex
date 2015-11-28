.. image:: ../../../../alex/doc/alex-logo.png
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
For current, this module contains only a SimpleUserSimulator working on dialogue act or semantic level. Thereforce, the document was mostly used to describe the user simulator, defining a domain, how it will be used.

Overview
-----------------
The core of user simulator is working based on a data provider and a metadata describing domain and the behaviour of users.
The data provider, roughly speaking, is a bridge helping the simulator accessing domain data-the values for slots. The interface of data provider is enclosed in this framework. An simple implementation of the provider working with text files named PythonDatabase is also included.
The metadata is a python dict encapsulate all domain specification which will be presented in details in next sections.

Addation to the code, this module is also distributing two examples of using the user simulator. One is quite trivial, appointment scheduling, where user only decides accept, delay or reject an appoinment. Another examples is the user simulator for a public transport information system, where user manage many slots (e.g. where and when to leave, destination etc.) and answer more various system acts (e.g. request, confirm, offer etc.). A short description of these examples is shown at the end of this document.

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
abc

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
