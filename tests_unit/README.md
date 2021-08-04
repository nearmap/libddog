# Guidelines for tests


## Imports

Imports from `libddog` should be at most two levels deep and should rely on the
convenience exports via `__all__`.

In other words, do this:

```python
from libddog.dashboards import Request
```

Instead of this:

```python
from libddog.dashboards.components import Request
```

This is in line with the API policy that we may wish to reorganize code over
time without breaking the published API.