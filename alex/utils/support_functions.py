import pprint
import copy

def get_dict_value(d, key):
    '''Return the value if the key exist, return none if the key doesnt exist'''
    if key in d.keys():
        return d[key]
    else:
        return None

def iscallable(o):
    '''Return True if the given object is callable'''
    if hasattr(o, '__call__'):
        return True
    return False

def iprint(s):
    pp = pprint.PrettyPrinter()
    pp.pprint(s)

def deep_copy(o):
    return copy.deepcopy(o)

def debug_print(s, mode=0, debug_mode=100):
    if mode<=debug_mode:
        print s
