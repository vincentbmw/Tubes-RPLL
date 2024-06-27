import os
from pyngrok import ngrok
from urllib.request import urlopen
from flask import Flask
from flask import jsonify, request, session
from dotenv import find_dotenv, dotenv_values
from controllers.login import login_blueprint
from controllers.register import register_blueprint
from controllers.database import initialize  
from controllers.manage_profile import manage_profile_blueprint
from controllers.logout import logout_blueprint
from controllers.llm_config import setup_llm, connect_llm, run_query 

app = Flask(__name__)
app.secret_key = "test123"

# Load konfigurasi dari .env
config = dotenv_values(find_dotenv())

# Registrasi blueprint
app.register_blueprint(login_blueprint)
app.register_blueprint(register_blueprint)
app.register_blueprint(manage_profile_blueprint)
app.register_blueprint(logout_blueprint)

# Rute untuk query (contoh)
@app.route('/api/query', methods=['POST'])
def api_query():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401 

        data = request.get_json()
        query_text = data.get('query')
        if not query_text:
            return jsonify({'error': 'Missing "query" parameter'}), 400

        response = run_query(query_text, user_id) 
        return jsonify({'response': str(response)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    ip = urlopen('https://api.ipify.org').read().decode('utf-8')
    print(f"My public IP is '{ip}'. Make sure this IP is allowed to connect to cloud Atlas")
    mongodb_client = initialize(config.get('ATLAS_URI'))
    setup_llm(config.get('GOOGLE_API_KEY'))
    connect_llm(mongodb_client)
    public_url = ngrok.connect(5000).public_url
    print(f"ngrok tunnel opened at {public_url}")
    app.run(debug=False)