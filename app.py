import os
import datetime
import random
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

# Stockage en mémoire - salons par défaut
rooms = {
    "general": {"name": "Général", "messages": [], "is_public": True, "owner": None, "code": None},
    "gaming": {"name": "Jeux", "messages": [], "is_public": True, "owner": None, "code": None},
    "help": {"name": "Aide", "messages": [], "is_public": True, "owner": None, "code": None}
}

# Utilisateurs connectés par salon
users_in_rooms = {
    "general": set(),
    "gaming": set(), 
    "help": set()
}

# Tous les utilisateurs connectés
connected_users = set()

# Compteur pour générer des IDs uniques de salons
room_counter = 0

def generate_room_code():
    """Génère un code à 6 chiffres unique"""
    return str(random.randint(100000, 999999))

@app.route('/')
def index():
    username = request.args.get('user')
    if not username or username not in connected_users:
        return redirect(url_for('login'))
    
    # Calculer le nombre d'utilisateurs par salon pour les salons publics
    rooms_with_counts = {}
    for room_id, room_data in rooms.items():
        if room_data['is_public']:  # Seulement les salons publics
            rooms_with_counts[room_id] = {
                **room_data,
                'user_count': len(users_in_rooms.get(room_id, set()))
            }
    
    return render_template('index.html', rooms=rooms_with_counts, username=username)

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
        # Retirer l'utilisateur de tous les salons et supprimer ses salons
        _remove_user_from_all_rooms(username)
    return redirect(url_for('login'))

def _remove_user_from_all_rooms(username):
    """Retire l'utilisateur de tous les salons et supprime ses salons privés"""
    rooms_to_delete = []
    
    for room_id, room_data in rooms.items():
        # Retirer l'utilisateur du salon
        if room_id in users_in_rooms:
            users_in_rooms[room_id].discard(username)
        
        # Si l'utilisateur est propriétaire d'un salon privé, marquer pour suppression
        if room_data['owner'] == username and not room_data['is_public']:
            rooms_to_delete.append(room_id)
    
    # Supprimer les salons privés de l'utilisateur
    for room_id in rooms_to_delete:
        if room_id in rooms:
            del rooms[room_id]
        if room_id in users_in_rooms:
            del users_in_rooms[room_id]

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
    
    # Debug temporaire
    print(f"DEBUG: Room data for {room_id}: {rooms[room_id]}")
    
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
        
        # Si l'utilisateur est le propriétaire d'un salon privé, le supprimer
        if (room_id in rooms and 
            rooms[room_id]['owner'] == username and 
            not rooms[room_id]['is_public']):
            del rooms[room_id]
            del users_in_rooms[room_id]
            
    return redirect(url_for('index', user=username))

@app.route('/create_room', methods=['GET', 'POST'])
def create_room():
    username = request.args.get('user')
    if not username or username not in connected_users:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        room_name = request.form.get('room_name', '').strip()
        is_public = request.form.get('visibility') == 'public'
        
        if room_name and len(room_name) <= 30:
            global room_counter
            room_counter += 1
            room_id = f"room_{room_counter}"
            
            # Générer un code pour les salons privés
            room_code = None if is_public else generate_room_code()
            
            rooms[room_id] = {
                'name': room_name,
                'messages': [],
                'is_public': is_public,
                'owner': username,
                'code': room_code
            }
            
            users_in_rooms[room_id] = set()
            
            if is_public:
                return redirect(url_for('room', room_id=room_id, user=username))
            else:
                flash(f'Salon privé créé ! Code d\'accès : {room_code}')
                return redirect(url_for('room', room_id=room_id, user=username))
        else:
            flash('Nom de salon invalide (max 30 caractères)')
    
    return render_template('create_room.html', username=username)

@app.route('/join_private', methods=['GET', 'POST'])
def join_private():
    username = request.args.get('user')
    if not username or username not in connected_users:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        room_code = request.form.get('room_code', '').strip()
        
        # Chercher le salon avec ce code
        for room_id, room_data in rooms.items():
            if (not room_data['is_public'] and 
                room_data['code'] == room_code):
                return redirect(url_for('room', room_id=room_id, user=username))
        
        flash('Code de salon invalide')
    
    return render_template('join_private.html', username=username)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
