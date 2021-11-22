# How to run rtree-spark

- Install Apache Spark.
- Git clone the repository.
- Install a virtual environment. (Recommended: venv)
  - You can install and activate a virtual environment with the command: `python -m venv .venv` & `./.venv/Scripts/activate`
- Install the project dependencies with the command: `pip install -r requirments`
- Run the program with the command `python main.py`

## Configurations

You can configure some aspects of the program. Inside `main.py` there are 3 variables that can be changed.

- printInConsole: If set to `True`, the R-Tree gets printed in the terminal. Default is `False`.
- data_set: It's the variable which points which data set should be used inside the `/data-sets/` folder.
