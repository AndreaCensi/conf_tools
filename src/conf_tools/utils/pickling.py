from io import StringIO
import pickle


def can_be_pickled(x):
    """ Returns True if the object can be pickled. """
    try:
        s = StringIO() 
        pickle.dump(x, s)   
        return True
    except:
        return False
