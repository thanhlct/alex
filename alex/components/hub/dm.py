#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import multiprocessing
import select
import time
import random
import urllib2
import json
from collections import deque
import ssl

from alex.components.slu.da import DialogueAct, DialogueActItem, DialogueActConfusionNetwork
from alex.components.hub.messages import Command, SLUHyp, DMDA
from alex.components.dm.common import dm_factory, get_dm_type
from alex.components.dm.exceptions import DMException
from alex.utils.procname import set_proc_name


class DM(multiprocessing.Process):
    """DM accepts N-best list hypothesis or a confusion network generated by an SLU component.
    The result of this component is an output dialogue act.

    When the component receives an SLU hypothesis then it immediately responds with an dialogue act.

    This component is a wrapper around multiple dialogue managers which handles multiprocessing
    communication.
    """

    def __init__(self, cfg, commands, slu_hypotheses_in, dialogue_act_out, close_event):
        multiprocessing.Process.__init__(self)

        self.cfg = cfg
        self.commands = commands
        self.slu_hypotheses_in = slu_hypotheses_in
        self.dialogue_act_out = dialogue_act_out
        self.close_event = close_event
        self.last_user_da_time = time.time()
        self.last_user_diff_time = time.time()
        self.epilogue_state = None

        dm_type = get_dm_type(cfg)
        self.dm = dm_factory(dm_type, cfg)
        self.dm.new_dialogue()

        self.codes = deque(["%04d" % i for i in range(0, 10000)])

        # random.seed(self.cfg['DM']['epilogue']['code_seed'])
        random.shuffle(self.codes)
        self.test_code_server_connection()

        #Thanh:
        self.dialogue_error=0
        self.minimum_dialogue_error=3#to get the Code
        self.num_repeat_final_question=10#maximum number of request the feedback

    def process_pending_commands(self):
        """Process all pending commands.

        Available commands:
          stop() - stop processing and exit the process
          flush() - flush input buffers.
            Now it only flushes the input connection.

        Return True if the process should terminate.
        """

        while self.commands.poll():
            command = self.commands.recv()

            if self.cfg['DM']['debug']:
                self.cfg['Logging']['system_logger'].debug(command)

            if isinstance(command, Command):
                if command.parsed['__name__'] == 'stop':
                    return True

                if command.parsed['__name__'] == 'flush':
                    # discard all data in in input buffers
                    while self.slu_hypotheses_in.poll():
                        data_in = self.slu_hypotheses_in.recv()

                    self.dm.end_dialogue()

                    self.commands.send(Command("flushed()", 'DM', 'HUB'))
                    
                    return False

                #if command.parsed['__name__'] == 'prepare_new_dialogue':
                    #self.dm.new_dialogue()

                if command.parsed['__name__'] == 'new_dialogue':
                    self.dm.new_dialogue()#thanh change???
                    self.epilogue_state = None

                    self.cfg['Logging']['session_logger'].turn("system")
                    self.dm.log_state()

                    # I should generate the first DM output
                    da = self.dm.da_out()

                    if self.cfg['DM']['debug']:
                        s = []
                        s.append("DM Output")
                        s.append("-"*60)
                        s.append(unicode(da))
                        s.append("")
                        s = '\n'.join(s)
                        self.cfg['Logging']['system_logger'].debug(s)

                    self.cfg['Logging']['session_logger'].dialogue_act("system", da)

                    self.commands.send(DMDA(da, 'DM', 'HUB'))

                    return False

                if command.parsed['__name__'] == 'end_dialogue':
                    self.dm.end_dialogue()
                    return False

                if command.parsed['__name__'] == 'timeout':
                    # check whether there is a looong silence
                    # if yes then inform the DM

                    silence_time = command.parsed['silence_time']

                    cn = DialogueActConfusionNetwork()
                    cn.add(1.0, DialogueActItem('silence','time', silence_time))

                    # process the input DA
                    self.dm.da_in(cn)

                    self.cfg['Logging']['session_logger'].turn("system")
                    self.dm.log_state()

                    print '----Time out: ', self.epilogue_state, silence_time
                    '''Thanh
                    if self.epilogue_state == 'give_code':
                        # an cant_apply act have been chosen
                        self.cfg['Logging']['session_logger'].dialogue_act("system", self.epilogue_da)
                        self.commands.send(DMDA(self.epilogue_da, 'DM', 'HUB'))
                        self.commands.send(Command('hangup()', 'DM', 'HUB'))
                        return False
                    #'''
                        
                    if self.epilogue_state and float(silence_time) > 5.0: 
                        if self.epilogue_state == 'final_question': # and self.final_question_repeated<16:
                            da = DialogueAct('say(text="{text}")'.format(text="Sorry, did you get the correct information?"))
                            #self.final_question_repeated += 1
                            self.cfg['Logging']['session_logger'].dialogue_act("system", da)
                            self.commands.send(DMDA(da, 'DM', 'HUB'))
                        else:
                            # a user was silent for too long, therefore hung up
                            self.cfg['Logging']['session_logger'].dialogue_act("system", self.epilogue_da)
                            self.commands.send(DMDA(self.epilogue_da, 'DM', 'HUB'))
                            self.commands.send(Command('hangup()', 'DM', 'HUB'))
                    else:
                        da = self.dm.da_out()
                        #if da[0].dat == 'cant_apply':

                        if self.cfg['DM']['debug']:
                            s = []
                            s.append("DM Output")
                            s.append("-"*60)
                            s.append(unicode(da))
                            s.append("")
                            s = '\n'.join(s)
                            self.cfg['Logging']['system_logger'].debug(s)

                        self.cfg['Logging']['session_logger'].dialogue_act("system", da)
                        self.commands.send(DMDA(da, 'DM', 'HUB'))

                        if da.has_dat("bye"):
                            self.commands.send(Command('hangup()', 'DM', 'HUB'))

                    return False

        return False

    def epilogue_final_question(self):
        da = DialogueAct('say(text="{text}")'.format(text=self.cfg['DM']['epilogue']['final_question']))
        self.cfg['Logging']['session_logger'].dialogue_act("system", da)
        self.commands.send(DMDA(da, 'DM', 'HUB'))

    def epilogue_final_apology(self):
        # apology for not reaching minimum number of turns
        text = self.cfg['DM']['epilogue']['final_code_text_min_turn_count_not_reached']
        da = DialogueAct('say(text="{text}")'.format(text=text))
        self.cfg['Logging']['session_logger'].dialogue_act("system", da)
        self.commands.send(DMDA(da, 'DM', 'HUB'))

    def epilogue_final_code(self):

        data = None
        attempts = 0
        url_template = self.cfg['DM']['epilogue']['final_code_url']
        system_logger = self.cfg['Logging']['system_logger']

        # store a code on the server (try several times if not successful)
        while attempts < 10 and not data or not data['response'] or data['response'] != 'success':
            code = self.codes.popleft()
            self.codes.append(code)  # put the code back to the end of the queue for reuse
            attempts += 1
            # pull the URL
            url = url_template.format(code=code, logdir=system_logger.get_session_dir_name())
            gcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            data = urllib2.urlopen(url, context=gcontext, data='').read()
            data = json.loads(data, encoding='UTF-8')

        if attempts >= 10:
            # This shouldn't happen
            text = 'I am sorry. A valid code could not be generated'
        else:
            text = [c for c in code]
            text = ", ".join(text)
            text = self.cfg['DM']['epilogue']['final_code_text'].format(code=text)
            text = [text, ] * 3
            text = self.cfg['DM']['epilogue']['final_code_text_repeat'].join(text)

        da = DialogueAct('say(text="{text}")'.format(text=text))
        self.cfg['Logging']['session_logger'].dialogue_act("system", da)
        self.commands.send(DMDA(da, 'DM', 'HUB'))

        self.final_code_given = True

    def epilogue(self):
        """ Gives the user last information before hanging up.

        :return the name of the activity or None
        """
        self.cfg['Logging']['system_logger'].info("FQ IS " + str(self.cfg['DM']['epilogue'].get('final_question')))
        #Thanh: change for  only ask final question or code, not both
        if self.epilogue_state==None and self.cfg['DM']['epilogue']['final_question']:
            self.epilogue_final_question()
            self.final_question_repeated=0
            return 'final_question'
        elif self.cfg['DM']['epilogue']['final_code_url']:
            #if self.dialogue_error<=self.minimum_dialogue_error and self.epilogue_state!='give_code' and self.dm.dialogue_state.turn_number < self.cfg['DM']['epilogue']['final_code_min_turn_count']:
            print '--Dialogue error %d, current total turn: %d'%(self.dialogue_error, self.turn_number)
            if self.dialogue_error<self.minimum_dialogue_error and self.turn_number < self.cfg['DM']['epilogue']['final_code_min_turn_count']:
                self.epilogue_final_apology()
            else:
                self.epilogue_final_code()
                self.dialogue_error=0
                '''
                if self.dialogue_error<=self.minimum_dialogue_error:
                    self.dialogue_error=0
                    self.epilogue_final_apology()
                else:
                    self.dialogue_error=0
                    self.epilogue_final_code()
                '''
            #return 'code_given'

        return None

    def set_dialogue_satisfied(self, slu_hyp):
        da = slu_hyp.get_best_nonnull_da()
        print '---user satisfied:', da[0].dat
        if da.has_dat('affirm'):
            self.dm.set_final_reward(True)
            return True
        elif da.has_dat('negate'):
            self.dm.set_final_reward(False)
            return True
        self.final_question_repeated +=1
        return False

    def cant_apply_act_handler(self):
        self.dm.set_final_reward(False)
        self.dm.end_dialogue() 
        self.dialogue_error +=1
        if self.dialogue_error<self.minimum_dialogue_error:
            print "Vao 1::", self.dialogue_error
            da = DialogueAct('say(text="{text}")'.format(text="Wow, Great, Alex has learned something very important and need to start over!"))
        else:
            print "Vao 2::", self.dialogue_error
            da = DialogueAct('say(text="{text}")&help(inform="hangup")&say(text="{text1}")'.format(text="Thanks! Alex has learned a lot from you. Now, Alex needs start over again. However,", text1='But Alex would love to learn more.'))

        self.cfg['Logging']['session_logger'].dialogue_act("system", da)
        self.commands.send(DMDA(da, 'DM', 'HUB'))
        
        self.commands.send(Command('fake_a_call()', 'DM', 'HUB'))

        '''#given code after Alex error choose wrong action
        if self.cfg['DM']['epilogue']['final_code_url']:
            self.epilogue_state ='give_code'
            self.epilogue_state = self.epilogue()
            #self.epilogue_state ='final_question'

        self.epilogue_da = DialogueAct('bye()')
        self.cfg['Logging']['session_logger'].dialogue_act("system", self.epilogue_da)
        self.commands.send(DMDA(self.epilogue_da, 'DM', 'HUB'))
        self.commands.send(Command('hangup()', 'DM', 'HUB'))
        '''
    
    def _ask_feedback_again(self):
        da = DialogueAct('say(text="Please answer clearly ,Yes I did, if you got the correct information, otherwise say, No I didn\'t")')
        self.cfg['Logging']['session_logger'].dialogue_act("system", da)
        self.commands.send(DMDA(da, 'DM', 'HUB'))

    def read_slu_hypotheses_write_dialogue_act(self):
        # read SLU hypothesis
        if self.slu_hypotheses_in.poll():
            # read SLU hypothesis
            data_slu = self.slu_hypotheses_in.recv()

            #change for get bot yest no sattifiys and code
            if self.epilogue_state=='final_question' and self.cfg['DM']['epilogue']['final_code_url']==None:#Thanh: only ask final question, not code
                # we have got another turn, now we can hang up.
                if self.set_dialogue_satisfied(data_slu.hyp) or self.final_question_repeated>=self.num_repeat_final_question:#update final reward for gp-sarsa, if get affirm or negate
                    self.cfg['Logging']['session_logger'].turn("system")
                    self.dm.log_state()
                    self.cfg['Logging']['session_logger'].dialogue_act("system", self.epilogue_da)
                    self.commands.send(DMDA(self.epilogue_da, 'DM', 'HUB'))
                    self.commands.send(Command('hangup()', 'DM', 'HUB'))
                else:
                    self._ask_feedback_again()
                    
            elif self.epilogue_state=='final_question' and self.cfg['DM']['epilogue']['final_code_url']:
                if self.set_dialogue_satisfied(data_slu.hyp) or self.final_question_repeated>=self.num_repeat_final_question:#:#update final rewar for gp-sarsa
                    self.epilogue_state = self.epilogue()
                    if not self.epilogue_state:
                        self.cfg['Logging']['session_logger'].dialogue_act("system", self.epilogue_da)
                        self.commands.send(DMDA(self.epilogue_da, 'DM', 'HUB'))
                        self.commands.send(Command('hangup()', 'DM', 'HUB'))
                else:
                    self._ask_feedback_again()
            elif isinstance(data_slu, SLUHyp):
                # reset measuring of the user silence
                self.last_user_da_time = time.time()
                self.last_user_diff_time = time.time()

                # process the input DA
                self.dm.da_in(data_slu.hyp, utterance=data_slu.asr_hyp)

                self.cfg['Logging']['session_logger'].turn("system")
                self.dm.log_state()

                da = self.dm.da_out()
                if da[0].dat == 'cant_apply':
                    self.cant_apply_act_handler()    
                    return

                # do not communicate directly with the NLG, let the HUB decide
                # to do work. The generation of the output must by synchronised with the input.
                if da.has_dat("bye"):
                    self.turn_number = self.dm.dialogue_state.turn_number
                    self.epilogue_state = self.epilogue()
                    self.epilogue_da = da

                    if not self.epilogue_state:
                        self.cfg['Logging']['session_logger'].dialogue_act("system", da)
                        self.commands.send(DMDA(da, 'DM', 'HUB'))
                        self.commands.send(Command('hangup()', 'DM', 'HUB'))
                else:
                    if self.cfg['DM']['debug']:
                        s = []
                        s.append("DM Output")
                        s.append("-"*60)
                        s.append(unicode(da))
                        s.append("")
                        s = '\n'.join(s)
                        self.cfg['Logging']['system_logger'].debug(s)

                    self.cfg['Logging']['session_logger'].dialogue_act("system", da)
                    self.commands.send(DMDA(da, 'DM', 'HUB'))


            elif isinstance(data_slu, Command):
                self.cfg['Logging']['system_logger'].info(data_slu)
            else:
                raise DMException('Unsupported input.')

    def run(self):
        try:
            set_proc_name("Alex_DM")
            self.cfg['Logging']['session_logger'].cancel_join_thread()

            while 1:
                # Check the close event.
                if self.close_event.is_set():
                    print 'Received close event in: %s' % multiprocessing.current_process().name
                    return

                select.select([self.commands, self.slu_hypotheses_in], [], [], 1)

                s = (time.time(), time.clock())

                # process all pending commands
                if self.process_pending_commands():
                    return

                # process the incoming SLU hypothesis
                self.read_slu_hypotheses_write_dialogue_act()

                # Print out the execution time if it took longer than the threshold.
                d = (time.time() - s[0], time.clock() - s[1])
                if d[0] > 0.200:
                    print "EXEC Time inner loop: DM t = {t:0.4f} c = {c:0.4f}\n".format(t=d[0], c=d[1])

        except KeyboardInterrupt:
            print 'KeyboardInterrupt exception in: %s' % multiprocessing.current_process().name
            self.close_event.set()
            return
        except:
            self.cfg['Logging']['system_logger'].exception('Uncaught exception in the DM process.')
            self.close_event.set()
            raise

        print 'Exiting: %s. Setting close event' % multiprocessing.current_process().name
        self.close_event.set()

    def test_code_server_connection(self):
        """ this opens a test connection to our code server, content of the response is not important
            if our server is down this call will fail and the VM will crash. this is more sensible to CF people,
            otherwise CF contributor would do the job without getting paid.
        """
        #if self.cfg['DM']['epilogue']['final_question'] is None and self.cfg['DM']['epilogue']['final_code_url'] is not None:
        if self.cfg['DM']['epilogue']['final_code_url'] is not None:
            url = self.cfg['DM']['epilogue']['final_code_url'].format(code='test', logdir='')
            gcontext = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
            urllib2.urlopen(url, context=gcontext, data='')
