# NERSC's Documentation Summarizer

Boils the [NERSC (mkdocs) documentation](https://gitlab.com/NERSC/nersc.gitlab.io/-/tree/main?ref_type=heads) to a single file for LLM ingestion, keeping only the most viewed pages.

## Installing

Creating a dedicated Python environment:

```sh
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install pandas pyyaml
```

## Usage

Place the `Pages_and_screens_Page_title_and_screen_class.csv` file in an `inputs` folder.

Update the NERSC documentation submodule:

```sh
# Pull the latest changes from the submodule's main branch
git submodule update --remote

# Commit the updated submodule reference
git commit -m "Update NERSC documentation submodule"
```

Load the Python environment and runing the code to collect the current documentation as a single file:

```sh
source venv/bin/activate

python3 merge.py
```

## Results

Currently (March 2025) the 248 files of our documentation seen at least once this month make for a 666296 Gemini tokens long file.
Fitting confortably in Gemini 2.5Pro's 1M tokens context length.

Short tests show that Gemini 2.5Pro is able to answer questions meaningfully using the following prompt:

```md
You have been given the [NERSC Supercomputing Center's documentation](https://docs.nersc.gov/). Use it to provide a NERSC-specific answer to questions submitted to you.
```
