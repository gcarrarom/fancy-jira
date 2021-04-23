from click import BadParameter

class Sorry(BadParameter):
    def __init__(self, message):
        super().__init__('Oh hey there! Sorry bud, but ' + message + '!')