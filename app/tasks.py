from app import create_app

# needs to create its own application instance if the task functions need it.
app = create_app()
# pushing a context makes the application be the "current" application instance
app.app_context().push()

