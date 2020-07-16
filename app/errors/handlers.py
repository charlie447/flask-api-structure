from app.errors import bp
from app import db
from app.api.errors import error_response as api_error_response

from flask import render_template, request


def wants_json_response():
    """compares the preference for JSON or HTML selected by the client in their list of preferred formats.
        If JSON rates higher than HTML, then I return a JSON response.
        Otherwise I'll return the original HTML responses based on templates.
    Returns:
        boolean:
    """
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']

@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404

@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html'), 500
