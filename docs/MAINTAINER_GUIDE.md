# Maintainer guide


## Steps to release a new version

Performing a release:

1. Bump version in `libddog/__init__.py`.
2. Update [CHANGELOG](CHANGELOG.md).
3. Git tag the new version: `git tag -a <version> -m <version>`
4. Push the new tag: `git push --tags`
5. Make sure there are no lingering distributions: `rm -rf dist/`
6. Create a source distribution: `python setup.py sdist`
7. Create a binary distribution: `python setup.py bdist_wheel`
8. Push the distributions to PyPi: `twine upload dist/* -u <username> -p <password>`

Post-release checks:

1. Run tox env to test the released version: `tox -e pypi-cli`
