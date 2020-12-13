tesla battery
epl blog posts
eenrgy py gym envs should inherit from the gym env - not use env.env!
testing of reinforcment learning codebases - energypy, using of agent and env stubs
agent.collect_policy(), agent.greedy_policy, agent.policy.greedy()
add confidence itnerval calc for rewards
reward space!!

Interface refactor
tf 2.0

charge is not being scaled beofre being addedinto the observation

use callbacks to change the training loop
- https://youtu.be/1TfI88uQNj8?t=2104

---

aux loss

3.0
- PPO
- CMA-ES

parallel by default
- ray

hardcode in the aussie data (domnload link)


---

## rethinking energy py

rebuild in ray
- parallelization from day one

off policy, continuous action space

MDP in the gym style

repo where I learnt to code

who is the target audiencce

not all the RL algos
- the value of the library is choosing which to support
- why we choose PPO

more than RL?
- anything in the MDP framework

not implementing from scratch as default
- first use someone elses

all the envs
- plus the data to run them!

goal = battery + chp

env model learning

rethink notes

---

# API driven development

## Setup

```bash
pip install energypy
```

## Usage

To train an agent:

```bash
energypy train
	--agent random
	--env battery
	--cpu 4
```

To test an agent:

```bash
energypy test
	--agent ppo
	--env battery
