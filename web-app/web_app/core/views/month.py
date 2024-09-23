from django.http import Http404
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods


@method_decorator(require_http_methods(['GET']), name='dispatch')
class MonthView(View):
    month_dict = {
        'jan': 'January',
        'feb': 'February',
        'mar': 'March',
        'apr': 'April',
        'may': 'May',
    }

    def get(self, request, month):
        try:
            text = self.month_dict[month]
            sample_list = ['one', 'two', 'three']
            return render(request, 'month.html', {
                'text': text,
                'month': month,
                'sample_list': sample_list
            })
        except KeyError:
            raise Http404()
