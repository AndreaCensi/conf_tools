import pickle
from io import BytesIO

def can_be_pickled(x):
    """ Returns True if the object can be pickled. """
    try:
        s = BytesIO() 
        pickle.dump(x, s)   
        return True
    except:
        return False
