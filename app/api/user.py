from app.api import bp


@bp.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    """Return a user.

    Args:
        id (int): the user id.
    """
    pass


@bp.route('/users', methods=['GET'])
def get_users():
    """Return the collection of all users.
    """
    pass


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
