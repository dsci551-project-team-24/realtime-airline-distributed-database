from typing import Any
from collections import namedtuple
from app import UPLOAD_FOLDER
import requests
from flask import Flask, render_template


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
    final_output = f"<h2>Final Output of Analyses</h2>{repr_list_items(analyses_result)}"
    html_repr = f"{header}{desc}{final_output}"
    return html_repr

def repr_list_items(li: list) -> str:
    list_repr = f""
    if isinstance(li, dict):
        for key, value in li.items():
            item_repr = f"<p style=padding-left:15px>{key} : {value},</p>"
            list_repr += item_repr
    # Otherwise, iterate through elements in list
    else:
        for item in li:
            list_repr += "<div style=padding-left:30px>["
            # List item could be a dictionary
            if not isinstance(item, list):
                for key, value in item.items():
                    if isinstance(value, dict):
                        val_repr = repr_list_items(value)
                    else:
                        val_repr = value
                    item_repr = f"<p style='padding-left:15px font-size:8px'>{key} : {val_repr},</p>"
                    list_repr += item_repr
            # List item is another list
            else:
                list_repr += "<div style=padding-left:30px>["
                list_repr += repr_list_items(item)
                list_repr += "],</div>"
            list_repr += "],</div>"
    return list_repr


if __name__ == "__main__":
    # This area is used for testing functions by running python helper.py
    pass