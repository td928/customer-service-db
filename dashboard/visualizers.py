import plotly.graph_objects as go
import streamlit as st
import pandas as pd
from streamlit.web import cli as stcli
from streamlit import runtime
import plotly.express as px
from datetime import date

from load_data import (
    load_status_data,
    load_agent_status_data,
    load_turnaround_time_data,
    load_subject_keyword_status_data,
)


def status_metrics(region: list, start_date, end_date):
    data = load_status_data(start_date=start_date, end_date=end_date)
    filtered = data.loc[data.region.isin(region)]
    if filtered.empty:
        return st.text(
            "Your selection returned empty dataframe. Check your parameters e.g. dates, groups etc"
        )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=filtered.status,
                values=filtered.ticket_count,
                textinfo="label+percent+value",
                textfont_size=10,
                # pull=[0.2 if x == company else 0 for x in total.index],
            )
        ],
    )
    fig.update_annotations()
    fig.update_layout(
        title_text=f"Status Breakdown",
    )
    st.plotly_chart(fig)
    return None


def agent_metrics(agent: str, start_date, end_date):

    data = load_agent_status_data(start_date=start_date, end_date=end_date)
    filtered = data.loc[data.id.astype(str) == str(agent)]

    if filtered.empty:
        return st.text(
            "Your selection returned empty dataframe. Check your parameters e.g. dates, groups etc"
        )

    name = filtered["name"].unique()[0]

    fig = go.Figure(
        data=[
            go.Pie(
                labels=filtered.status,
                values=filtered.user_ticket_status,
                textinfo="label+percent+value",
                textfont_size=10,
                # pull=[0.2 if x == company else 0 for x in total.index],
            )
        ],
    )
    fig.update_annotations()
    fig.update_layout(
        title_text=f"{name} Status Breakdown",
    )
    st.plotly_chart(fig)

    return None


def turnaround_time_metrics(start_date, end_date):
    data = load_turnaround_time_data(start_date=start_date, end_date=end_date)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=data.ticket_id, y=data.turnaround_hours))
    fig.update_annotations()
    fig.update_layout(
        title_text=f"Turnaround Hours by Ticket ID",
    )
    fig.update_xaxes(type="category")
    st.plotly_chart(fig)

    return


def turnaround_time_agent_metrics(start_date, end_date, **kwargs):
    data = load_turnaround_time_data(start_date=start_date, end_date=end_date)
    agent_id = kwargs["agent_id"]
    agent_name = kwargs["agent_name"]

    filtered = data.loc[data.agent_id == agent_id]
    if filtered.empty:
        return st.text(
            "Your selection returned empty dataframe. Check your parameters e.g. dates, groups etc"
        )
    bar_agent = go.Figure()
    bar_agent.add_trace(go.Bar(x=filtered.ticket_id, y=filtered.turnaround_hours))
    bar_agent.update_annotations()
    bar_agent.update_layout(
        title_text=f"Turnaround Hours by Ticket ID for {agent_name}",
    )
    bar_agent.update_xaxes(type="category")
    st.plotly_chart(bar_agent)

    return None


def keyword_metrics(start_date, end_date, **kwargs):
    keyword = kwargs.get("keyword")
    data = load_subject_keyword_status_data(
        start_date=start_date, end_date=end_date, keyword=keyword
    )

    fig = go.Figure(
        data=[
            go.Pie(
                labels=data.status,
                values=data.ticket_count,
                textinfo="label+percent+value",
                textfont_size=10,
                # pull=[0.2 if x == company else 0 for x in total.index],
            )
        ],
    )
    fig.update_annotations()
    fig.update_layout(
        title_text=f"Status for Ticket Subject with '{keyword}'",
    )
    st.plotly_chart(fig)

    return
