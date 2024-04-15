from typing import Any
from collections import namedtuple
import requests
from flask import Flask, render_template
import pandas as pd

def validate_input(form_response: dict, file_obj) -> tuple:
    """Validates input from form
    Args:
        form_response (dict): Form Response returned by HTML
    Returns:
        tuple: tuple containing command information, or an error if one exists. 
    """
    command = form_response.get('command')
    error = ""
    arg1 = form_response.get('arg1_input')

    if command == "1":
        if not arg1:
            error += "Country must be provided!"
    elif command == "2":
        if not arg1:
            error += "Country must be provided!"
    elif command == "3":
        if not arg1:
            error += "Airport code must be provided!"
    elif command == "4":
        if not arg1:
            error += "Airport code must be provided!"
    elif command == "5":
        pass
    elif command == "6":
        pass
    else:
        error = "Invalid Command"
    converted = namedtuple("Command", "command arg1 error")
    return converted(command, arg1, error)

def run_analyses(command: tuple) -> str:
    """Given an analyses to run, will execute that analyses and get that result as an HTML string.
    Args:
        analyses (str): Key dictating which analyses to run
    Returns:
        str: HTML Output of analyses
    """
    if command.command == "1":
        country = command.arg1
        query = "SELECT _ from _"
        desc = "Finds all Delta flights with the origin country: {}".format(country)
        result = requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "2":
        country = command.arg1
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name FROM flight_data WHERE destination_airport_country_name  = '{command.arg1}' limit 10"
        desc = "Finds all Delta flights with the destination country: {}".format(country)
        result = requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "3":
        airport = command.arg1
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name from flight_data where origin_airport_iata = '{command.arg1}' limit 10"
        desc = "Finds all Delta flights with the origin airport code: {}".format(airport)
        result =  requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "4":
        airport = command.arg1
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name from flight_data where destination_airport_iata = '{command.arg1}' limit 10"
        desc = "Finds all Delta flights with the destination airport code: {}".format(airport)
        result =  requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "5":
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name from flight_data where latitude > 0 limit 10"
        desc = "Finds all Delta flights within the Northern hemisphere"
        result = requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "6":
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name from flight_data where latitude < 0 limit 10"
        desc = "Finds all Delta flights within the Southern hemisphere"
        result = requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    #result = [{'callsign': 'DAL88', 'origin_airport_name': 'Atlanta Hartsfield-Jackson International Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}, {'callsign': 'DAL84', 'origin_airport_name': 'Atlanta Hartsfield-Jackson International Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}, {'callsign': 'DAL98', 'origin_airport_name': 'Detroit Metropolitan Wayne County Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}, {'callsign': 'DAL228', 'origin_airport_name': 'Cincinnati Northern Kentucky International Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}, {'callsign': 'DAL266', 'origin_airport_name': 'New York John F. Kennedy International Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}, {'callsign': 'DAL82', 'origin_airport_name': 'Atlanta Hartsfield-Jackson International Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}, {'callsign': 'DAL264', 'origin_airport_name': 'New York John F. Kennedy International Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}, {'callsign': 'DAL152', 'origin_airport_name': 'Minneapolis Saint Paul International Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}, {'callsign': 'DAL224', 'origin_airport_name': 'Boston Logan International Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}, {'callsign': 'DAL220', 'origin_airport_name': 'Salt Lake City International Airport', 'destination_airport_name': 'Paris Charles de Gaulle Airport'}]
    return format_analyses_output(result, query, desc)
        

def format_analyses_output(analyses_result, query, desc) -> str:
    """Given the result of an analyses, will format as HTML string. Should be able to call this function with any analyses result
    Args:
        analyses_result (tuple): Result of analyses
    Returns:
        str: HTML Representation of analyses
    """
    html_repr = ""
    header = f"<h1>Analyses</h1><h2>What Analyses is being ran?</h2><p>{query}</p>"
    desc = f"<h2>What is this Analyses doing?</h2><p>{desc}</p>"
    note = f"<div class='alert alert-warning alert-dismissable fade show' role='alert'><strong>NOTE:</strong> <button type='button' class='close' data-dismiss='alert' aria-label='close><span aria-hidden='true'>&times;</span></button></div>"
    final_output = f"<h2>Final Output of Analyses</h2>{pd.DataFrame(analyses_result).to_html(index = False)}"
    html_repr = f"{header}{desc}{final_output}"
    return html_repr

if __name__ == "__main__":
    # This area is used for testing functions by running python helper.py
    pass