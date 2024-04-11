import time
from typing import Union, Dict

import mysql.connector
from loguru import logger
from mysql.connector import Error
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection


class MySqlClient:
    host: str
    username: str
    password: str
    connection_pool: Dict[str, Union[PooledMySQLConnection, MySQLConnectionAbstract]]

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.connection_pool = {}

    def __connect(self, database: str) -> bool:
        # attempt to connect to the database with 5 retries with a 5 second delay
        logger.info(f"Attempting to connect to {self.host} using {self.username}")
        for i in range(5):
            try:
                self.connection_pool[database] = mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    database=database
                )
            except Error as e:
                logger.error(f"Failed to connect to {self.host} using {self.username} with error: {e}")
                logger.info(f"Retrying in 5 seconds.")
                time.sleep(5)
                continue
            logger.info(f"Connected to {self.host} using {self.username}")
            return True

    def close_connections(self) -> None:
        for database, connection in self.connection_pool.items():
            connection.close()
            logger.info(f"Closed connection to {self.host} for database {database}")

    def create_database(self, database: str) -> bool:
        # create a connection to the default database
        if not self.__connect(""):
            logger.error(f"Failed to connect to {self.host} for database creation")
            return False
        logger.info(f"Creating database {database} on {self.host}")
        cursor = self.connection_pool[""].cursor()
        try:
            # check if the database exists and create it if it does not
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database}")
        except Error as e:
            logger.error(f"Failed to create database {database} on {self.host} with error: {e}")
            return False

    def execute_ddl_query(self, query: str, database: str) -> bool:
        if database not in self.connection_pool:
            if not self.__connect(database):
                logger.error(f"Failed to connect to {self.host} for database {database}")
                return False
        logger.info(f"Executing DDL query on {self.host}")
        cursor = self.connection_pool[database].cursor()
        try:
            cursor.execute(query)
        except Error as e:
            logger.error(f"Failed to execute DDL query on {self.host} with error: {e}")
            return False
        return True

    def execute_dml_query(self, query: str, database: str) -> bool:
        if database not in self.connection_pool:
            if not self.__connect(database):
                logger.error(f"Failed to connect to {self.host} for database {database}")
                return False
        logger.info(f"Executing DML query on {self.host}")
        cursor = self.connection_pool[database].cursor()
        try:
            cursor.execute(query)
            self.connection_pool[database].commit()
        except Error as e:
            logger.error(f"Failed to execute DML query on {self.host} with error: {e}")
            return False
        return True

    def execute_select_query(self, query: str, database: str) -> list:
        if database not in self.connection_pool:
            if not self.__connect(database):
                logger.error(f"Failed to connect to {self.host} for database {database}")
                raise Exception(f"Failed to connect to {self.host} for database {database}")
        logger.info(f"Executing DML query on {self.host}")
        cursor = self.connection_pool[database].cursor()
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return result
        except Error as e:
            logger.error(f"Failed to execute DML query on {self.host} with error: {e}")
            raise e
