from django.views import View
from django.shortcuts import render

from base.views.base_view import BaseView
from ..helpers.constants import PageNames, SessionContent


class IndexView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, page_name=PageNames.INDEX, *args, **kwargs)

    def get(self, request):
        return render(request, self.context['page']['template'], self.context)
