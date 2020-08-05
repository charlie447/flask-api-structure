from app import create_app, db
from app.models import User, Task

app = create_app()

@app.shell_context_processor
def make_flask_shell_context():
    """pre-import modules/variables like db, User for flask shell,
        which can test the database in the shell.
        Run `flask shell` command to get into shell and no need to import all the dependencies one by one.
    """
    return {'db': db, 'User': User, 'Task': Task}
