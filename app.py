import os
import datetime
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Configuration du logging pour le debug
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "3ds-discord-secret-key")

# Configuration des sessions pour compatibilité 3DS
app.config.update(
    SESSION_COOKIE_SECURE=False,  # Permet les cookies non-HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',  # Plus permissif que 'Strict'
    PERMANENT_SESSION_LIFETIME=86400  # 24 heures
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
    app.logger.debug(f"Index route accessed, session: {dict(session)}")
    if 'username' not in session:
        app.logger.debug("No username in session, redirecting to login")
        return redirect(url_for('login'))
    app.logger.debug(f"User {session['username']} accessing index")
    return render_template('index.html', rooms=rooms, username=session['username'])

@app.route('/login', methods=['GET', 'POST'])
def login():
    app.logger.debug(f"Login route accessed, method: {request.method}")
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        app.logger.debug(f"Username received: '{username}', length: {len(username) if username else 0}")
        if username and len(username) <= 20:
            session.permanent = True  # Rendre la session permanente
            session['username'] = username
            connected_users.add(username)
            app.logger.debug(f"Session set for user: {username}")
            app.logger.debug(f"Redirecting to index...")
            return redirect(url_for('index'))
        else:
            app.logger.debug(f"Invalid username: '{username}'")
            flash('Nom d\'utilisateur invalide (max 20 caractères)')
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        username = session['username']
        connected_users.discard(username)
        # Retirer l'utilisateur de tous les salons
        for room_users in users_in_rooms.values():
            room_users.discard(username)
        session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/room/<room_id>')
def room(room_id):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if room_id not in rooms:
        flash('Salon inexistant')
        return redirect(url_for('index'))
    
    username = session['username']
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
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if room_id not in rooms:
        return redirect(url_for('index'))
    
    message_text = request.form.get('message', '').strip()
    if message_text and len(message_text) <= 200:
        message = {
            'username': session['username'],
            'text': message_text,
            'timestamp': datetime.datetime.now().strftime('%H:%M')
        }
        rooms[room_id]['messages'].append(message)
        
        # Garder seulement les 50 derniers messages en mémoire
        if len(rooms[room_id]['messages']) > 50:
            rooms[room_id]['messages'] = rooms[room_id]['messages'][-50:]
    
    return redirect(url_for('room', room_id=room_id))

@app.route('/get_messages/<room_id>')
def get_messages(room_id):
    """Endpoint pour récupérer les nouveaux messages (polling)"""
    if 'username' not in session or room_id not in rooms:
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
    if 'username' in session and room_id in users_in_rooms:
        users_in_rooms[room_id].discard(session['username'])
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
