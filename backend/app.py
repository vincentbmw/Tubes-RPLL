import os
from pyngrok import ngrok
from urllib.request import urlopen
from flask import Flask
from flask import render_template, jsonify, request, session
from dotenv import find_dotenv, dotenv_values
from controllers.login import login_blueprint
from controllers.register import register_blueprint
from controllers.database import DatabaseFactory, get_user_profile_data, initialize
from controllers.manage_profile import manage_profile_blueprint
from controllers.logout import logout_blueprint
from controllers.chats import chats_blueprint, get_chat_prompts, get_chats
from controllers.llm_config import setup_llm, connect_llm, run_query

app = Flask(__name__)
app.secret_key = "test123"

config = dotenv_values(find_dotenv())

app.register_blueprint(chats_blueprint)
app.register_blueprint(login_blueprint)
app.register_blueprint(register_blueprint)
app.register_blueprint(manage_profile_blueprint)
app.register_blueprint(logout_blueprint)


@app.route('/registerpage')
def registerpage():
    return render_template('register.html')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html')

@app.route('/chatpage')
def chatpage():
    chat_list, status_code = get_chats()

    return render_template('chat-page.html', chats=chat_list)

@app.route('/chatpage/<chat_id>')
def chatpage_with_id(chat_id):
    chat_list, status_code = get_chats()
    prompts_data, prompts_status_code = get_chat_prompts(chat_id)
    print(prompts_data)
    if prompts_status_code == 200 and prompts_data is not None:
        return render_template('chat-page-with-id.html', chats=chat_list, chat_id=chat_id, messages=prompts_data)
    else:
        return render_template('chat-page-with-id.html', chats=chat_list, chat_id=chat_id, messages=[])


@app.route('/api/query', methods=['POST'])
def api_query():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401 

        data = request.get_json()
        query_text = data.get('query')
        chat_id = data.get('chatId')
        if not query_text:
            return jsonify({'error': 'Missing "query" parameter'}), 400

        response = run_query(query_text, user_id, chat_id) 
        return jsonify({'response': str(response)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/profile', methods=['GET'])
def get_profile():
    profile_data, status_code = get_user_profile_data()
    if status_code == 200:
        return jsonify(profile_data), 200
    else:
        return profile_data, status_code

@app.route('/api/<chat_id>/prompts', methods=['GET'])
def get_prompts(chat_id):
    prompts_data, status_code = get_chat_prompts(chat_id)
    if status_code == 200:
        return jsonify(prompts_data), 200
    else:
        return prompts_data, status_code

if __name__ == '__main__':
    ip = urlopen('https://api.ipify.org').read().decode('utf-8')
    print(f"My public IP is '{ip}'. Make sure this IP is allowed to connect to cloud Atlas")

    mongodb_client = initialize(config.get('ATLAS_URI'))
    setup_llm(config.get('GOOGLE_API_KEY'))
    connect_llm(mongodb_client)

    public_url = ngrok.connect(5000).public_url
    print(f"ngrok tunnel opened at {public_url}")
    app.run(debug=False)