import ray
from energypy.servers import ParameterServer, TransitionServer
from energypy.workers import collect_worker
import energypy

ray.init()

ps = ParameterServer.remote(0)
ts = TransitionServer.remote()
learner = energypy.make('add-learner', 2)

n_collectors = 2

for step in range(10):
    collectors = [
        collect_worker.remote(10, ps, 'random', 'mountaincar') for _ in range(n_collectors)
    ]
    ts.add_object_ids.remote(collectors)
    t = ts.get_object_ids.remote()

    print('{} transitions'.format(len(t)))

    p = learner.learn(ps, ts)
    ps.update_params.remote(p)
    print('{} params'.format(p))
