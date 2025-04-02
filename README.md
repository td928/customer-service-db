# csat db
Repo for zendesk customer service db updates


## How to Run

Repo is set up to run automatically with GitHub Actions on Sunday, Tuesday, and Thursday. Running the application locally should be similar, once [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) is set up with VSCode and running with the Docikerfile provided. Try

```shell
python -m pip install -r requirements.txt
mkdir -p output
python zendesk_csat.py 2023-05-24
```

Python script `zendesk_csat.py` requires one argument is 
