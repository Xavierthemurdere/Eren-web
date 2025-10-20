import os
import json

from flask import Flask, request, jsonify, Response
import requests

app = Flask(__name__)

DISCORD_API = 'https://discord.com/api/v10'
# Optional: set the user id here as a default; front-end also passes it.
DEFAULT_USER = '1228657207034380343'

@app.route('/', methods=['GET'])
def handler():
    user_id = request.args.get('user_id', DEFAULT_USER)
    token = os.environ.get('DISCORD_BOT_TOKEN')

    if not token:
        # No token — return minimal info and an explanation
        return jsonify({
            'error': 'No bot token configured. Set DISCORD_BOT_TOKEN in Vercel environment variables to show username & avatar.'
        }), 200

    headers = {'Authorization': f'Bot {token}'}
    try:
        r = requests.get(f"{DISCORD_API}/users/{user_id}", headers=headers, timeout=6)
    except Exception as e:
        return jsonify({'error': 'Failed to contact Discord API.'}), 502

    if r.status_code != 200:
        # pass back the error
        return jsonify({'error': f'Discord API returned {r.status_code}'}), r.status_code

    u = r.json()
    # build avatar url
    avatar = u.get('avatar')
    if avatar:
        # choose animated if starts with a_ prefix
        if avatar.startswith('a_'):
            avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.gif?size=512"
        else:
            avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar}.png?size=512"
    else:
        avatar_url = None

    # NOTE: presence is not available from this endpoint. We return null for presence.
    payload = {
        'id': u.get('id'),
        'username': u.get('username'),
        'discriminator': u.get('discriminator'),
        'avatar_url': avatar_url,
        'presence': None
    }
    return jsonify(payload)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
