import pickle
from io import BytesIO

__all__ = [
    'can_be_pickled',
]

def can_be_pickled(x):
    """ Returns True if the object can be pickled. """
    try:
        s = BytesIO() 
        pickle.dump(x, s)   
        return True
    except:
        return False
