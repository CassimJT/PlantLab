# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Property


class User(QObject):

    # ======================================================
    # Signals
    # ======================================================
    userChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._id = ""
        self._name = ""
        self._employee_id = ""
        self._role = ""

    # ======================================================
    # Qt Properties (Read-Only)
    # ======================================================

    @Property(str, notify=userChanged)
    def id(self):
        return self._id

    @Property(str, notify=userChanged)
    def name(self):
        return self._name

    @Property(str, notify=userChanged)
    def employeeId(self):
        return self._employee_id

    @Property(str, notify=userChanged)
    def role(self):
        return self._role

    # ======================================================
    # Internal Setters (Used by AuthService)
    # ======================================================

    def _setId(self, value: str):
        self._id = value

    def _setName(self, value: str):
        self._name = value

    def _setEmployeeId(self, value: str):
        self._employee_id = value

    def _setRole(self, value: str):
        self._role = value

    def _emitChanged(self):
        self.userChanged.emit()
