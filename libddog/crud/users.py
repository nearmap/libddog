class UserIdentity:
    def __init__(
        self, *, handle: str, email: str, name: str, app_key_name: str
    ) -> None:
        self.handle = handle
        self.email = email
        self.name = name
        self.app_key_name = app_key_name
