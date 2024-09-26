from django.views import View
from django.shortcuts import render

from ..abstract_views.base_view import BaseView
from ...helpers.constants import PageNames, SessionContent


class IndexView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, page_name=PageNames.INDEX, *args, **kwargs)

    def get(self, request):
        token = request.session.get(SessionContent.TOKEN, None)
        user = request.session.get(SessionContent.CURRENT_USER, None)

        self.context.update({'token': token, 'user': user})

        return render(request, self.page['template'], self.context)