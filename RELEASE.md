# Release Procedure
The basic procedure for releasing a new version of **pyFitOut** consists of:
- Running the unit tests.
- Checking the documentation
- Create a tag and update the change log
- Build and Publish the project

## Check the Unit Tests

Run the unit tests from the project top level directory:
```bash
pytest
```

## Check the Documentation

Build and check the documentation:
```bash
cd docs
make clean html
```

Load the `docs/build/html/index.html`.

## Create a Tag

**pyFitOut** uses semantic versioning. Update the version number in [pyFitOut/fitout/__init__.py](pyFitOut/fitout/__init__.py) according to changes since the previous tag.

Create a tag with the current version, e.g. `v0.0.9`.
```bash
git tag v0.0.9
```

## Update the ChangeLog

**pyFitOut** uses `auto-changelog` to parse git commit messages and generate the `CHANGELOG.md`.

```bash
auto-changelog --tag-prefix v
git add CHANGELOG.md
git commit -m "Updating CHANGELOG"
git push
git push --tags
```

## Make a GitHub Release

Go to the GitHub project administration page and [publish a release](https://github.com/kev-m/pyFitOut/releases/new) using the tag created, above.

Update the `release` branch:
```bash
git checkout release
git rebase development
git push -f
git checkout development
```

## Publishing the Package (Manual)

**NOTE:** This project is set up on GitHub for automatic publishing during the GitHub release process (above).
These instructions are for legacy purposes or manual publishing.

The library can be published using `flit` to build and publish the artifact.

**NOTE:** Ensure that PyPI configuration is set up correctly, e.g. that servers and authentication are defined in the `~/.pypirc` file.

The project details are defined in the `pyproject.toml` files. The version and description are defined in the top-level `__init__.py` file.

This project uses [semantic versioning](https://semver.org/).

Build and publish the library:
```bash
$ flit build
$ flit publish
```