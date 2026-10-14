"""Password hashing, registration and login."""
import hashlib
import hmac
import os

import mysql.connector

from db import run_query


def hash_password(password, salt=None):
    salt = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)
    return salt.hex() + "$" + digest.hex()


def verify_password(password, stored):
    salt_hex, _ = stored.split("$")
    return hmac.compare_digest(hash_password(password, bytes.fromhex(salt_hex)), stored)


def register(username, password):
    """Creates a customer account. Returns True on success."""
    try:
        run_query("INSERT INTO users (username, password, role) VALUES (%s,%s,'customer')",
                  (username, hash_password(password)))
        return True
    except mysql.connector.IntegrityError:
        return False


def login(username, password):
    """Returns (user_id, role) if credentials are valid, else None."""
    rows = run_query("SELECT user_id, password, role FROM users WHERE username=%s",
                     (username,), fetch=True)
    if rows and verify_password(password, rows[0][1]):
        return rows[0][0], rows[0][2]
    return None
