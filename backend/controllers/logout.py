from flask import Blueprint, session, jsonify, redirect, url_for

logout_blueprint = Blueprint('logout', __name__)

@logout_blueprint.route('/logout', methods=['POST'])
def logout():
    try:
        session.pop('user_id', None)

        return redirect(url_for('loginpage'))

    except Exception as e:
        return jsonify({'error': str(e)}), 500