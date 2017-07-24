import numpy as np


class Base_Env(object):
    """
    the main energy_py environment class
    inspired by the gym.Env class

    The methods of this class are:
        step
        reset

    To implement an environment:
    1 - override the following methods in your child:
        _step
        _reset

    2 - set the following attributes
        action_space
        observation_space
        reward_range (defaults to -inf, +inf)
    """

    # Override in ALL subclasses
    def _step(self, action): raise NotImplementedError
    def _reset(self): raise NotImplementedError

    # Set these in ALL subclasses
    action_space = None
    observation_space = None
    reward_range = (-np.inf, np.inf)

    def step(self, action):
        """
        Run one timestep of the environment's dynamics. When end of
        episode is reached, you are responsible for calling `reset()`
        to reset this environment's state.

        Accepts an action and returns a tuple (observation, reward, done, info).

        Args:
            action (object): an action provided by the environment

        Returns:
            observation (np array): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (boolean): whether the episode has ended, in which case further step() calls will return undefined results
            info (dict): contains auxiliary diagnostic information (helpful for debugging, and sometimes learning)
        """
        return self._step(action)

    def reset(self):
        """
        Resets the state of the environment and returns an initial observation.

        Returns: observation (np array): the initial observation
        """
        return self._reset()

class Space(object):
    """
    The base class for observation & action spaces

    Analagous to the 'Space' object used in gym

    """

    def sample(self):
        """
        Uniformly randomly sample a random element of this space
        """
        return self._sample()

    def contains(self, x):
        """
        Return boolean specifying if x is a valid
        member of this space
        """
        return self._contains(x)


class Discrete_Space(Space):
    """
    A single dimension discrete space

    Args:
        low  (float): an array with the minimum bound for each
        high (float): an array with the maximum bound for each
        step (float): an array with step size
    """

    def __init__(self, low, high, step, current=None):
        self.current = current
        self.low = low
        self.high = high
        self.step = step
        self.discrete_space = np.arange(low, high + step, step).reshape(- 1)

    def _sample(self):
        return np.random.choice(self.discrete_space)

    def _contains(self, x):
        return np.in1d(x, self.discrete_space)


class Continuous_Space(Space):
    """
    A single dimension continuous space

    Args:
        low  (float): an array with the minimum bound for each
        high (float): an array with the maximum bound for each
    """

    def __init__(self, low, high, current=None):
        self.current = current
        self.low = low
        self.high = high

    def _sample(self):
        return np.random.uniform(low=self.low, high=self.high)

    def _contains(self, x):
        return (x >= self.low) and (x <= self.high)

if __name__ == '__main__':


    space = Continuous_Space(low=0, high=20)
    # print(space.space)
    print(space.sample())
    print(space.contains(2))
    print(space.contains(1.2))
    print(space.contains(100))