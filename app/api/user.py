from app.api import bp

from flask import jsonify, request
from app.models import User


@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """Return a user.

    Args:
        id (int): the user id.
    """
    return jsonify(User.query.get_or_404(id).to_dict())


@bp.route('/users', methods=['GET'])
def get_users():
    """Return the collection of all users.
    """
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    data = User.to_collection_dict(User.query, page, per_page, 'api.get_users')
    return jsonify(data)


@bp.route('/users', methods=['POST'])
def create_user():
    """	Register a new user account.
    """
    pass


@bp.route('/users/<int:id>', methods=['PUT'])
def update_user(id):
    """	Modify a user.

    Args:
        id (int): User ID.
    """
    pass
