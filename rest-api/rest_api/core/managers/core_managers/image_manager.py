from ..abstract_managers.base_manager import BaseManager


class ImageManager(BaseManager):
    def by_page(self, page_id):
        return self.get_queryset().filter(page_id=page_id)
