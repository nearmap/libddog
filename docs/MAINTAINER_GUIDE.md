# libddog maintainer guide


## Our challenge

In libddog we provide a library API that maps onto the Datadog (service) API and, indirectly, onto the Datadog UI that users see and interact with. We do not control the Datadog API, and our understanding of it will always be imperfect. It will always be limited to specific cases we have seen of dashboards and widgets exported to JSON that we can learn from. This information feeds into the assumptions we make about Datadog's internal data architecture, and our design decisions will often fall out of that. The trick is not to be *too* closely tied to Datadog's representation of metrics and widgets - giving us some wiggle room to choose the API we think is best for users, and to allow us to evolve things internally in libddog without making breaking changes - but without going as far introducing whole new abstractions that don't exist in Datadog and which could become very difficult to sustain over time.

**Our goal is provide a stable and understandable API which keeps working**, even when the Datadog API may slowly evolve over time. **Whenever possible we want to avoid breaking changes** and keep user code working.

If we deem that breaking changes are necessary **this must be reflected in the version by bumping the major version**. Instructions must also be provided in the [CHANGELOG](../CHANGELOG.md) on what code changes users need to make in order to upgrade.



## Semantic versioning

libddog is still a young project and this is the reflected in the current version being in the `0.0.x` series. At some point we will bump to `1.0.0` to reflect that it has become quite a mature project.

When making changes to the public API this must be reflected in the version:
- A bug fix or a small incremental feature (like a new kwarg added to an existing method) warrants a patch version bump: `1.2.3 -> 1.2.4`.
- A significant new feature added (like a new class or method) warrants a minor version bump: `1.2.3 -> 1.3.0`.
- A breaking change (a public API removed or changed in a backwards incompatible way) warrants a major version bump: `1.2.3 -> `2.0.0`.



## Steps to release a new version

Create a commit for the release:

1. Bump version in `libddog/__init__.py` to a final release version, eg. `0.0.2`.
2. Update [CHANGELOG](../CHANGELOG.md).
3. Create a commit: `git commit -am'bump version to <version>'`

Perform the release:

1. Git tag the new version: `git tag -a <version> -m <version>`
2. Push the new tag: `git push --tags`
3. Make sure there are no lingering distributions: `rm -rf dist/`
4. Create a source distribution: `python setup.py sdist`
5. Create a binary distribution: `python setup.py bdist_wheel`
6. Push the distributions to PyPI: `twine upload dist/* -u <username> -p <password>`

Post-release checks:

1. Run tox env to test the released version: `tox -e pypi-cli`. *Make sure the libddog version listed as installed is the version you just released.* If not rm -rf the tox env and re-run.

If at this point you discover that the release is broken PyPI will let you
yank/delete it and you can redo it. As long as this happens as part of the
release process, it's fair to assume that noone is using the new version yet, so
it should be okay.

By contrast, if you discover that an *earlier* released version is broken it's
better to yank it than to leave it up for users to stumble over. Update the
[CHANGELOG](../CHANGELOG.md) as well to document this.

Finalizing steps:

1. Bump version in `libddog/__init__.py` to an alpha release version, eg. `0.0.3a0`.
