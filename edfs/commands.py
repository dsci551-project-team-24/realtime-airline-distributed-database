# Placeholder for commands.py, a file that will contain definitions for commands used by edfs
from edfs.tools import *
import pandas as pd
import numpy as np
import json
from uuid import uuid4
from functools import reduce



def mkdir(filepath: str) -> str:
    """Connects to database and creates proper file structure by writing a object to database.

    Args:
        filepath (str): Logical path to file in database from root.

    Return:
        str: Representation of the object that was written.
    """
    
    raise NotImplementedError("Function has not been implemented yet")

    return filepath


def ls(filepath: str) -> str:
    """Connects to the database and returns the contents of the database at the location given by 'filepath'.

    Args:
        filepath (str): Logical path to file in database from root.

    Return:
        str: Object located at the filepath, if it exists.
    """
    raise NotImplementedError("Function has not been implemented yet")



def cat(filename: str) -> str:
    """Connects to database and gets the contents of a single file at that location.

    Args:
        filename (str): Logical path to file in database from root.

    Return:
        str: Contents of the file located at the filepath, if it exists.
    """
    raise NotImplementedError("Function has not been implemented yet")
    return full_file

def rm(filename: str) -> bool:
    """Connects to the chosen database and DELETS the file located at the given string, without modifying the directories above the file.

    Args:
        filename (str): Logical path to file in database from root.

    Return:
        bool: Whether or not the operation was successful.
    """
    raise NotImplementedError("Function has not been implemented yet")
    return operation_successful


def put(filename: str, location: str, k: int) -> bool:
    """Calls the partition() function and uses the output to write a json object to the database at the location specified.

    Args:
        filename (str): Logical path to file in database from root.
        location (str): Location to write specific partition of file.
        k (int): Number of partitions that the file should be divided into.

    Returns:
        bool: Whether the operation was successful.
    """
    raise NotImplementedError("Function has not been implemented yet")
    return operation_successful
