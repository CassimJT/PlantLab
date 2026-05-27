# This Python file uses the following encoding: utf-8
from PySide6.QtCore import QObject, Signal, Slot, Property
from .AuthApiClient import AuthApiClient
from .AppSettings import AppSettings


class AuthService(QObject):

    # ======================================================
    # Signals
    # ======================================================
    authenticationChanged = Signal(bool)
    userChanged = Signal()
    errorOccurred = Signal(str)
    loginCompleted = Signal(dict)

    # ======================================================
    # Init
    # ======================================================
    def __init__(self, parent=None):
        super().__init__(parent)

        self._is_authenticated = False
        self._token = None
        self._current_user = None
        self._api_client = AuthApiClient(self)
        self._settings = AppSettings.instance()

        # Set base URL
        self._api_client.baseUrl = "https://plantdoctor-api.onrender.com/api"

        # Connect API client signals
        self._api_client.requestFinished.connect(self._on_request_finished)
        self._api_client.requestFailed.connect(self._on_request_failed)

        # Restore session if token exists (one-time login)
        self._restore_session()

    # ======================================================
    # Properties
    # ======================================================

    @Property(bool, notify=authenticationChanged)
    def isAuthenticated(self):
        return self._is_authenticated

    def _setIsAuthenticated(self, value: bool):
        if self._is_authenticated == value:
            return
        self._is_authenticated = value
        self.authenticationChanged.emit(self._is_authenticated)
        self._settings.setLoggedIn(value)

    @Property(object, notify=userChanged)
    def currentUser(self):
        return self._current_user

    def _setCurrentUser(self, user):
        if self._current_user == user:
            return
        self._current_user = user
        self.userChanged.emit()

    # ======================================================
    # Session Management
    # ======================================================

    def _restore_session(self):
        """Restore user session from saved settings (one-time login)"""
        if self._settings.isLoggedIn and self._settings.token:
            self._token = self._settings.token
            self._api_client.token = self._token
            self._setIsAuthenticated(True)

            # Restore user from settings
            user = {
                "email": self._settings.userEmail,
                "displayName": self._settings.userDisplayName
            }
            if user["email"]:
                self._setCurrentUser(user)
                print(f"[AuthService] Session restored for: {user.get('email')}")

    # ======================================================
    # Public API
    # ======================================================

    @Slot(str, str)
    def login(self, email: str, password: str):
        """Login - happens once, then remembered forever"""
        print(f"[AuthService] Login attempt for: {email}")
        payload = {
            "email": email,
            "password": password
        }
        self._api_client.post("/auth/login", payload)

    @Slot()
    def logout(self):
        """Manual logout - clears all saved data"""
        print("[AuthService] Logout")
        self._clear_token()
        self._setCurrentUser(None)
        self._setIsAuthenticated(False)
        self._settings.clearAll()

    # ======================================================
    # Internal Handlers
    # ======================================================

    def _on_request_finished(self, endpoint: str, data: dict):
        if "/auth/login" in endpoint:
            self._handle_login_response(data)

    def _on_request_failed(self, endpoint: str, error: str):
        print(f"[AuthService] Request failed: {endpoint} - {error}")
        self.errorOccurred.emit(error)

    def _handle_login_response(self, data: dict):
        success = data.get("success", False)

        if success:
            token = data.get("token")
            user = data.get("user", {})

            if token:
                self._set_token(token)
                self._api_client.token = token

                # Create simplified user object for display
                display_name = user.get("displayName") or f"{user.get('firstName', '')} {user.get('lastName', '')}".strip() or user.get("email")
                user_obj = {
                    "email": user.get("email"),
                    "displayName": display_name
                }

                self._setCurrentUser(user_obj)
                self._setIsAuthenticated(True)

                # Save to persistent settings (one-time login)
                self._settings.setToken(token)
                self._settings.setUser(user.get("email", ""), display_name)

                self.loginCompleted.emit(user_obj)
                print(f"[AuthService] Login successful for: {user.get('email')}")
            else:
                self.errorOccurred.emit("No token received")
        else:
            error_msg = data.get("message", "Login failed")
            self.errorOccurred.emit(error_msg)

    # ======================================================
    # Token Handling
    # ======================================================

    def _set_token(self, token: str):
        self._token = token

    def _clear_token(self):
        self._token = None
        self._api_client.token = None

    def getToken(self):
        return self._token