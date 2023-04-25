class FamilyNotFound(Exception):
    def __init__(self):
        super().__init__(f'Family or person not found')
        self.error_msg = 'ИИН не найден. Проверьте ИИН'


class WrongPassword(Exception):
    def __init__(self):
        super().__init__(f'Wrong password')
        self.error_msg = 'Неправильный пароль. Свяжитесь с администраторами'


class WrongIIN(Exception):
    def __init__(self):
        super().__init__('Wrong iin')
        self.error_msg = 'Неверный ИИН. ИИН должен состоять из 12 цифр без букв и пробелов'

