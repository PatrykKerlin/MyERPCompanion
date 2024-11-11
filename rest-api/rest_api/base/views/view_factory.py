from base.views import BaseView


class ViewFactory:
    @staticmethod
    def get(Model, serializer):
        class NewView(BaseView):
            queryset = Model.objects.all()
            serializer_class = serializer

        return NewView
