from datetime import date
from decimal import Decimal


class FormConverter:
    @staticmethod
    def convert(form):
        return {
            key: (
                value.isoformat() if isinstance(value, date) else
                float(value) if isinstance(value, Decimal) else
                value
            )
            for key, value in form.cleaned_data.items()
        }
