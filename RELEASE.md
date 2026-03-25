# Release Procedure
The basic procedure for releasing a new version of **FitOut** consists of:
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

**FitOut** uses semantic versioning. Update the version number in [FitOut/fitout/__init__.py](FitOut/fitout/__init__.py) according to changes since the previous tag.

**NOTE:** Ensure that the updated [FitOut/fitout/__init__.py](FitOut/fitout/__init__.py) is committed before creating the tag!

Create a tag with the current version, e.g. `v0.0.9`.
```bash
git tag v0.0.9
```

*(Tip: In PowerShell, you can automatically extract and tag using the version in `__init__.py`:)*
```powershell
$version = python -c "import re; match=re.search(r'__version__\s*=\s*[\'\""]v?([^\'\""]+)[\'\""]', open('fitout/__init__.py').read()); print('v' + match.group(1)) if match else exit(1)"
if ($LASTEXITCODE -eq 0) { git tag $version; Write-Host "Created tag: $version" } else { Write-Host "Failed to find version" }
```

## Update the ChangeLog

**FitOut** uses `auto-changelog` to parse git commit messages and generate the `CHANGELOG.md`.

```bash
# 1. Generate the changelog (it will detect the tag you just made)
auto-changelog --tag-prefix v

# 2. Add and commit the changelog
git add CHANGELOG.md
git commit -m "Updating CHANGELOG for $version"

# 3. Move the tag forward to include the changelog commit!
git tag -f $version

# 4. Push the branch and the new tag
git push
git push -f --tags
```

## Make a GitHub Release

Go to the GitHub project administration page and [publish a release](https://github.com/kev-m/FitOut/releases/new) using the tag created, above.

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