from django.apps import AppConfig


class MysummarizerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mysummarizer'
class TextsummaryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'textsummary'

    def ready(self):
        from .nltk_setup import ensure_nltk_resources
        ensure_nltk_resources()
