from mysql.connector import connect
import boto3
from botocore.exceptions import ClientError
import json
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
import sys
import logging
from datetime import datetime

logging.basicConfig()

from zendesk_csat import get_data
from helpers import rename_columns

load_dotenv()

SECRET_NAME = os.environ["SECRET_NAME"]
REGION_NAME = os.environ["REGION_NAME"]
AWS_ACCESS_KEY_ID = os.environ["AWS_ACCESS_KEY_ID"]
AWS_SECRET_ACCESS_KEY = os.environ["AWS_SECRET_ACCESS_KEY"]
AWS_DB_HOST = os.environ["AWS_DB_HOST"]
AWS_DB_USER = os.environ["AWS_DB_USER"]


def get_secret():

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name="secretsmanager",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION_NAME,
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=SECRET_NAME)
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    # Decrypts secret using the associated KMS key.
    secret = get_secret_value_response["SecretString"]

    return secret


def clean_response(df: pd.DataFrame) -> pd.DataFrame:
    # df = df.drop(["Unnamed: 0", "Comment Sentiment"], axis=1)
    # Convert any NaN values to NULL
    df = df.where((pd.notnull(df)), None)
    try:
        df["uid"] = df["Ticket ID"].astype(str) + "-" + df["Agent ID"].astype(str)
    except KeyError:
        pass
    df = rename_columns(df)
    print(df)
    return df


def dedup_insert(df: pd.DataFrame, engine):

    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

    df["updated_at"] = datetime.now()

    query_dedup = """
    # check if the ids from staging already exists in the main table if so deleting existing records
    DELETE 
    FROM csat_prod
    WHERE CAST(uid as CHAR) IN (SELECT CAST(uid as CHAR) FROM csat_staging);
    """

    query_insert = """
    # check if the ids from staging already exists in the main table if so deleting existing records
    INSERT INTO csat_prod
    SELECT 
    ticket_id,
    csat_score,
    agent_id,
    agent_name,
    timestamp,
    group_name,
    uid,
    updated_at
    FROM 
    csat_staging
    ;
    """

    with engine.connect() as conn:

        df.to_sql(con=conn, name="csat_staging", if_exists="replace", index=False)

        conn.execute(text(query_dedup))

        conn.execute(text(query_insert))

        conn.commit()

    return None


def upload_postgres(data: pd.DataFrame, name: str):
    engine = create_engine(os.environ["POSTGRES"])
    data.to_sql(
        name=name,
        con=engine,
        if_exists="replace",
        index=False,
    )
    return None


if __name__ == "__main__":
    ct_string = str(sys.argv[1])
    mysql_secret = json.loads(get_secret())
    # Read the CSV file and exclude the "ABC" column
    if os.path.exists(f"output/{ct_string}_csat.csv"):
        csv_file = f"output/{ct_string}_csat.csv"
        csat_apu = pd.read_csv(csv_file)
    if os.path.exists(f"output/{ct_string}_csat_tickets.csv"):
        csv_file = f"output/{ct_string}_csat_tickets.csv"
        csat_ticket = pd.read_csv(csv_file)
    if os.path.exists(f"output/{ct_string}_csat_user.csv"):
        csv_file = f"output/{ct_string}_csat_user.csv"
        csat_user = pd.read_csv(csv_file)
    # else:
    #     df = get_data()

    csat_apu = clean_response(csat_apu)
    csat_ticket = clean_response(csat_ticket)

    upload_postgres(csat_apu, "csat_apu_staging")
    upload_postgres(csat_ticket, "csat_ticket_staging")
    upload_postgres(csat_user, "csat_user_staging")

    # # Connect to your AWS MySQL database
    # aws_db_host = AWS_DB_HOST
    # aws_db_user = AWS_DB_USER
    # aws_db_password = mysql_secret['password']
    # aws_db_name = 'csat_aputure'

    # engine = create_engine(f"mysql+mysqlconnector://{aws_db_user}:{aws_db_password}@{aws_db_host}/{aws_db_name}", echo=True)
    # dedup_insert(df=df, engine=engine)
