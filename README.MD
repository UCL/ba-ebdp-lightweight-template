# Introduction to scripted lightweight models

This folder contains some example workflows for generating lightweight models from open datasets.

## IDE Setup

Install VS Code and peruse the [getting started docs](https://code.visualstudio.com/docs/introvideos/basics). VS Code is a well maintained and intuitive "Integrated Developer Environment" which helps with code. It has a built in terminal, file navigator, plugins (extensions), and all around robust support for development in a variety of languages.

Once installed, go to the extensions tab and install the following. When there are multiple options or similar sounding plugins, select the ones with the blue checkmark and signed by e.g. Microsoft:

- Code Spell Checker
- markdownlint
- python
- pylance
- pylint
- Black formatter
- isort
- Jupyter
- Jupyter Cell Tags
- Jupyter Keymap
- Jupyter Notebook Renderers

## Package Management

- If you're on mac, install [homebrew](https://brew.sh). This is a package manager which simplifies installation of packages used by computational workflows. If you're on windows you'll need to manage and install packages another way.
- Start off by installing `git`, `python`, and `pdm` (from the terminal).
  - `brew install git`
  - `brew install python`
  - `brew install pdm`
- Periodically run `brew upgrade` to keep your packages updated and in sync.

## Directory Setup

If you will be using the code and notebooks for continued development, then it may be worth learning about `git`, which is a versioning control system. `git` allows you to compare and "commit" changes, work in multiple "branches", "tag" versions, etc. When used with Github.com, it becomes a way to share and collaborate, and serves as a backup of your code.

Start by setting-up a Github account with two factor authentication by following Part 1 of their [onboarding](https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account) guide.

Once you have a Github account, you can either fork this template repository or you can create your own from scratch by following the Environment Setup guidelines below.

- If creating your own repo from scratch, you can refer to this template repository's structure, `.gitignore`, and `pyproject.toml` files for clues on how to complete setup.
- If forking this repository, run `pdm install` to initialise a virtual environment and install the required python packages.

## Environment Setup

Create a Github repository inside your Github.com account, and then clone this repository to your local machine. This can be done manually, but if new to `git` and repository management then it can be easier to get started with the [GitHub Desktop](https://desktop.github.com) utility. Once you've cloned your new repository to a local directory, then open this folder from VS code. Note that VS code has built-in `git` synchronisation features to help commit changes and for pulling and pushing changes to Github.com.

> Don't clone or create `git` managed folders in cloud-synced directories, i.e. avoid use of Dropbox or iCloud directories.

Once you've created your Github repository, cloned it to your local machine, and opened it in VS code:

- Open the integrated terminal window.
- Add a `.gitignore` file in the root of your repository directory, notice the leading period. This file lists file types and directories that should be ignored by `git`. Copy and paste the content from [this file](https://github.com/UCL/ba-ebdp-toolkit/blob/main/.gitignore) as a starting point. Once this file is created, commit this change and sync to Github using the built-in VS Code tools.
- Add a `README.md` file in the root of you repository. This file serves as a landing page for your repository on Github.com and should contain any introductory or setup instructions for your repo.
- Use PDM to initialise the repository by typing `pdm init`; select your `brew` python version and allow PDM to create a "virtual environment". While initialising your repository, PDM will create a `pyproject.toml` file in your repo which lists metadata about the project and the packages required by the project. If cloning this repository to another computer, you are then able to run `pdm install` to install any packages listed in your `pyproject.toml` file. To update packages, run `pdm update`.
- By using a virtual environment, your packages remain contained within the project, thereby preventing complications from sharing packages system-wide. VS code will ordinarily auto-detect the virtual environment and will ask to use the virtual environment; click "yes" and check that VS code is using the virtual environment instead of the system or brew python.
- Install any required python packages using `pdm add` followed by the desired packages. For example, `pdm add shapely geopandas cityseer osmnx momepy networkx pandas matplotlib ipykernel pyproj`. This will add the packages to your `pyproject.toml` file and install them in your virtual environment.
- Commit the changes and sync to the remote.

## Notebooks vs Code Cells

- The examples in this template repository make use of code cells which can be used from regular python files where supported by the IDE. The cells are demarcated by `#%%` and VS code will then show buttons for running a cell, with outputs generated to separate pane. This works similarly to Python notebooks, and the code cells workflows can generally be replicated as notebooks without issue if that were preferable.

## Data

- Create a folder called `temp` inside the root of your repository. Check that this is ignored by the `.gitignore` file. Place any data or temporary files in this directory so that these files are not synced to Github, which would otherwise introduce unwanted bloat into your repository.
- Define an area of extents in QGIS and save to a GPKG file in your `temp` directory; this will be loaded from the notebooks for the subsequent analysis. Alternatively, use the `workflows/download_extent.py` template script to download an area of interest using `osmnx`.
- Follow the scripts:
  - [](workflows/download_extent.py)
  - [](workflows/download_network.py)
  - [](workflows/compute_centrality.py)
  - [](workflows/compute_accessibility.py)
  - [](workflows/download_buildings.py)
- Additional metrics can be computed based on available datasets. Prepare the datasets in QGIS and save as a GPKG for the region of interest. We will then create a suitable workflow for ingesting and using the dataset. Examples of useful datasets may include:
  - [Eurostat census grid population count](https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/population-distribution-demography/geostat#geostat11). This is count per km2.
  - [Urban atlas](https://land.copernicus.eu/local/urban-atlas/urban-atlas-2018) for blocks.
  - [Tree cover](https://land.copernicus.eu/local/urban-atlas/street-tree-layer-stl-2018) (~36GB vectors).
  - [Digital Height Model](https://land.copernicus.eu/local/urban-atlas/building-height-2012)

## Workflows
