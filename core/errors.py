from core.localization import _


class ValidationException(Exception):
    def __init__(self, *args, **kwargs):
        self.messages = args
        self.obj = kwargs

