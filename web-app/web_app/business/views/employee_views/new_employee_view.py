from django.views import View
from django.shortcuts import render, redirect
from django.conf import settings

from base.views.base_view import BaseView
from core.helpers.constants import PageNames, SessionContent, ApiEndpoints
from core.helpers.api_client import ApiClient
from core.helpers.session import Session
from core.helpers.form_converter import FormConverter
from ...forms.employee_form import EmployeeForm


class NewEmployeeView(BaseView):
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, page_name=PageNames.NEW_EMPLOYEE, *args, **kwargs)

    def get(self, request):
        form = EmployeeForm()
        self.context.update({'form': form})
        return render(request, self.context['page']['template'], self.context)

    def post(self, request):
        form = EmployeeForm(request.POST)

        if form.is_valid():
            url = settings.API_URL + ApiEndpoints.EMPLOYEE
            data = FormConverter.convert(form)
            response = ApiClient.post(url, data, Session.get(request, SessionContent.TOKEN))

            if response.status_code == 201:
                return redirect(PageNames.INDEX)
            else:
                form.add_error(None, "Failed to create employee in API.")
        return render(request, 'web_app/add_employee.html', {'form': form})
