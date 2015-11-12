from alex.components.simulator.base import UserSimulator

class SimpleUserSimulator(UserSimulator):
    '''Simple user simulator'''
    def __init__(self):
        '''Initilise'''
        pass
    def new_dialogue(self):
        '''Start a new dialogue
        Sample a new user goal. Reset everything for simulating a new dialogue
        '''
        pass
    def da_in(self, da):
        '''Recieve a system dialogue act'''
        pass

    def da_out(self):
        '''Samples and returns a user dialogue act based on user's current state and given system dialogue act'''
        pass
    def reward_last_da(self):
        '''Rewards the last system dialgoue act'''
        pass
    def reward_final_goal(self):
        '''Return final reward for the current dialouge'''
        pass
    def end_dialogue(self):
        '''end dialgoue and post-processing'''
        pass
