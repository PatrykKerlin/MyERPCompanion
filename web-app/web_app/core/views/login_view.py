import aiohttp
from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.http import Http404


class LoginView(View):
    def __init__(self):
        super().__init__()
        self.template = None
        self.user = None
        self.token = None

    def dispatch(self, request, *args, **kwargs):
        pages_data = request.session.get('pages_data', {})
        page = pages_data.get('user-login', None)

        if page:
            self.template = page.get('template')

    async def get(self, request):
        return render(request, self.template)

    async def post(self, request):
        login = request.POST.get('login')
        password = request.POST.get('password')

        api_url = f'{settings.API_URL}/token/'

        async with aiohttp.ClientSession() as session:
            data = {
                'login': login,
                'password': password
            }
            async with session.post(api_url, data=data) as response:
                if response.status == 200:
                    result = await response.json()
                    token = result.get('token')
                    request.session['token'] = token
                    context = {'token': token}
                else:
                    context = {'error': response.status}

                return render(request, self.template, context)
