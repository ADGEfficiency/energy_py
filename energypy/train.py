import json
import os
import pathlib
import time

import numpy as np
import ray

import energypy


def main(agent, env, learner, n_generations, n_collectors):
    ray.shutdown()
    ray.init()
