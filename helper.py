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
    operation = ""

    if command == "1":
        operation = f"Flights that have currently taken off"
    elif command == "2":
        operation = f"Flights with destination country: {arg1}"
        if not arg1:
            error += "Country must be provided!"
    elif command == "3":
        operation = f"Flights originating from airport with code: {arg1}"
        if not arg1:
            error += "Airport code must be provided!"
    elif command == "4":
        operation = f"Flights landing at airport with code: {arg1}"
        if not arg1:
            error += "Airport code must be provided!"
    elif command == "5":
        operation = "Flights within the Northern Hemisphere"
    elif command == "6":
        operation = "Flights within the Southern Hemisphere"
    else:
        error = "Invalid Command"
    converted = namedtuple("Command", "command operation arg1 error")
    return converted(command, operation, arg1, error)

def run_analyses(command: tuple) -> str:
    """Given an analyses to run, will execute that analyses and get that result as an HTML string.
    Args:
        analyses (str): Key dictating which analyses to run
    Returns:
        str: HTML Output of analyses
    """
    if command.command == "1":
        country = command.arg1
        query = "SELECT DISTINCT callsign, origin_airport_name, destination_airport_name from flight_data where altitude > 0"
        desc = "Finds all Delta flights with altitude greater than 0"
        result = requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "2":
        country = command.arg1
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name FROM flight_data WHERE destination_airport_country_name  = '{command.arg1}'"
        desc = "Finds all Delta flights with the destination country: {}".format(country)
        result = requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "3":
        airport = command.arg1
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name from flight_data where origin_airport_iata = '{command.arg1}'"
        desc = "Finds all Delta flights with the origin airport code: {}".format(airport)
        result =  requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "4":
        airport = command.arg1
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name from flight_data where destination_airport_iata = '{command.arg1}'"
        desc = "Finds all Delta flights with the destination airport code: {}".format(airport)
        result =  requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "5":
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name from flight_data where latitude > 0"
        desc = "Finds all Delta flights within the Northern hemisphere"
        result = requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    elif command.command == "6":
        query = f"SELECT DISTINCT callsign, origin_airport_name, destination_airport_name from flight_data where latitude < 0"
        desc = "Finds all Delta flights within the Southern hemisphere"
        result = requests.post("http://127.0.0.1:8090/database/scan", json={"tableName": "flight_data", "selectQuery": query}).json()
    return format_analyses_output(result, query, desc)


def format_analyses_output(analyses_result, query, desc) -> str:
    """Given the result of an analyses, will format as HTML string.

    Args:
        analyses_result (tuple): Result of analyses
        query (str): SQL query used in the analysis
        desc (str): Description of the analysis
    Returns:
        str: HTML Representation of analyses
    """
    # header = f"<h1>Analyses</h1><h2>What Analyses is being ran?</h2><p>{query}</p>"
    # desc = f"<h2>What is this Analyses doing?</h2><p>{desc}</p>"
    # note = f"<div class='alert alert-warning alert-dismissable fade show' role='alert'><strong>NOTE:</strong> <button type='button' class='close' data-dismiss='alert' aria-label='close><span aria-hidden='true'>&times;</span></button></div>"

    # Convert analyses_result to DataFrame
    df = pd.DataFrame(analyses_result)

    # Add hyperlink to the 'callsign' column
    df['callsign'] = df['callsign'].apply(lambda x: f"<a href='/route/{x}'>{x}</a>")

    final_output = f"{df.to_html(index=False, classes='styled-table', escape=False)}"
    html_repr = f"{final_output}"

    return html_repr


if __name__ == "__main__":
    # This area is used for testing functions by running python helper.py
    pass