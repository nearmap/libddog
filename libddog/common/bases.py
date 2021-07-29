from typing import Any, Dict


class Renderable:
    def as_dict(self) -> Dict[str, Any]:
        raise NotImplementedError
