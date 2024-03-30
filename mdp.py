""" Define your MDP here

The following example is a variant of the standard machine replacement
problem, where, as the equipment gets older, the availability of knowledgeable
service personnel decays and hence the risk of a bad repair increases.
"""

from numpy import exp
from scipy.stats import beta

def number_of_states():
    """ Return the number of states in the MDP """
    return 2

def number_of_controls():
    """ Return the number of actions in the MDP 

    In the example, the two control actions are
        0 - Take a regular shot
        1 - Take a blind shot
    """
    return 2

def state_labels():
    """ Define the state labels for the states in the MDP """
    labels = {}

    labels[0] = 'Target hit'
    labels[1] = 'Target missed'

    return labels

def TProb(i, j, k, u):
    """ Define the transition probabilities of the MDP

    The arguments to the functions are
        i - From state
        j - To state
        k - Time
        u - Action
    and it should return a real in [0,1].
    """
    if u == 0:
        # Control: Take a regular shot
        T = [[0.7, 0.3],
             [0.5, 0.5]]

        return T[i][j]

    elif u == 1:
        # Control: Take a blind shot

        T = [[0.3, 0.7],
             [0, 1]]

        return T[i][j]

