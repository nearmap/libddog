# Maintainer guide


## Steps to release a new version

Doc updates:

1. Update [CHANGELOG](CHANGELOG.md).

Performing a release:

1. Bump version in `libddog/__init__.py`.
2. Git tag the new version: `git tag -a <version> -m <version>`
3. Push the new tag: `git push --tags`
4. Make sure there are no lingering distributions: `rm -rf dist/`
5. Create a source distribution: `python setup.py sdist`
6. Create a binary distribution: `python setup.py bdist_wheel`
7. Push the distributions to PyPi: `twine upload dist/* -u <username> -p <password>`