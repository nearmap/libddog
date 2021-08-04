from libddog.common.types import JsonDict


class Renderable:
    def as_dict(self) -> JsonDict:
        raise NotImplementedError
