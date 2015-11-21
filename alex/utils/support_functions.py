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
