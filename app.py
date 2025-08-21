import os
import datetime
from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "3ds-discord-secret-key")

# Configuration des sessions pour compatibilité 3DS - approche alternative
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=False,  # Désactiver pour 3DS
    SESSION_COOKIE_SAMESITE=None,   # Pas de restriction
    SESSION_COOKIE_PATH='/',
    SESSION_COOKIE_DOMAIN=None,
    PERMANENT_SESSION_LIFETIME=86400
)

# Stockage en mémoire
rooms = {
    "general": {"name": "Général", "messages": []},
    "gaming": {"name": "Jeux", "messages": []},
    "help": {"name": "Aide", "messages": []}
}

# Utilisateurs connectés par salon
users_in_rooms = {
    "general": set(),
    "gaming": set(), 
    "help": set()
}

# Tous les utilisateurs connectés
connected_users = set()

@app.route('/')
def index():
    username = request.args.get('user')
    if not username or username not in connected_users:
        return redirect(url_for('login'))
    return render_template('index.html', rooms=rooms, username=username)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username and len(username) <= 20:
            connected_users.add(username)
            return redirect(url_for('index', user=username))
        else:
            flash('Nom d\'utilisateur invalide (max 20 caractères)')
    return render_template('login.html')

@app.route('/logout')
def logout():
    username = request.args.get('user')
    if username and username in connected_users:
        connected_users.discard(username)
        # Retirer l'utilisateur de tous les salons
        for room_users in users_in_rooms.values():
            room_users.discard(username)
    return redirect(url_for('login'))

@app.route('/room/<room_id>')
def room(room_id):
    username = request.args.get('user')
    if not username or username not in connected_users:
        return redirect(url_for('login'))
    
    if room_id not in rooms:
        flash('Salon inexistant')
        return redirect(url_for('index', user=username))
    
    users_in_rooms[room_id].add(username)
    
    # Garder seulement les 20 derniers messages pour les performances
    messages = rooms[room_id]['messages'][-20:]
    room_users = list(users_in_rooms[room_id])
    
    return render_template('room.html', 
                         room=rooms[room_id], 
                         room_id=room_id,
                         messages=messages,
                         users=room_users,
                         username=username)

@app.route('/send_message/<room_id>', methods=['POST'])
def send_message(room_id):
    username = request.form.get('user') or request.args.get('user')
    if not username or username not in connected_users:
        return redirect(url_for('login'))
    
    if room_id not in rooms:
        return redirect(url_for('index', user=username))
    
    message_text = request.form.get('message', '').strip()
    if message_text and len(message_text) <= 200:
        message = {
            'username': username,
            'text': message_text,
            'timestamp': datetime.datetime.now().strftime('%H:%M')
        }
        rooms[room_id]['messages'].append(message)
        
        # Garder seulement les 50 derniers messages en mémoire
        if len(rooms[room_id]['messages']) > 50:
            rooms[room_id]['messages'] = rooms[room_id]['messages'][-50:]
    
    return redirect(url_for('room', room_id=room_id, user=username))

@app.route('/get_messages/<room_id>')
def get_messages(room_id):
    """Endpoint pour récupérer les nouveaux messages (polling)"""
    username = request.args.get('user')
    if not username or username not in connected_users or room_id not in rooms:
        return "[]"
    
    # Récupérer les 20 derniers messages
    messages = rooms[room_id]['messages'][-20:]
    users = list(users_in_rooms[room_id])
    
    # Retourner du HTML simple plutôt que du JSON pour compatibilité 3DS
    html = ""
    for msg in messages:
        html += f'<div class="message"><span class="author">{msg["username"]}</span> <span class="time">{msg["timestamp"]}</span><br>{msg["text"]}</div>'
    
    # Ajouter la liste des utilisateurs
    html += '<div id="users-list">'
    for user in users:
        html += f'<span class="user-badge">{user}</span> '
    html += '</div>'
    
    return html

@app.route('/leave_room/<room_id>')
def leave_room(room_id):
    username = request.args.get('user')
    if username and room_id in users_in_rooms:
        users_in_rooms[room_id].discard(username)
    return redirect(url_for('index', user=username))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
