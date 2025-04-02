# csat db
Repo for zendesk customer service db updates


## How to Run

Repo is set up to run automatically with [GitHub Actions on Sunday, Tuesday, and Thursday](https://github.com/td928/customer-service-db/blob/main/.github/workflows/triweekly.yml). Running the application locally should be similar, once [devcontainer](https://code.visualstudio.com/docs/devcontainers/containers) is set up with VSCode and running with the Docikerfile provided. Try

```shell
python -m pip install -r requirements.txt
mkdir -p output
python zendesk_csat.py 2023-05-24
```
Three output should be saved per run e.g. 

```
cd output
ls 

#should return
#2023-05-24_csat.csv
#2023-05-24_csat_tickets.csv
#2023-05-24_csat_user.csv
```

### Upload AWS
Push the results to AWS PostgreSQL instance

```
python upload.py 2023-05-24
```

when running this GitHub Acitons all credentials specified below need to be added as [repo secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions). 

```yaml
    - name: Upload AWS
      env:
        EMAIL: ${{ secrets.EMAIL }}
        TOKEN: ${{ secrets.TOKEN }}
        SUBDOMAIN: ${{ secrets.SUBDOMAIN }}
        SECRET_NAME: ${{ secrets.SECRET_NAME }}
        REGION_NAME: ${{ secrets.REGION_NAME}}
        AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
        AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY}}
        AWS_DB_HOST: ${{ secrets.AWS_DB_HOST }}
        AWS_DB_USER: ${{ secrets.AWS_DB_USER}}
```

### Metrics Visualizations

`visualizers.py` include a series of metrics that can be visualized in the streamlit tool. Run the tool in the devcontainer by 

```shell
streamlit run app.py
```
