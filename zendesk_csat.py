#!/usr/bin/python
# Aputure Zendesk Integration
# (C) Aputure Data
# Import neccessary libraries
import pandas as pd
import pandasql as ps

from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import parser
from dotenv import load_dotenv
import os
import sys

from helpers import unpack_fields

from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User
load_dotenv()

EMAIL = os.environ["EMAIL"]
TOKEN = os.environ["TOKEN"]
SUBDOMAIN = os.environ["SUBDOMAIN"]

# Zendesk credentials (confidential)
creds = {
    'email' : EMAIL,
    'token' : TOKEN,
    'subdomain': SUBDOMAIN
}

def process_ticket(results: dict, id: str, ticket: Ticket) -> dict:
    results[id] = {}
    results[id]["Ticket ID"]= ticket.id
    results[id]["Subject"] = ticket.subject
    results[id]["Assignee ID"] = ticket.assignee_id
    results[id]["Fields"] = unpack_fields(ticket.fields)
    results[id]["Ticket Descriptions"] = ticket.description
    results[id]["Created At"] = ticket.created_at
    results[id]["Status"] = ticket.status
    results[id]["Updated At"] = ticket.updated_at
    results[id]["Request Timestamp"] = datetime.now()

    return results

def process_user(results: dict, id: str, user: User) -> dict:
    results[id] = user.to_dict()
    results[id]["Updated At"] = datetime.now()

    return results


def get_data():
    # Default
    # zenpy_client = Zenpy(proactive_ratelimit=300, **creds)
    zenpy_client = Zenpy(**creds)

    # Initializing blank dictionary
    csat_apu = {}
    csat_ticket = {}
    csat_user = {}
    # Ticket Metrics
    # Ticket Customer Satisfaction
    # for scoring in ['bad_with_comment']:
    for scoring in ['good_with_comment', 'good_without_comment', 'bad_with_comment', 'bad_without_comment']:
        for counter, s in enumerate(zenpy_client.satisfaction_ratings(sort_order = 'desc', score = scoring)): # , score='good'):
            print("Customer satisfaction #" + str(counter))
            # print(s)
            print("Ticket ID: " + str(s.ticket.id))
            tickID = s.ticket.id
            csat_apu[tickID] = {}
            csat_apu[tickID]["Ticket ID"] = tickID
            # print("CSAT score: " + str(s.score))
            print("CSAT score: " + str(scoring))
            csat_apu[tickID]["CSAT score"] = scoring
            print("Agent ID assigned to at time of rating: " + str(s.assignee.id))
            csat_apu[tickID]["Agent ID"] = s.assignee.id
            print("Agent name: " + str(s.assignee.name))
            csat_apu[tickID]["Agent Name"] = s.assignee.name
            print("Time the satisfaction rating got created: " + str(s.created))
            csat_apu[tickID]["Timestamp"] = s.created
            print("Ticket group: " + str(s.ticket.group.name))
            csat_apu[tickID]["Group Name"] = s.ticket.group.name
            print("The time the satisfaction rating got updated: " + str(s.updated))
            # input("Press enter to continue...")
            if tickID in csat_ticket:
                pass
            else: 
                ticket = zenpy_client.tickets(id=tickID)
                csat_ticket = process_ticket(csat_ticket, id=tickID, ticket=ticket)
                print(f"add ticket {tickID}")
            
            if csat_apu[tickID]["Agent ID"] in csat_user:
                pass
            else:
                agentID = csat_apu[tickID]["Agent ID"]
                user = zenpy_client.users(id=agentID)
                csat_user = process_user(csat_user, id=agentID, user=user)
                print(f"add user {agentID}")
                
                
    csat_pd = pd.DataFrame.from_dict(csat_apu, orient='index')
    csat_ticket_df = pd.DataFrame.from_dict(csat_ticket, orient="index")
    csat_user_df = pd.DataFrame.from_dict(csat_user, orient="index")
    return csat_pd, csat_ticket_df, csat_user_df

if __name__ == "__main__":

    #get the current time 
    ct_string = str(sys.argv[1])
    fileout = f"output/{ct_string}_csat.csv"

    csat_pd, csat_ticket_df, csat_user_df = get_data()
    csat_pd.to_csv(fileout, index=False)
    csat_ticket_df.to_csv(f"output/{ct_string}_csat_tickets.csv", index=False)
    csat_user_df.to_csv(f"output/{ct_string}_csat_user.csv", index=False)
    

#print(csat_pd)
