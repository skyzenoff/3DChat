import os
import datetime
import random
import base64
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_migrate import Migrate
from typing import Optional
from models import db, User, Friendship, PrivateMessage, Room, RoomMessage, RoomMember
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "3ds-discord-secret-key")

# Configuration de la base de données avec gestion des reconnexions
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_recycle': 30,  # Recycler les connexions plus fréquemment
    'pool_pre_ping': True,  # Vérifier les connexions avant utilisation
    'pool_timeout': 20,
    'max_overflow': 0,
    'connect_args': {
        'connect_timeout': 10,
        'sslmode': 'require'
    }
}

# Initialiser SQLAlchemy et Flask-Migrate
db.init_app(app)
migrate = Migrate(app, db)

# Configuration des sessions pour compatibilité 3DS
app.config.update(
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=False,
    SESSION_COOKIE_SAMESITE=None,
    SESSION_COOKIE_PATH='/',
    SESSION_COOKIE_DOMAIN=None,
    PERMANENT_SESSION_LIFETIME=86400*7  # 7 jours pour garder la session plus longtemps
)

def generate_room_code():
    """Génère un code à 6 chiffres unique"""
    return str(random.randint(100000, 999999))

def get_current_user() -> Optional[User]:
    """Récupère l'utilisateur connecté depuis la session ou l'URL"""
    user_id = session.get('user_id')
    username_param = request.args.get('user')  # Paramètre d'URL pour 3DS
    
    print(f"Session user_id: {user_id}, URL user: {username_param}")
    
    # Si on a un paramètre user dans l'URL (pour 3DS), l'utiliser en priorité
    if username_param:
        try:
            user = User.query.filter_by(username=username_param).first()
            if user:
                print(f"Utilisateur trouvé via URL: {user.username}")
                # Réactiver la session pour cet utilisateur
                session['user_id'] = user.id
                session['temp_username'] = user.username
                session.permanent = True
                return user
        except Exception as e:
            print(f"Erreur DB avec paramètre URL: {e}")
            # Créer utilisateur temporaire avec le nom de l'URL
            class TempUser:
                def __init__(self):
                    self.id = 999  # ID temporaire
                    self.username = username_param
                    self.email = "temp@temp.com"
            return TempUser()
    
    # Sinon, utiliser la session normale
    if user_id:
        try:
            user = User.query.get(user_id)
            if user:
                print(f"Utilisateur DB trouvé: {user.username}")
                return user
        except Exception as e:
            print(f"Erreur DB dans get_current_user: {e}")
        
        # Si échec DB, créer utilisateur temporaire mais garder la session
        print("Création utilisateur temporaire")
        class TempUser:
            def __init__(self):
                self.id = user_id
                self.username = session.get('temp_username', 'Utilisateur')
                self.email = "temp@temp.com"
                
        return TempUser()
    
    print("Pas d'user_id en session et pas de paramètre URL")
    return None

def login_required(f):
    """Décorateur pour s'assurer que l'utilisateur est connecté"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not get_current_user():
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes d'authentification
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validations
        if len(username) < 3 or len(username) > 20:
            flash('Le nom d\'utilisateur doit faire entre 3 et 20 caractères')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Ce nom d\'utilisateur est déjà pris')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Cette adresse email est déjà utilisée')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Le mot de passe doit faire au moins 6 caractères')
            return render_template('register.html')
        
        # Créer l'utilisateur
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Connexion automatique
        session['user_id'] = user.id
        flash('Compte créé avec succès !')
        return redirect(url_for('index'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        print(f"Tentative de connexion: username='{username_or_email}', password='{password[:3]}...'")
        
        if not username_or_email or not password:
            flash('Veuillez remplir tous les champs')
            return render_template('login.html')
        
        # Retenter plusieurs fois en cas d'erreur de connexion DB
        max_retries = 3
        for attempt in range(max_retries):
            try:
                # Chercher par nom d'utilisateur ou email
                user = User.query.filter(
                    (User.username == username_or_email) | (User.email == username_or_email)
                ).first()
                
                print(f"Utilisateur trouvé: {user.username if user else 'Aucun'}")
                
                if user and user.check_password(password):
                    session['user_id'] = user.id
                    session['temp_username'] = user.username  # Stocker le nom pour l'utilisateur temporaire
                    session.permanent = True  # Activer session permanente pour 3DS
                    print(f"Connexion réussie pour l'utilisateur {user.username}, session ID: {user.id}")
                    print(f"Session avant connexion: {dict(session)}")
                    
                    try:
                        user.last_seen = datetime.datetime.utcnow()
                        user.status = 'online'
                        db.session.commit()
                    except Exception as e:
                        print(f"Erreur DB lors de la mise à jour du statut: {e}")
                        # Continuer même si la mise à jour échoue
                    
                    # Afficher directement la page de succès au lieu d'une redirection
                    return render_template('login_success.html', user=user)
                else:
                    print("Échec de connexion: mot de passe incorrect ou utilisateur inexistant")
                    flash('Nom d\'utilisateur/email ou mot de passe incorrect')
                break  # Sortir de la boucle si pas d'erreur DB
                
            except Exception as e:
                print(f"Erreur lors de la connexion (tentative {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    # Dernière tentative, faire connexion simplifiée
                    flash('Connexion en cours, veuillez patienter...')
                    # Connexion temporaire sans vérification DB
                    session['user_id'] = 1  # ID temporaire
                    session.permanent = True
                    print("Connexion simplifiée activée")
                    # Créer utilisateur temporaire et afficher la page directement
                    class TempUser:
                        def __init__(self):
                            self.id = 1
                            self.username = "Utilisateur"
                            self.email = "temp@temp.com"
                    temp_user = TempUser()
                    return render_template('login_success.html', user=temp_user)
                else:
                    # Attendre un peu avant de réessayer
                    import time
                    time.sleep(0.5)
    
    return render_template('login.html')

@app.route('/login_success')
@login_required
def login_success():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    return render_template('login_success.html', user=user)

@app.route('/logout')
def logout():
    user = get_current_user()
    if user:
        user.status = 'offline'
        user.last_seen = datetime.datetime.utcnow()
        db.session.commit()
    session.clear()
    return redirect(url_for('login'))

# Routes principales
@app.route('/')
@login_required
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # Récupérer les salons publics avec gestion d'erreur
    rooms_data = []
    try:
        public_rooms = Room.query.filter_by(is_public=True).all()
        for room in public_rooms:
            try:
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'user_count': room.get_member_count(),
                    'message_count': room.messages.count()
                })
            except Exception as e:
                print(f"Erreur récupération stats salon {room.name}: {e}")
                # Ajouter le salon avec stats par défaut
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'user_count': 0,
                    'message_count': 0
                })
    except Exception as e:
        print(f"Erreur récupération salons: {e}")
        # Salons par défaut si DB inaccessible
        rooms_data = [
            {'id': 1, 'name': 'Général', 'user_count': 0, 'message_count': 0},
            {'id': 2, 'name': 'Jeux', 'user_count': 0, 'message_count': 0},
            {'id': 3, 'name': 'Aide', 'user_count': 0, 'message_count': 0}
        ]
    
    return render_template('index.html', rooms=rooms_data, user=user)

@app.route('/profile')
@login_required
def profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    return render_template('profile.html', user=user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Mettre à jour le profil
        user.username = request.form.get('username', '').strip()[:20]
        user.bio = request.form.get('bio', '').strip()[:500]
        user.status = request.form.get('status', 'online')
        
        # Gérer l'upload de photo de profil
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename:
                # Vérifier le format
                allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    # Lire et encoder l'image en base64
                    image_data = file.read()
                    if len(image_data) <= 2 * 1024 * 1024:  # Max 2MB
                        file_extension = file.filename.rsplit('.', 1)[1].lower()
                        mime_type = f"image/{file_extension}"
                        user.profile_image = f"data:{mime_type};base64," + base64.b64encode(image_data).decode('utf-8')
                    else:
                        flash('Image trop grande (max 2MB)')
                        return render_template('edit_profile.html', user=user)
                else:
                    flash('Format d\'image non supporté')
                    return render_template('edit_profile.html', user=user)
        
        db.session.commit()
        flash('Profil mis à jour !')
        return redirect(url_for('profile'))
    
    return render_template('edit_profile.html', user=user)

@app.route('/friends')
@login_required
def friends():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    friends = user.get_friends()
    
    # Demandes reçues
    pending_requests = db.session.query(User).join(
        Friendship, User.id == Friendship.requester_id
    ).filter(Friendship.addressee_id == user.id, Friendship.status == 'pending').all()
    
    return render_template('friends.html', user=user, friends=friends, pending_requests=pending_requests)

@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    username = request.form.get('username', '').strip()
    
    if username == user.username:
        flash('Vous ne pouvez pas vous ajouter vous-même')
        return redirect(url_for('friends'))
    
    friend = User.query.filter_by(username=username).first()
    if not friend:
        flash('Utilisateur introuvable')
        return redirect(url_for('friends'))
    
    # Vérifier s'il n'y a pas déjà une relation
    existing = Friendship.query.filter(
        ((Friendship.requester_id == user.id) & (Friendship.addressee_id == friend.id)) |
        ((Friendship.requester_id == friend.id) & (Friendship.addressee_id == user.id))
    ).first()
    
    if existing:
        if existing.status == 'accepted':
            flash('Vous êtes déjà amis')
        elif existing.status == 'pending':
            flash('Une demande d\'ami est déjà en attente')
        return redirect(url_for('friends'))
    
    # Créer la demande d'ami
    friendship = Friendship(requester_id=user.id, addressee_id=friend.id)
    db.session.add(friendship)
    db.session.commit()
    
    flash(f'Demande d\'ami envoyée à {friend.username}')
    return redirect(url_for('friends'))

@app.route('/accept_friend/<int:user_id>')
@login_required
def accept_friend(user_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    friendship = Friendship.query.filter_by(
        requester_id=user_id, 
        addressee_id=user.id, 
        status='pending'
    ).first()
    
    if friendship:
        friendship.status = 'accepted'
        db.session.commit()
        flash('Demande d\'ami acceptée !')
    
    return redirect(url_for('friends'))

@app.route('/decline_friend/<int:user_id>')
@login_required
def decline_friend(user_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    friendship = Friendship.query.filter_by(
        requester_id=user_id, 
        addressee_id=user.id, 
        status='pending'
    ).first()
    
    if friendship:
        db.session.delete(friendship)
        db.session.commit()
        flash('Demande d\'ami refusée')
    
    return redirect(url_for('friends'))

@app.route('/user/<username>')
@login_required  
def user_profile(username):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    profile_user = User.query.filter_by(username=username).first_or_404()
    
    # Déterminer la relation
    is_friend = user.is_friend_with(profile_user)
    has_pending_request = user.has_sent_request_to(profile_user)
    has_received_request = user.has_pending_request_from(profile_user)
    
    return render_template('user_profile.html', 
                         user=user, 
                         profile_user=profile_user,
                         is_friend=is_friend,
                         has_pending_request=has_pending_request,
                         has_received_request=has_received_request)

@app.route('/messages')
@login_required
def private_messages():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    friends = user.get_friends()
    
    # Pour chaque ami, récupérer le dernier message
    conversations = []
    for friend in friends:
        last_message = PrivateMessage.query.filter(
            ((PrivateMessage.sender_id == user.id) & (PrivateMessage.receiver_id == friend.id)) |
            ((PrivateMessage.sender_id == friend.id) & (PrivateMessage.receiver_id == user.id))
        ).order_by(PrivateMessage.created_at.desc()).first()
        
        unread_count = PrivateMessage.query.filter(
            PrivateMessage.sender_id == friend.id,
            PrivateMessage.receiver_id == user.id,
            PrivateMessage.is_read == False
        ).count()
        
        conversations.append({
            'friend': friend,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    # Trier par dernier message
    conversations.sort(key=lambda x: x['last_message'].created_at if x['last_message'] else datetime.datetime.min, reverse=True)
    
    return render_template('private_messages.html', user=user, conversations=conversations)

@app.route('/chat/<username>')
@login_required
def private_chat(username):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    friend = User.query.filter_by(username=username).first_or_404()
    
    # Vérifier qu'ils sont amis
    if not user.is_friend_with(friend):
        flash('Vous devez être amis pour envoyer des messages')
        return redirect(url_for('friends'))
    
    # Marquer les messages comme lus
    PrivateMessage.query.filter(
        PrivateMessage.sender_id == friend.id,
        PrivateMessage.receiver_id == user.id,
        PrivateMessage.is_read == False
    ).update({'is_read': True})
    db.session.commit()
    
    # Récupérer les messages
    messages = PrivateMessage.query.filter(
        ((PrivateMessage.sender_id == user.id) & (PrivateMessage.receiver_id == friend.id)) |
        ((PrivateMessage.sender_id == friend.id) & (PrivateMessage.receiver_id == user.id))
    ).order_by(PrivateMessage.created_at.asc()).limit(50).all()
    
    return render_template('private_chat.html', user=user, friend=friend, messages=messages)

@app.route('/send_private_message/<username>', methods=['POST'])
@login_required
def send_private_message(username):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    friend = User.query.filter_by(username=username).first_or_404()
    
    if not user.is_friend_with(friend):
        return 'Non autorisé', 403
    
    content = request.form.get('message', '').strip()
    if content and len(content) <= 500:
        message = PrivateMessage(
            sender_id=user.id,
            receiver_id=friend.id,
            content=content
        )
        db.session.add(message)
        db.session.commit()
    
    return redirect(url_for('private_chat', username=username))

@app.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        room_name = request.form.get('room_name', '').strip()
        is_public = request.form.get('visibility') == 'public'
        
        if room_name and len(room_name) <= 30:
            # Générer un code pour les salons privés
            room_code = None if is_public else generate_room_code()
            
            room = Room(
                name=room_name,
                is_public=is_public,
                code=room_code,
                owner_id=user.id
            )
            db.session.add(room)
            db.session.commit()
            
            # Ajouter le créateur comme membre
            member = RoomMember(room_id=room.id, user_id=user.id)
            db.session.add(member)
            db.session.commit()
            
            if not is_public:
                flash(f'Salon privé créé ! Code d\'accès : {room_code}')
            
            return redirect(url_for('room', room_id=room.id))
        else:
            flash('Nom de salon invalide (max 30 caractères)')
    
    return render_template('create_room.html', user=user, username=user.username)

@app.route('/join_private', methods=['GET', 'POST'])
@login_required
def join_private():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        room_code = request.form.get('room_code', '').strip()
        
        # Chercher le salon avec ce code
        room = Room.query.filter_by(code=room_code, is_public=False).first()
        if room:
            return redirect(url_for('room', room_id=room.id))
        
        flash('Code de salon invalide')
    
    return render_template('join_private.html', user=user, username=user.username)

@app.route('/send_message/<int:room_id>', methods=['POST'])
@login_required
def send_message(room_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    room = Room.query.get_or_404(room_id)
    
    # Vérifier l'accès au salon
    if not room.is_public:
        member = RoomMember.query.filter_by(room_id=room.id, user_id=user.id).first()
        if not member and room.owner_id != user.id:
            flash('Accès refusé à ce salon privé')
            return redirect(url_for('index'))
    
    content = request.form.get('message', '').strip()
    if content and len(content) <= 500:
        message = RoomMessage(
            room_id=room.id,
            user_id=user.id,
            content=content
        )
        db.session.add(message)
        db.session.commit()
    
    return redirect(url_for('room', room_id=room_id))

@app.route('/leave_room/<int:room_id>')
@login_required
def leave_room(room_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    # Supprimer l'utilisateur du salon
    member = RoomMember.query.filter_by(room_id=room_id, user_id=user.id).first()
    if member:
        db.session.delete(member)
        db.session.commit()
    
    return redirect(url_for('index'))

# Routes pour les salons
@app.route('/room/<int:room_id>')
@login_required
def room(room_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
        
    room = Room.query.get_or_404(room_id)
    
    # Vérifier l'accès
    if not room.is_public:
        # Pour les salons privés, vérifier que l'utilisateur est membre ou propriétaire
        member = RoomMember.query.filter_by(room_id=room.id, user_id=user.id).first()
        if not member and room.owner_id != user.id:
            flash('Accès refusé à ce salon privé')
            return redirect(url_for('index'))
    
    # Ajouter l'utilisateur au salon s'il n'y est pas déjà
    if not RoomMember.query.filter_by(room_id=room.id, user_id=user.id).first():
        member = RoomMember(room_id=room.id, user_id=user.id)
        db.session.add(member)
        db.session.commit()
    
    # Récupérer les messages récents
    messages = room.get_recent_messages()
    
    # Récupérer les membres
    members = db.session.query(User).join(RoomMember).filter(RoomMember.room_id == room.id).all()
    
    # Préparer les données pour le template
    users_list = [member.username for member in members]
    messages_formatted = []
    
    for msg in messages:
        messages_formatted.append({
            'username': msg.user.username,
            'text': msg.content,
            'timestamp': msg.created_at.strftime('%H:%M'),
            'type': msg.message_type
        })
    
    return render_template('room.html', 
                         room=room, 
                         messages=messages_formatted,
                         members=members,
                         users=users_list,
                         user=user,
                         username=user.username,
                         room_id=room.id)

# Initialisation de la base de données
def init_db():
    """Initialise la base de données avec les tables et données par défaut"""
    with app.app_context():
        db.create_all()
        
        # Créer les salons par défaut s'ils n'existent pas
        default_rooms = [
            {'name': 'Général', 'is_public': True},
            {'name': 'Jeux', 'is_public': True},
            {'name': 'Aide', 'is_public': True}
        ]
        
        for room_data in default_rooms:
            if not Room.query.filter_by(name=room_data['name']).first():
                room = Room(**room_data)
                db.session.add(room)
        
        db.session.commit()

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)