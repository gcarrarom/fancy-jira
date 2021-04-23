class Sorry(Exception):
    def __init__(self, message):
        self.args = ('Oh hey dere! Sorry bud, but ' + message + '!',)