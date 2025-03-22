class Session:
    @staticmethod
    def add(request, key, value):
        request.session[key] = value
        request.session.modified = True

    @staticmethod
    def get(request, key, default=None):
        return request.session.get(key, default)
