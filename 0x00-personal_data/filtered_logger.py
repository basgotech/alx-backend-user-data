#!/usr/bin/env python3
"""
Module for handling Personal Data
"""
from typing import List
import re
import logging
from os import environ
import mysql.connector


PII_FIELDS = ("name", "email", "phone", "ssn", "password")


def filter_datum(fields: List[str], redaction: str,
                 message: str, separator: str) -> str:
    """ Log message with specified fields obfuscated """
    for x in fields:
        message = re.sub(f'{x}=.*?{separator}',
                         f'{x}={redaction}{separator}', message)
    return message


def get_logger() -> logging.Logger:
    """ function that takes no arguments and
    returns a logging.Logger object """
    logger_hol = logging.getLogger("user_data")
    logger_hol.setLevel(logging.INFO)
    logger_hol.propagate = False

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(RedactingFormatter(list(PII_FIELDS)))
    logger_hol.addHandler(stream_handler)

    return logger_hol


def get_db() -> mysql.connector.connection.MySQLConnection:
    """ function that returns a connector to the database """
    username = environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    pwd = environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    host = environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db = environ.get("PERSONAL_DATA_DB_NAME")

    cur = mysql.connector.connection.MySQLConnection(user=username,
                                                     password=pwd,
                                                     host=host,
                                                     database=db)
    return cur


def main():
    """
    Obtain a database connection using get_db and retrieves all rows
    """
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users;")
    field_names = [i[0] for i in cursor.description]

    logger = get_logger()

    for data in cursor:
        str_row = ''.join(f'{f}={str(r)}; ' for r, f in zip(data, field_names))
        logger.info(str_row.strip())

    cursor.close()
    db.close()


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class
        """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: List[str]):
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """ Filters values in incoming log records using filter_datum """
        record.msg = filter_datum(self.fields, self.REDACTION,
                                  record.getMessage(), self.SEPARATOR)
        return super(RedactingFormatter, self).format(record)


if __name__ == '__main__':
    main()
