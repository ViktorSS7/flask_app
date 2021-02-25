from core.localization import _


class ValidationException(Exception):
    def __init__(self, message):
        self.message = message

