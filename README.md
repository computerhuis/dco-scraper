1. Create a new Python virtual environment
    ```python -m venv _env```
1. Switch to the new Python virtual environment:
    - Mac OS / Linux ```source _env/bin/activate```
    - Windows ```_env\Scripts\activate```
1. Check if the new Python virtual environment os active
    ```pip -V```
1. Upgrade pip in the virtual environment:
    ```pip install --upgrade pip```
1. Install the needed dependencies
    ```pip install -r requirements.txt```

For more information see [here](https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/26/python-virtual-env/)

## Pip tips
1. Remove all pip packages
    ```python -m venv --clear _env```
1. Save all packages to the 'requirements.txt'
    ```pip freeze > requirements.txt```
1. On Macos/Linux remove all pip packages:
    ```pip freeze | xargs pip uninstall -y```
