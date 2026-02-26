# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject
import sqlite3
from pathlib import Path


class DBManager(QObject):

    # ======================================================
    # Init
    # ======================================================
    def __init__(self, db_name: str = "plantlab.db", parent=None):
        super().__init__(parent)

        self._db_path = Path(db_name)
        self._connection = None

    # ======================================================
    # Connection Handling
    # ======================================================

    def connect(self):
        """
        Open SQLite connection.
        """
        pass

    def close(self):
        """
        Close SQLite connection.
        """
        pass

    # ======================================================
    # Schema Setup
    # ======================================================

    def initialize(self):
        """
        Create required tables if they don't exist.
        """
        pass

    # ======================================================
    # Generic Execution Helpers
    # ======================================================

    def execute(self, query: str, params: tuple = ()):
        """
        Execute INSERT / UPDATE / DELETE.
        """
        pass

    def fetch_one(self, query: str, params: tuple = ()):
        """
        Execute SELECT and return single row.
        """
        pass

    def fetch_all(self, query: str, params: tuple = ()):
        """
        Execute SELECT and return multiple rows.
        """
        pass

    # ======================================================
    # Session-Specific Helpers (For AuthService)
    # ======================================================

    def save_session(self, user_data: dict, token: str):
        """
        Persist authenticated session.
        Expected user_data keys:
            id, name, employee_id, role
        """
        pass

    def load_session(self):
        """
        Load stored session.
        Return dict or None.
        """
        pass

    def clear_session(self):
        """
        Remove stored session.
        """
        pass
