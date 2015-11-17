'''
Support Functions similar to Matlab
'''
import numpy as np

def ismember(a, b):
    '''Return a mask of 1s for elements in a which also occurs in b'''
    return np.array([1 if v in b else 0 for v in a])

def diff(a, b):
    '''Return a mask of 1s for element in a which doesnt occur in b'''
    return np.array([1 if v not in b else 0 for v in a])
    
def find(condition):
    '''Return 1 for where condition is satisfied, otherwise 0'''
    #Require element in condtion is np.array :(
    return np.where(condition)[0]

def find_indexes(a, b):
    '''find index in b for elements in a where a is subset of b'''
    a = list(a)
    b = list(b)
    ids = []
    for val in a:
        ids.append(b.index(val))
    return ids

def sub(a, b):
    '''a - b, list subtraction'''
    return [v for v in a if v not in b] 
