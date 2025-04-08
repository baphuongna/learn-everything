from django.apps import AppConfig


class LearningGoalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'learning_goals'
    verbose_name = 'Mục tiêu học tập'

    def ready(self):
        import learning_goals.signals
