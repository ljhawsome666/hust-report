from django.apps import AppConfig


class BookstoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookstore'

    def ready(self):
        import bookstore.signals  # 替换为实际的 app 名称