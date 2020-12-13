import ray

import energypy


@ray.remote
def collect_worker(
    n_rounds,
    parameter_server,
    *args,
    **kwargs
):
    """
    Runs in parallel with other collect workers
    """
    data = []
    for _ in range(n_rounds):
        data.append(
            collect(parameter_server, *args, **kwargs)
        )

    return data


def collect(
    parameter_server,
    agent,
    env
):
    """
    Runs in sequence (in a single collect_worker)

    Gets latest parameters each time
    """
    agent = energypy.make(agent, parameter_server, env)
    env = energypy.make(env)

    obs = env.reset()
    done = False
    transitions = []
    while not done:
        action = agent.act(obs)
        next_obs, reward, done, info = env.step(action)

        transitions.append(
            {
                'observation': obs,
                'action': action,
                'reward': reward,
                'next_obs': next_obs,
                'done': done
            }
        )
        obs = next_obs

    return transitions
