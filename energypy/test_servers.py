import ray
from energypy.servers import ParameterServer, TransitionServer

ray.init()

ps = ParameterServer.remote(0)
ts = TransitionServer.remote()

for step in range(10):
    ps.update_params.remote(step)
    print(ray.get(ps.get_params.remote()))

    ts.add_object_id.remote([10])
    print(ray.get(ts.get_object_ids.remote()))

