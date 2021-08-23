# Maintainer guide


## Steps to release a new version

Performing a release:

1. Bump version in `libddog/__init__.py`.
2. Update [CHANGELOG](../CHANGELOG.md).
3. Git tag the new version: `git tag -a <version> -m <version>`
4. Push the new tag: `git push --tags`
5. Make sure there are no lingering distributions: `rm -rf dist/`
6. Create a source distribution: `python setup.py sdist`
7. Create a binary distribution: `python setup.py bdist_wheel`
8. Push the distributions to PyPi: `twine upload dist/* -u <username> -p <password>`

Post-release checks:

1. Run tox env to test the released version: `tox -e pypi-cli`

If at this point you discover that the release is broken PyPI will let you
yank/delete it and you can redo it. As long as this happens as part of the
release process, it's fair to assume that noone is using the new version yet, so
it should be okay.

By contrast, if you discover that an earlier released version is broken it's
better to yank it than to leave it up for users to stumble over. Update the
[CHANGELOG](../CHANGELOG.md) as well to document this.
