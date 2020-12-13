import ray


class AddLearner():
    def __init__(self, step):
        self.step = step

    def learn(self, ps, ts):
        p = ray.get(ps.get_params.remote())
        return p + self.step
