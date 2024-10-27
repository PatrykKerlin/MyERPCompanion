from django.views import View
from django.shortcuts import render, redirect

from base.views.base_view import BaseView
from ..helpers.constants import PageNames, SessionContent
from ..helpers.session import Session


class IndexView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        if request.method == 'POST' and 'tab_name' in request.POST:
            tab_name = request.POST.get('tab_name')
            tabs = Session.get(request, SessionContent.TABS)

            if tab_name in tabs.keys():
                del tabs[tab_name]
                Session.add(request, SessionContent.TABS, tabs)
            return redirect(PageNames.INDEX)
        return super().dispatch(request, page_name=PageNames.INDEX, *args, **kwargs)

    def get(self, request):
        return render(request, self.context['page']['template'], self.context)
