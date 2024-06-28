from flask import Blueprint, session, jsonify

logout_blueprint = Blueprint('logout', __name__)

@logout_blueprint.route('/api/logout', methods=['POST'])
def logout():
    """Melakukan logout user dengan menghapus session.
    """
    try:
        session.pop('user_id', None)
        return jsonify({'message': 'Logout successful'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500