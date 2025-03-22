from django.views import View
from django.shortcuts import redirect
from django.conf import settings
from django.http import Http404

from core.helpers.constants import ApiEndpoints, SessionContent, PageNames, Defaults
from core.helpers.api_client import ApiClient
from core.helpers.session import Session


class BaseView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.context = None

    def dispatch(self, request, *args, **kwargs):
        page_name = kwargs.pop('page_name', None)

        if not page_name:
            raise Http404()

        current_user = request.session.get(SessionContent.CURRENT_USER, {})

        if not current_user and page_name != PageNames.LOGIN:
            return redirect(PageNames.LOGIN)

        menu_content = request.session.get(SessionContent.MENU_CONTENT, {})

        if not menu_content and page_name != PageNames.LOGIN:
            return redirect(PageNames.LOGIN)

        user_language = current_user.get('language', Defaults.LANGUAGE)
        user_theme = current_user.get('theme', Defaults.THEME)

        pages = request.session.get(SessionContent.PAGES, {})
        current_page = pages.get(page_name, {})
        current_page_language = current_page.get('language', Defaults.LANGUAGE)
        current_page_theme = current_page.get('theme', Defaults.THEME)

        if not current_page or user_language != current_page_language:
            page_content_url = f'{settings.API_URL}{ApiEndpoints.PAGE_CONTENT}{user_language}/{page_name}/'

            token = request.session.get(SessionContent.TOKEN, '')

            if not token:
                response = ApiClient.get(page_content_url)
            else:
                response = ApiClient.get(page_content_url, token=token)

            if response.status_code != 200:
                raise Http404()

            current_page = response.json()
            pages[page_name] = current_page

        elif user_theme != current_page_theme:
            current_page['theme'] = user_theme
            pages[page_name] = current_page

        Session.add(request, SessionContent.PAGES, pages)

        tabs = request.session.get(SessionContent.TABS, {})

        if ((page_name != PageNames.LOGIN) and
                (page_name != PageNames.INDEX) and
                (page_name not in tabs.keys())):
            tabs[page_name] = {
                'name': current_page['name'],
                'label': current_page['label'],
                'close': PageNames.INDEX
            }

        Session.add(request, SessionContent.TABS, tabs)

        self.context = {
            'page': current_page,
            'menu': menu_content,
            'tabs': tabs,
        }

        return super().dispatch(request, *args, **kwargs)
