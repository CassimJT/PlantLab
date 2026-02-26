# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property


class AuthService(QObject):

    # ======================================================
    # Signals
    # ======================================================
    authenticationChanged = Signal(bool)
    userChanged = Signal()
    errorOccurred = Signal(str)

    # ======================================================
    # Init
    # ======================================================
    def __init__(self, parent=None):
        super().__init__(parent)

        self._is_authenticated = False
        self._token = None
        self._current_user = None

    # ======================================================
    # Properties
    # ======================================================

    # --- isAuthenticated ---
    @Property(bool, notify=authenticationChanged)
    def isAuthenticated(self):
        return self._is_authenticated

    def _setIsAuthenticated(self, value: bool):
        if self._is_authenticated == value:
            return
        self._is_authenticated = value
        self.authenticationChanged.emit(self._is_authenticated)

    # --- currentUser ---
    @Property(object, notify=userChanged)
    def currentUser(self):
        return self._current_user

    def _setCurrentUser(self, user):
        if self._current_user == user:
            return
        self._current_user = user
        self.userChanged.emit()

    # ======================================================
    # Public API (Business Logic – MVP Skeleton)
    # ======================================================

    @Slot(str, str)
    def login(self, email: str, password: str):
        """
        Trigger login flow via AuthApiClient.
        On success:
            - set token
            - set currentUser
            - set isAuthenticated = True
        """
        pass

    @Slot(str, str, str, str, int)
    def signin(self, fname: str, lname: str, email: str, password: str, phone: int):
        """ Local stratagy sign in """
        pass

    @Slot()
    def logout(self):
        """
        Clear authentication state.
        """
        pass

    # ======================================================
    # Internal Helpers (Token Handling)
    # ======================================================

    def _set_token(self, token: str):
        self._token = token

    def _clear_token(self):
        self._token = None

    def getToken(self):
        """
        Internal use by ApiClient to attach Authorization header.
        """
        return self._token
