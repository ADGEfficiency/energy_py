import ray


@ray.remote
class TransitionServer:
    def __init__(self):
        self.object_ids = []

    def get_object_ids(self):
        return self.object_ids

    def add_object_ids(self, new):
        self.object_ids.extend(new)


@ray.remote
class ParameterServer:
    def __init__(self, params):
        self.params = params

    def get_params(self):
        return self.params

    def update_params(self, new):
        self.params = new
