import sys
import os
import yaml
from yaml.loader import SafeLoader

import plotly.graph_objects as go
import streamlit as st
import streamlit_authenticator as stauth
import pandas as pd
from streamlit.web import cli as stcli
from streamlit import runtime

from sqlalchemy import create_engine, text
from dotenv import load_dotenv

import datetime
from datetime import date

from visualizers import (
    status_metrics,
    agent_metrics,
    turnaround_time_metrics,
    turnaround_time_agent_metrics,
    keyword_metrics,
)
from load_data import load_agents, load_subject_keyword_dataframe


load_dotenv()

PAGES = ["Tickets Status", "Rep Stats"]


def UI():
    st.sidebar.title("CSAT Dashboard")

    if st.session_state.page:
        page = st.sidebar.radio("Navigation", PAGES, index=st.session_state.page)
    else:
        page = st.sidebar.radio("Navigation", PAGES, index=0)
    st.experimental_set_query_params(page=page)

    if page == "Tickets Status":
        st.sidebar.title("Tickets Status")
        start_date = st.sidebar.date_input(
            "choose a start date for metric calculation: ", datetime.date(2023, 2, 1)
        )
        end_date = st.sidebar.date_input(
            "choose an end date for metric calculation: ", datetime.date(2023, 3, 1)
        )

        keyword = st.sidebar.text_input(
            label="Type in keyword you want to display metrics for",
            value="300d",
        )

        # ticket status
        region = st.multiselect(
            "select all regions to view the metrics:",
            options=[
                "africa",
                "apac",
                "europe",
                "united_states",
                "south_america",
                "middle_east__west_asia_south_asia",
                "india",
            ],
            default=[
                "africa",
                "apac",
                "europe",
                "united_states",
                "south_america",
                "middle_east__west_asia_south_asia",
                "india",
            ],
        )
        status_metrics(region=region, start_date=start_date, end_date=end_date)

        # ticket status by agent
        # agent_metrics(agent=agent_id,start_date=start_date, end_date=end_date)

        # service turnaround time for a ticket to be resolved
        turnaround_time_metrics(start_date=start_date, end_date=end_date)

        # visualize the frequency keywords appear in the ticket descriptions
        keyword_metrics(start_date=start_date, end_date=end_date, keyword=keyword)

        keyword_df = load_subject_keyword_dataframe(
            start_date=start_date, end_date=end_date, keyword=keyword
        )
        st.text(f"Tickets Contain Keyword: {keyword}")
        st.dataframe(keyword_df)

    if page == "Rep Stats":
        st.sidebar.title("Rep Stats")
        start_date = st.sidebar.date_input(
            "choose a start date for metric calculation: ", datetime.date(2023, 2, 1)
        )
        end_date = st.sidebar.date_input(
            "choose an end date for metric calculation: ", datetime.date(2023, 3, 1)
        )
        agents = load_agents()
        agent = st.selectbox("Which agent metrics to view", options=agents.keys())
        agent_id = agents[agent]

        # ticket status by agent
        agent_metrics(agent=agent_id, start_date=start_date, end_date=end_date)

        # service turnaround time for a ticket to be resolved
        turnaround_time_agent_metrics(
            start_date=start_date,
            end_date=end_date,
            agent_id=agent_id,
            agent_name=agent,
        )
    return


if __name__ == "__main__":
    # if not os.path.exists("Output"):
    #     os.makedirs("Output")
    with open("./dashboard/authentications.yml") as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"],
        config["preauthorized"],
    )

    name, authentication_status, username = authenticator.login("Login", "main")

    if authentication_status:
        authenticator.logout("Logout", "main", key="unique_key")

        if runtime.exists():
            url_params = st.experimental_get_query_params()
            print(f"the url params are: {url_params}")
            if "loaded" not in st.session_state:
                if len(url_params.keys()) == 0:
                    st.experimental_set_query_params(page="Tickets Status")
                    url_params = st.experimental_get_query_params()
                    print(f"not loaded url params {url_params}")

                st.session_state.page = PAGES.index(url_params["page"][0])

            UI()
        else:
            sys.argv = ["streamlit", "run", sys.argv[0]]
            sys.exit(stcli.main())

    elif authentication_status is False:
        st.error("Username/password is incorrect")
    elif authentication_status is None:
        st.warning("Please enter your username and password")
