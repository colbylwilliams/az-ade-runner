# Tools

This folder contains scripts used during development and in [workflows](../.github/workflows)

| Script                                 | Description                                                           |
| -------------------------------------- | --------------------------------------------------------------------- |
| [build-cli.sh](build-cli.sh)           | Used to build, lint and style check the cli extension for release     |
| [bump-version](bump-version.py)        | Bump the version of the CLI extension and update the install url      |
| [cli-version](cli-version.py)          | Gets the version of the CLI from the source. Used in release pipeline |
| [prepare-assets.py](prepare-assets.py) | Creates and saves all release assets to be uploaded                   |