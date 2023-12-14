from flask import Flask, request, jsonify
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Your Slack bot's access token
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json

    print(data)

    # Verify request came from Slack
    if data.get('type') == 'url_verification':
        return jsonify({'challenge': data.get('challenge')})
    
    # Handle the 'app_home_opened' event
    if data.get('event', {}).get('type') == 'app_home_opened':
        user_id = data['event']['user']
        send_welcome_message(user_id)

    return jsonify({'status': 'ok'})

@app.route('/github/webhook', methods=['POST'])
def github_webhook():
    payload = request.json

    print(payload)
    # Check if it's a push event
    # Check if it's a repository added event
    if 'repositories_added' in payload and payload['repositories_added']:
        for repo in payload['repositories_added']:
            repo_name = repo['name']
            channel_name = f'changelog-{repo_name}'
            create_slack_channel(channel_name)
    elif payload.get('commits'):
        # Log relevant details

        message = f"New commit made to repository: {payload['repository']['name']}\n" +\
            f"Commit message: {payload['head_commit']['message']}\n" +\
            f"Commit author: {payload['head_commit']['author']['name']}\n"
        
        slack_channel_name = f"#changelog-{payload['repository']['name']}"
        send_slack_message(slack_channel_name, message= message)
    return jsonify({'status': 'success'}), 200

def create_slack_channel(channel_name):
    url = 'https://slack.com/api/conversations.create'
    headers = {
        'Authorization': f'Bearer {SLACK_BOT_TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {'name': channel_name}
    response = requests.post(url, headers=headers, json=data)
    print(response.json()) 

def send_welcome_message(user_id):
    print("Sending welcome message to user_id: ", user_id)
    return send_slack_message(user_id, "Welcome to my bot!")

def send_slack_message(user_id, message):
    print("Sending welcome message to user_id: ", user_id)
    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {SLACK_BOT_TOKEN}'}
    payload = {
        'channel': user_id,
        'text': message
    }
    response = requests.post(url, headers=headers, json=payload)
    print(response.json())
    return response.json()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

