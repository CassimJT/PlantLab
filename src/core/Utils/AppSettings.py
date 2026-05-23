from PySide6 import QtCore


class AppSettings(QtCore.QObject):

    _instance = None

    loginChanged = QtCore.Signal()
    tokenChanged = QtCore.Signal()
    userChanged = QtCore.Signal()
    rememberMeChanged = QtCore.Signal()
    languageChanged = QtCore.Signal()

    def __init__(self, parent=None):

        if AppSettings._instance is not None:
            raise Exception(
                "AppSettings is a singleton."
                "Use AppSettings.instance()"
            )

        super().__init__(parent)

        self._settings = QtCore.QSettings(
            "MyCompany",
            "PlantDoctor"
        )

    @classmethod
    def instance(cls):

        if cls._instance is None:
            cls._instance = AppSettings()

        return cls._instance

    # ---------------- LOGIN ----------------

    @QtCore.Property(bool, notify=loginChanged)
    def isLoggedIn(self):

        return self._settings.value(
            "auth/isLoggedIn",
            False,
            type=bool
        )

    @QtCore.Slot(bool)
    def setLoggedIn(self, loggedIn):

        if self.isLoggedIn == loggedIn:
            return

        self._settings.setValue(
            "auth/isLoggedIn",
            loggedIn
        )

        self.loginChanged.emit()

    # ---------------- REMEMBER ME (always true for desktop) ----------------

    @QtCore.Property(bool, notify=rememberMeChanged)
    def rememberMe(self):
        # Default to True for desktop app
        return self._settings.value(
            "auth/rememberMe",
            True,
            type=bool
        )

    @QtCore.Slot(bool)
    def setRememberMe(self, remember):

        if self.rememberMe == remember:
            return

        self._settings.setValue(
            "auth/rememberMe",
            remember
        )

        self.rememberMeChanged.emit()

    # ---------------- TOKEN ----------------

    @QtCore.Property(str, notify=tokenChanged)
    def token(self):

        return self._settings.value(
            "auth/token",
            "",
            type=str
        )

    @QtCore.Slot(str)
    def setToken(self, token):

        if self.token == token:
            return

        self._settings.setValue(
            "auth/token",
            token
        )

        self.tokenChanged.emit()

    def clearToken(self):
        self._settings.remove("auth/token")
        self.tokenChanged.emit()

    # ---------------- USER ----------------

    @QtCore.Property(str, notify=userChanged)
    def userEmail(self):

        return self._settings.value(
            "auth/userEmail",
            "",
            type=str
        )

    @QtCore.Property(str, notify=userChanged)
    def userDisplayName(self):

        return self._settings.value(
            "auth/userDisplayName",
            "",
            type=str
        )

    @QtCore.Slot(str, str)
    def setUser(self, email: str, displayName: str):

        self._settings.setValue("auth/userEmail", email)
        self._settings.setValue("auth/userDisplayName", displayName)
        self.userChanged.emit()

    def clearUser(self):
        self._settings.remove("auth/userEmail")
        self._settings.remove("auth/userDisplayName")
        self.userChanged.emit()

    # ---------------- LANGUAGE ----------------

    @QtCore.Property(str, notify=languageChanged)
    def language(self):

        return self._settings.value(
            "app/language",
            "en",
            type=str
        )

    @QtCore.Slot(str)
    def setLanguage(self, language):

        if self.language == language:
            return

        self._settings.setValue(
            "app/language",
            language
        )

        self.languageChanged.emit()

    # ---------------- HELPER ----------------

    def clearAll(self):
        """Clear all settings (logout)"""
        self.setLoggedIn(False)
        self.clearToken()
        self.clearUser()