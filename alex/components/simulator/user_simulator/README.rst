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

- **goals**: A list of final goal description which the user may have. :ref:`goals-12`
- ``slot_table_field_mapping``: A dict mapping each slot to its data sources.
- same_table_slot: A dict specifying slots which must be fetched data from the same row in the same table.
- dialogue_act_definitions: A dict definiing all acts which user may uses and how to build them.
- reply_system_acts: A dict defining how to answer a system act.
- data_observation_probabilitygoals : A dict presenting the data occurring distribution.

.. _goal-12:
goals
-----------------
abc

.. _slot-table-field-mapping:
slot_table_field_mapping:
-------



The Alex Dialogue Systems Framework is named after `the famous parrot Alex <http://en.wikipedia.org/wiki/Alex_(parrot)>`_.

This framework is being developed by the dialogue systems group at UFAL - http://ufal.mff.cuni.cz/ -
the Institute of Formal and Applied Linguistics, Faculty of Mathematics and Physics, Charles University in Prague,
Czech Republic. The purpose of this work is to facilitate research into and development of spoken dialogue systems.


Implemented features:

- VOIP using ``PJSIP 2.1`` with some modifications
- example dialogue domains:

  - PTIcs: :doc:`alex.applications.PublicTransportInfoCS.README`
  - PTIen: :doc:`alex.applications.PublicTransportInfoEN.README`


Coding style
------------
This project follows the coding convention defined in PEP8. However, do not
automatically reformat the length of the lines. The *right* length of a line
is for every person different!

Development process
-------------------
Anyone can contribute to the project as long as he or she agrees to publish the contributions under the APACHE 2.0
license.

If you are a core member of the development team, please do not make changes directly in the master branch. Please,
make a topic branch and when you believe that your changes are completed and properly tested, update your branch from
master, and again *re-test the code*. Testing involves:

- evaluating the projects unittest using nose
- testing all interactive tests in the ``alex/test`` directory
- testing that the example dialogue domains are working properly. E.g.

  - running PTIcs: :doc:`alex.applications.PublicTransportInfoCS.README`
  - running RAMcs: :doc:`alex.applications.RepeatAfterMe.README`

If you are **not** a core member of the development team, please **fork** the project. Then make a topic branch make all
changes in the topic branch. Then follow the instructions above, that is:

- evaluate unit and interactive tests, test the implemented domains that they still work with your changes
- then merge any changes upstream in the master master branch
- again do the evaluation and testing
- if everything is ok, send us a pull request.

Documentation
-------------
The documentation is available `here <http://alex.readthedocs.org/en/latest/>`_ and is 
automatically generated after each push on readthedocs.org using Sphinx and its ``autodoc`` 
extension. Please document all your code as much as possible using the conventions which can 
be parsed by Sphinx. 

Also provide README style documentation describing the complete packages, applications, 
or preparation of data and models. The documentation should be placed near the code 
and/or application to which it is the most relevant. 
For formatting the text, use reStructured (reSt) *wiki like* syntax. 
The advantage of reSt is that it is fairly readable in source format 
and it can be nicely rendered into HTML or PDF using Sphinx. 
Documents with the ``rst`` extension are automatically detected, 
included into the documentation, and an index page for these documents is created.

Each document should start with a every descriptive title, e.g.:

::

  Description of building domain specific language model for the PTI domain
  =========================================================================

Then the text should be sectioned further, e.g.:

::

  Introduction
  ------------

  Evaluation
  -----------

  Notes
  -----

More information on  how to write documentation is available at

- `Quick cheatsheet for ReST and Sphinx <http://matplotlib.org/sampledoc/cheatsheet.html>`_
- `More thorough documentation with code examples <http://packages.python.org/an_example_pypi_project/sphinx.html>`_
- The docstrings should follow google (or sphinx or numpy) style. See examples: 
    - http://sphinxcontrib-napoleon.readthedocs.org/en/latest/#google-vs-numpy
    - http://sphinxcontrib-napoleon.readthedocs.org/en/latest/example_google.html#example-google


To compile and see the documentation, you can:

.. code-block:: bash

  $ cd doc
  $ make html

The open in your browser file ``doc/_build/html/index.html``.

If you need to completely rebuild the documentation, then run:

.. code-block:: bash

  $ make clean
  $ make html

You can build also a PDF file using the ``make latexpdf`` command.

License
-------
This code is released under the APACHE 2.0 license unless the code says otherwise and its license does not allow re-licensing.
The full wording of the APACHE 2.0 license can be found in the LICENSE-APACHE-2.0.TXT.

List of contributors
--------------------
If you contributed to this project, you are encouraged to add yourself here ;-)

- Filip Jurcicek
- Jan Hajic jr.
- Lukas Zilka
- Ondrej Dusek
- Matej Korvas
- David Marek
- Ondrej Platek
