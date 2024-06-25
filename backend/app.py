import os
from flask import Flask
from dotenv import find_dotenv, dotenv_values
from login import login_blueprint
from register import register_blueprint
from database import initialize  
from llm_config import setup_llm, connect_llm, run_query 

app = Flask(__name__)

# Load konfigurasi dari .env
config = dotenv_values(find_dotenv())

# Registrasi blueprint
app.register_blueprint(login_blueprint)
app.register_blueprint(register_blueprint)

# Inisialisasi database dan LLM saat aplikasi dijalankan
@app.before_first_request
def initialize_app():
    mongodb_client = initialize(config.get('ATLAS_URI'))
    setup_llm(config.get('GOOGLE_API_KEY'))
    connect_llm(mongodb_client)

# Rute untuk query (contoh)
@app.route('/api/query', methods=['POST'])
def api_query():
    try:
        data = request.get_json()
        query_text = data.get('query')
        if not query_text:
            return jsonify({'error': 'Missing "query" parameter'}), 400

        response = run_query(query_text)
        return jsonify({'response': str(response)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    from pyngrok import ngrok
    from urllib.request import urlopen
    ip = urlopen('https://api.ipify.org').read().decode('utf-8')
    print(f"My public IP is '{ip}'. Make sure this IP is allowed to connect to cloud Atlas")
    public_url = ngrok.connect(5000).public_url
    print(f"ngrok tunnel opened at {public_url}")
    app.run(debug=True)