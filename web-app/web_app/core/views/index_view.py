import aiohttp
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings


class IndexView(View):
    template_name = 'user/index.html'

    async def get(self, request):
        token = request.session.get('token')
        if token:
            api_url = f'{settings.API_URL}/api/current-user/'
            headers = {'Authorization': f'Bearer {token}'}

            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        # Użytkownik pobrany poprawnie
                        user_data = await response.json()
                        return redirect('main_page')  # Przekierowanie na stronę główną
                    else:
                        # Token jest nieprawidłowy lub wygasł, usuń token z sesji
                        del request.session['token']
                        return redirect('login')

        # Jeśli nie ma tokena w sesji, pokaż stronę powitalną z przyciskiem logowania
        return render(request, self.template_name)
