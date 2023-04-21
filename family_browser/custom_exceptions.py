class FamilyNotFound(Exception):
    def __init__(self, iin: str):
        super().__init__(f'Family with iin {iin} not found')
        self.iin = iin


class WrongPassword(Exception):
    def __init__(self, username: str):
        super().__init__(f'Wrong password for user {username}')
        self.username = username


class WrongIIN(Exception):
    def __init__(self, iin: str):
        super().__init__(f'Wrong iin {iin}')
        self.iin = iin


class FamilyNotInList(Exception):
    def __init__(self, iin: str):
        super().__init__(f'Family with iin {iin} not in list')
        self.iin = iin
