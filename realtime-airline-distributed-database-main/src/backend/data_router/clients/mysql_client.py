import time
from typing import Union

import mysql.connector
from loguru import logger
from mysql.connector import Error
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.pooling import PooledMySQLConnection


class MySqlClient:
    host: str
    username: str
    password: str
    connection: Union[PooledMySQLConnection, MySQLConnectionAbstract]

    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.__connect()

    def __connect(self) -> bool:
        # attempt to connect to the database with 5 retries with a 5 second delay
        logger.info(f"Attempting to connect to {self.host} using {self.username}")
        for i in range(5):
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password
                )
            except Error as e:
                logger.error(f"Failed to connect to {self.host} using {self.username} with error: {e}")
                logger.info(f"Retrying in 5 seconds.")
                time.sleep(5)
                continue
            logger.info(f"Connected to {self.host} using {self.username}")
            return True

    def close_connection(self) -> bool:
        logger.info(f"Attempting to disconnect from {self.host}")
        try:
            self.connection.close()
        except Error as e:
            logger.error(f"Failed to disconnect from {self.host} with error: {e}")
            return False
        logger.info(f"Disconnected from {self.host}")
        return True

    def execute_ddl_query(self, query: str) -> bool:
        logger.info(f"Executing DDL query on {self.host}")
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
        except Error as e:
            logger.error(f"Failed to execute DDL query on {self.host} with error: {e}")
            return False
        return True

    def execute_dml_query(self, query: str) -> bool:
        logger.info(f"Executing DML query on {self.host}")
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
        except Error as e:
            logger.error(f"Failed to execute DML query on {self.host} with error: {e}")
            return False
        return True

    def execute_select_query(self, query: str) -> list:
        logger.info(f"Executing SELECT query on {self.host}")
        cursor = self.connection.cursor()
        try:
            cursor.execute(query)
        except Error as e:
            logger.error(f"Failed to execute SELECT query on {self.host} with error: {e}")
            return []
        return cursor.fetchall()


