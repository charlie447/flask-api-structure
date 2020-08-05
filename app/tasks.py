from app import create_app

from rq import get_current_job
from app import db
from app.models import Task

# needs to create its own application instance if the task functions need it.
app = create_app()
# pushing a context makes the application be the "current" application instance
app.app_context().push()


def _set_task_progress(progress):
    job = get_current_job()
    if job:
        job.meta['progress'] = progress
        job.save_meta()
        # get task from db
        task = Task.query.get(job.get_id())
        # push notifications to the client
        # task.user.add_notification('task_progress', {'task_id': job.get_id(),
        #                                              'progress': progress})
        if progress >= 100:
            task.complete = True
        db.session.commit()
