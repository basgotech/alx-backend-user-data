#!/usr/bin/env python3
"""
Encrypting passwords for a database using bcrypt
"""
import bcrypt


def hash_password(password: str) -> bytes:
    """
    Hashes a password using bcrypt.
    """
    enc = password.encode()
    hash_tble = bcrypt.hashpw(enc, bcrypt.gensalt())

    return hash_tble


def is_valid(hashed_password: bytes, password: str) -> bool:
    """
    Checks if the provided password matches the hashed password.
    """
    istru = False
    encoded_data = password.encode()
    if bcrypt.checkpw(encoded_data, hashed_password):
        istru = True
    return istru
