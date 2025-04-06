class TokenModel:
    def __init__(self):
        self.__token = None

    @property
    def token(self):
        return self.__token

    @token.setter
    def token(self, token):
        self.__token = token
