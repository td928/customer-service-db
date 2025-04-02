import os
import pandas as pd

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

from datetime import date
import re 

load_dotenv()
BUILD_ENGINE = os.environ["POSTGRES"]
TABLE_LOOKUP = {
    "Nanlite": "nanlite_user_group",
    "Gaffer Salon": "gaffer_salon",
    "Godox": "godox_user_group",
    "Prolycht": "prolycht_user_group",
}

engine = create_engine(BUILD_ENGINE)

def load_agents() -> pd.DataFrame:
    query = f"""
        SELECT
        DISTINCT
        u.id,
        u.name
        FROM
        csat_user_staging u 
        WHERE
        active = 'TRUE'
    """
    with engine.begin() as conn:
        df = pd.read_sql(sql=text(query), con=conn)

    agents = dict(zip(df.name, df.id))
    return agents

def load_status_data(start_date: date, end_date: date):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    query = f"""
        select 
        COUNT(*) as ticket_count,
        status,
        SPLIT_PART(fields, '-', 1) as region
        FROM
        csat_ticket_staging
        WHERE
        created_at BETWEEN '{start_date_str}' and '{end_date_str}'
        GROUP BY
        status,
        region
        """
    with engine.begin() as conn:
        df = pd.read_sql(sql=text(query), con=conn)

    return df

def load_agent_status_data(start_date: date, end_date: date):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    query = f"""
        select 
        u.id::TEXT,
        u.name,
        t.status,
        COUNT(*) as user_ticket_status
        from
        csat_user_staging u 
        LEFT JOIN  csat_ticket_staging t ON u.id = t.assignee_id
        WHERE
        t.created_at BETWEEN '{start_date_str}' and '{end_date_str}'
        GROUP BY 
        u.id,
        u.name,
        t.status
        """
    with engine.begin() as conn:
        df = pd.read_sql(sql=text(query), con=conn)

    return df

def load_turnaround_time_data(start_date: date, end_date: date):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    query = f"""
    select
    t.ticket_id::TEXT, 
    u.id as agent_id,
    u.name as agent_name,
    EXTRACT(EPOCH FROM (t.updated_at::timestamp - t.created_at::timestamp)) as turnaround_seconds,
    ROUND(EXTRACT(EPOCH FROM (t.updated_at::timestamp - t.created_at::timestamp)) / 3600) as turnaround_hours,
    t.updated_at::timestamp - t.created_at::timestamp as turnaround_interval
    FROM
    csat_ticket_staging t LEFT JOIN csat_user_staging u ON t.assignee_id = u.id
    WHERE
    t.created_at BETWEEN '{start_date_str}' and '{end_date_str}'
    AND t.status = 'solved'
    """
    with engine.begin() as conn:
        df = pd.read_sql(sql=text(query), con=conn)

    return df

def load_subject_keyword_status_data(keyword: str, start_date: date, end_date: date):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    if not re.match("^[a-zA-Z0-9\s!?\(\)\-]*$", keyword):
        print("Bad input. Only letters (upper and lowercase), numbers and space are allowed types.")
        return pd.DataFrame()
    if re.search(r'\bdelete\b', keyword, re.IGNORECASE):
        print("Found 'delete' in keyword phrase")
        return pd.DataFrame()
    if re.search(r'\bselect\b', keyword, re.IGNORECASE):
        print("Found 'select' in keyword phrase")
        return pd.DataFrame()
    if re.search(r'\bunion\b', keyword, re.IGNORECASE):
        print("Found 'union' in keyword phrase")
        return pd.DataFrame()
    
    query = f"""
        SELECT 
        COUNT(*) as ticket_count,
        status
        FROM 
        csat_ticket_staging t
        WHERE 
        t.created_at BETWEEN '{start_date_str}' AND '{end_date_str}'
        AND 
        LOWER(t.subject) LIKE '%{keyword}%'
        GROUP BY 
        status
        """
    with engine.begin() as conn:
        df = pd.read_sql(sql=text(query), con=conn)

    return df

def load_subject_keyword_dataframe(keyword: str, start_date: date, end_date: date):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    if not re.match("^[a-zA-Z0-9\s!?\(\)\-]*$", keyword):
        print("Bad input. Only letters (upper and lowercase), numbers and space are allowed types.")
        return pd.DataFrame()
    if re.search(r'\bdelete\b', keyword, re.IGNORECASE):
        print("Found 'delete' in keyword phrase")
        return pd.DataFrame()
    if re.search(r'\bselect\b', keyword, re.IGNORECASE):
        print("Found 'select' in keyword phrase")
        return pd.DataFrame()
    if re.search(r'\bunion\b', keyword, re.IGNORECASE):
        print("Found 'union' in keyword phrase")
        return pd.DataFrame()
    
    query = f"""
        SELECT 
        *
        FROM 
        csat_ticket_staging t
        WHERE 
        t.created_at BETWEEN '{start_date_str}' AND '{end_date_str}'
        AND 
        LOWER(t.subject) LIKE '%{keyword}%'
        """
    with engine.begin() as conn:
        df = pd.read_sql(sql=text(query), con=conn)

    return df

def basic_stats():

    """things to keep track such as number of posts per weeks to establish baseline of scraping working properly"""

    