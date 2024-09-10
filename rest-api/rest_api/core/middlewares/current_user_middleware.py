import threading


class CurrentUserMiddleware:
    __thread_local = threading.local()

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self.__thread_local.user = request.user
        response = self.get_response(request)
        return response

    @classmethod
    def get_current_user(cls):
        current_user = getattr(cls.__thread_local, 'user', None)
        if not current_user or not current_user.is_authenticated:
            return None
        return current_user
