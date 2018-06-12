"""
The base class for energy_py environments
"""
import collections
import logging

import numpy as np
import pandas as pd

import energy_py
from energy_py.common.spaces import ContinuousSpace, DiscreteSpace, GlobalSpace
from energy_py.common.utils import load_csv


logger = logging.getLogger(__name__)


class BaseEnv(object):
    """
    The base environment class for time series environments

    args
        dataset (str) located in energy_py/experiments/datasets
        episode_sample (str) fixed, random

    Most energy problems are time series problems
    The BaseEnv has functionality for working with time series data
    """
    def __init__(self,
                 dataset='example',
                 episode_sample='fixed',
                 episode_length=2016):

        logger.info('Initializing environment {}'.format(repr(self)))

        #  load the time series info from csv
        self.state_ts, self.observation_ts = self.load_dataset(dataset)

        self.episode_sample = episode_sample

        self.episode_length = min(int(episode_length), self.state_ts.shape[0])

        assert self.episode_length <= self.state_ts.shape[0]

    def _step(self, action): raise NotImplementedError

    def _reset(self): raise NotImplementedError

    def reset(self):
        """
        Resets the state of the environment and returns an initial observation

        returns
            observation (np array) initial observation
        """
        logger.debug('Resetting environment')

        self.info = collections.defaultdict(list)
        self.outputs = collections.defaultdict(list)

        self.state_ep, self.observation_ep = self.get_episode()

        logger.debug(
            'Episode start {} Episode end {}'.format(
                self.state_ep.index[0], self.state_ep.index[-1])
        )

        return self._reset()

    def step(self, action):
        """
        Run one timestep of the environment's dynamics.

        args
            action (object) an action provided by the environment
            episode (int) the current episode number

        returns
            observation (np array) agent's observation of the environment
            reward (np.float)
            done (boolean)
            info (dict) auxiliary information

        User is responsible for resetting after episode end.

        The step function should progress in the following order:
        - action = a[1]
        - reward = r[1]
        - next_state = next_state[1]
        - update_info()
        - step += 1
        - self.state = next_state[1]

        step() returns the observation - not the state!
        """
        action = np.array(action).reshape(1, *self.action_space.shape)

        logger.debug('step {} action {}'.format(self.steps, action))

        return self._step(action)

    def update_info(self, **kwargs):
        """
        Helper function to update the self.info dictionary.
        """
        for name, data in kwargs.items():
            self.info[name].append(data)

        return self.info

    def load_dataset(self, dataset):
        """
        Loads time series data from csv

        args
            dataset (str)

        Datasets are located in energy_py/experiments/datasets
        A dataset consists of state.csv and observation.csv
        """
        dataset_path = energy_py.get_dataset_path(dataset)
        logger.info('Using {} dataset'.format(dataset))
        logger.debug('Dataset path {}'.format(dataset_path))

        try:
            state = load_csv(dataset_path, 'state.csv')
            observation = load_csv(dataset_path, 'observation.csv')

            assert state.shape[0] == observation.shape[0]

            #  check that the index is equally spaced on 5 min basis
            test_idx = pd.DatetimeIndex(
                start=state.index[0],
                end=state.index[-1],
                freq='5min'
            )
            assert test_idx.shape[0] == state.shape[0]

        except FileNotFoundError:
            raise FileNotFoundError(
                'state.csv & observation.csv are missing from {}'.format(
                    dataset_path)
            )

        logger.debug('State start {} \
                      State end {}'.format(state.index[0],
                                           state.index[-1]))
        return state, observation

    def make_observation_space(self, spaces, space_labels):
        """
        Pull out the column names so we know what each variable is

        args
            spaces (list) of energy_py Space objects for additional variables
            space_labels (list) labels for the additional observation vars

        returns
            observation_space (GlobalSpace) energy_py object for the obs space
        """
        self.state_info = self.state_ts.columns.tolist()
        self.observation_info = self.observation_ts.columns.tolist()

        observation_space = self.timeseries_to_spaces(self.observation_ts)

        observation_space.extend(spaces)
        self.observation_info.extend(space_labels)

        logger.debug('State info {}'.format(self.state_info))
        logger.debug('Observation info {}'.format(self.observation_info))

        return GlobalSpace(observation_space)

    def get_episode(self):
        """
        Samples a single episode from the state and observation dataframes

        returns
            observation_ep (pd.DataFrame)
            state_ep (pd.DataFrame)
        """
        max_len = self.state_ts.shape[0]
        ep_len = self.episode_length
        assert ep_len <= max_len

        if self.episode_sample == 'random':
            start = np.random.randint(low=0, high=max_len - ep_len)

        elif self.episode_sample == 'fixed':
            #  max length using episode_length = 0
            if self.episode_length == 0:
                ep_len = max_len
            else:
                ep_len = self.episode_length
            #  always get the most recent fixed length episode
            start = max_len - ep_len

        else:
            raise ValueError('episode sample of {} not supported'.format(
                self.episode_sample))

        end = start + ep_len

        logging.debug(
            'sampling episode using {}'.format(self.episode_sample)
        )
        logging.debug(
            'max_len {} start {} end {}'.format(max_len, start, end)
        )

        state_ep = self.state_ts.iloc[start:end, :]
        observation_ep = self.observation_ts.iloc[start:end, :]

        assert observation_ep.shape[0] == state_ep.shape[0]
        assert state_ep.shape[0] == ep_len

        return state_ep, observation_ep

    def timeseries_to_spaces(self, obs_ts):
        """
        Creates the observation space list

        args
            obs_ts (pd.DataFrame)

        returns
            observation_space (list) contains energy_py Space objects
        """
        observation_space = []

        for name, col in obs_ts.iteritems():
            #  pull the label from the column name
            label = str(name[:2])

            if label == 'D_':
                obs_space = DiscreteSpace(col.max())

            elif label == 'C_':
                obs_space = ContinuousSpace(col.min(), col.max())

            else:
                raise ValueError('Time series columns mislabelled')

            observation_space.append(obs_space)

        assert len(observation_space) == obs_ts.shape[1]

        return observation_space

    def get_state(self, steps, append=None):
        """
        Helper function to get a state.

        Also takes an optional argument to append onto the end of the array.

        This is so that environment specific info can be added onto the
        state array.

        Repeated code with get_observation but I think having two functions
        is cleaner when using in the child class.

        args
            steps (int) used as a row index
            append (list) optional array to append onto the state

        returns
            state (np.array)
        """
        state = np.array(self.state_ep.iloc[steps, :])

        if append:
            state = np.append(state, append)

        return state.reshape(1, len(self.state_info))

    def get_observation(self, steps, append=None):
        """
        Helper function to get a observation.

        Also takes an optional argument to append onto the end of the array.

        This is so that environment specific info can be added onto the
        observation array.

        Repeated code with get_state but I think having two functions
        is cleaner when using in the child class.

        args
            steps (int) used as a row index
            append (list) optional array to append onto the observation

        returns
            observation (np.array)
        """
        observation = np.array(self.observation_ep.iloc[steps, :])

        if append:
            observation = np.append(observation, np.array(append))

        return observation.reshape(1, *self.observation_space.shape)
