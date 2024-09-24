from django.shortcuts import redirect
from django.urls import resolve

from ..helpers.constants import PageNames, SessionContent


class CheckSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_url_name = resolve(request.path).url_name

        if request.method == "GET":
            if current_url_name != PageNames.ENTRY_POINT:
                pages_data = request.session.get(SessionContent.PAGES_DATA, None)
                if not pages_data:
                    return redirect(PageNames.ENTRY_POINT)

        token = request.session.get(SessionContent.TOKEN, None)
        if not token:
            return redirect(PageNames.ENTRY_POINT)

        return self.get_response(request)
