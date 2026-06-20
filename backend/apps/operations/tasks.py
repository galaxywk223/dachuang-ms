try:
    from config.celery import app
except Exception:  # pragma: no cover
    app = None

from .services import DataCenterService


if app:

    @app.task(name="operations.run_import_task")
    def run_import_task(task_id):
        DataCenterService.run_import_task(task_id)
