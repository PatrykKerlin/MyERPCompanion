from ..base.base_manager import BaseManager


class ContentManager(BaseManager):
    def by_page(self, page_id):
        return self.get_queryset().filter(page_id=page_id)
