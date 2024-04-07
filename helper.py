from typing import Any
from collections import namedtuple
from edfs.commands import *
#from edfs.pmr import *
from app import UPLOAD_FOLDER

'''def dict_to_html(prev_str: str, item: Any) -> str:
    """Given a python object, will attempt to convert that object to an HTML string

    Args:
        prev_str (str): String to build on.
        item (Any): A python object

    Returns:
        str: HTML Representation of a string.
    """
    # Given Dict
    if isinstance(item, dict):
        for dict_key, dict_value in item.items():
            header = f"<details style='padding-left:30px'><summary>{dict_key}</summary>"
            contents = dict_to_html("", dict_value)
            expandable_element = f"{header}{contents}</details>"
            prev_str += expandable_element
    # GIVEN LIST
    elif isinstance(item, list):
        for element in item:
            elem_as_str = dict_to_html(prev_str, element)
            prev_str += elem_as_str
    # BASE CASE: GIVEN VALUE
    else:
        prev_str = f"<p style='padding-left:30px'>{item}</p>"

    return prev_str'''

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
    arg2 = form_response.get('arg2_input')
    file_input = file_obj
    filepath = ""
    cmd = None

    if command == "1":
        cmd = 'mkdir'
        if not arg1:
            error += "Filepath must be provided!"
    elif command == "2":
        cmd = 'ls'
        if not arg1:
            error += "Filepath must be provided!"
    elif command == "3":
        cmd = 'rm'
        if not arg1:
            error += "Filename must be provided!"
    elif command == "4":
        cmd = 'cat'
        if not arg1:
            error += "Filepath must be provided!"
    elif command == "5":
        cmd = 'put'
        if not file_input:
            error += "File must be provided!\t"
        else:
            filename = file_input.filename
            # Create UPLOAD folder if it does not exist
            if not os.path.exists(UPLOAD_FOLDER):
                os.mkdir(UPLOAD_FOLDER)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file_input.save(filepath)
            if not file_input.filename.endswith('.csv'):
                error += f"{file_input.filename.split('.')[-1]} files are not supported!"
        if not arg1:
            error += "Location must be provided!\t"
        if not arg2:
            error += "k (number of partitions) must be provided!"
    else:
        error = "Invalid Command"
    
    converted = namedtuple("Command", "command arg1 arg2 file_input error")
    return converted(cmd, arg1, arg2, filepath, error)

def run_command(command: tuple) -> tuple:
    """Runs a command given by a tuple

    Args:
        command (tuple): Command to execute.

    Returns:
        tuple: Tuple of output and status
    """
    output = "dummy"
    status = "success"

    if command.command == "mkdir":
        output = mkdir(filepath=command.arg1)
        if not output:
            output = f"Directory {command.arg1} already exists!"
            status = "danger"

    elif command.command == "ls":
        output = ls(filepath=command.arg1)
        status = "secondary"

    elif command.command == "rm":
        output = rm(filename=command.arg1)
        if not output:
            output = f"File '{command.arg1}' does not exist!"
            status = "danger"

    elif command.command == "cat":
        output = cat(filename=command.arg1)
        if not output:
            output = f"File '{command.arg1}' does not exist!"
            status = "danger"

    elif command.command == "put":
        output = put(filename=command.file_input, location=command.arg1, k=command.arg2)
        if not output:
            output = f"Directory '{command.arg1}' does not exist!"
            status = "danger"
    else:
        output = "Invalid Command! This shouldn't happen"
        status = "danger"

    response = namedtuple("Response", "output status")
    return response(output, status)

def run_analyses(analyses) -> str:
    """Given an analyses to run, will execute that analyses via partitionMapReduce() and get that result as an HTML string.
       NOTE: PLEASE MAKE SURE TO DEFINE A QUERY, DESC

    Args:
        analyses (str): Key dictating which analyses to run
        database (str): Database to use.

    Returns:
        str: HTML Output of analyses
    """
    if analyses == 'ana_1':
        query = "SELECT _ from _"
        desc = "Description"
        result = None

    if analyses == 'ana_2':
        query = "SELECT _ from _"
        desc = "Description"
        result = None

    if analyses == 'ana_3':
        query = "SELECT _ from _"
        desc = "Description"
        result = None

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
    map_inputs = f"<h2>Data passed into mapPartition()</h2>{repr_list_items(analyses_result.map_partition_inputs)}"
    map_outputs = f"<h2>Data returned from mapPartition()</h2>{note}{repr_list_items(analyses_result.map_partition_outputs)}<h4 style='color:blue;'></h4>"
    final_output = f"<h2>Final Output of Analyses</h2>{repr_list_items(analyses_result.reduce_output)}"
    html_repr = f"{header}{desc}{map_inputs}{map_outputs}{final_output}"
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