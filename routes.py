import datetime
import random
import base64
from flask import render_template, request, redirect, url_for, session, flash, jsonify
from typing import Optional
from app import app, db
from models import User, Friendship, PrivateMessage, Room, RoomMessage, RoomMember
from werkzeug.utils import secure_filename

def generate_room_code():
    """Génère un code à 6 chiffres unique"""
    return str(random.randint(100000, 999999))

class TempUser:
    def __init__(self, user_id=999, username="Utilisateur"):
        self.id = user_id
        self.username = username
        self.email = "temp@temp.com"
        self.status = "online"
        self.bio = ""
        self.profile_image = ""
        self.last_seen = datetime.datetime.utcnow()
    
    def get_friends(self):
        return []
    
    def is_friend_with(self, user):
        return False

def get_current_user():
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
            return TempUser(999, username_param)
    
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
        return TempUser(user_id, session.get('temp_username', 'Utilisateur'))
    
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
        user = User()
        user.username = username
        user.email = email
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
                    temp_user = TempUser(1, "Utilisateur")
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
    if user and hasattr(user, 'status'):
        try:
            user.status = 'offline'
            user.last_seen = datetime.datetime.utcnow()
            db.session.commit()
        except:
            pass
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
                    'message_count': room.get_message_count()
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
        # Créer quelques salons par défaut si aucun n'existe
        try:
            # Créer des salons de base s'ils n'existent pas
            default_rooms = [
                {'name': 'Général', 'desc': 'Discussion générale'},
                {'name': 'Jeux', 'desc': 'Parlez de vos jeux favoris'},
                {'name': 'Aide', 'desc': 'Entraide et support'},
                {'name': '3DS Homebrew', 'desc': 'Développement homebrew 3DS'}
            ]
            
            for room_data in default_rooms:
                if not Room.query.filter_by(name=room_data['name']).first():
                    room = Room()
                    room.name = room_data['name']
                    room.description = room_data['desc']
                    room.owner_id = user.id if hasattr(user, 'id') else 1
                    room.is_public = True
                    db.session.add(room)
            
            db.session.commit()
            
            # Récupérer à nouveau les salons
            public_rooms = Room.query.filter_by(is_public=True).all()
            for room in public_rooms:
                rooms_data.append({
                    'id': room.id,
                    'name': room.name,
                    'user_count': room.get_member_count(),
                    'message_count': room.get_message_count()
                })
        except Exception as e2:
            print(f"Erreur création salons par défaut: {e2}")
            # Forcer la création des salons par défaut
            rooms_data = [
                {'id': 1, 'name': 'Général', 'user_count': 0, 'message_count': 0},
                {'id': 2, 'name': 'Jeux', 'user_count': 0, 'message_count': 0},
                {'id': 3, 'name': 'Aide', 'user_count': 0, 'message_count': 0},
                {'id': 4, 'name': '3DS Homebrew', 'user_count': 0, 'message_count': 0}
            ]
    
    return render_template('index.html', rooms=rooms_data, user=user)

@app.route('/room/<int:room_id>')
@login_required
def room(room_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    try:
        room = Room.query.get(room_id)
        if not room:
            flash('Salon inexistant')
            return redirect(url_for('index'))
        
        # Ajouter l'utilisateur au salon s'il n'y est pas déjà
        if hasattr(user, 'id') and not room.is_member(user):
            room.add_member(user)
            db.session.commit()
        
        # Récupérer les messages récents
        messages = RoomMessage.query.filter_by(room_id=room_id).order_by(RoomMessage.created_at.desc()).limit(20).all()[::-1]
        
        # Récupérer les membres du salon
        members = room.members.all() if room else []
        
        return render_template('room.html', 
                             room=room, 
                             room_id=room_id,
                             messages=messages,
                             members=members,
                             user=user)
    except Exception as e:
        print(f"Erreur accès salon: {e}")
        flash('Erreur d\'accès au salon')
        return redirect(url_for('index'))

@app.route('/send_message/<int:room_id>', methods=['POST'])
@login_required
def send_message(room_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    try:
        room = Room.query.get(room_id)
        if not room:
            return redirect(url_for('index'))
        
        message_text = request.form.get('message', '').strip()
        if message_text and len(message_text) <= 500 and hasattr(user, 'id'):
            message = RoomMessage()
            message.room_id = room_id
            message.user_id = user.id
            message.content = message_text
            db.session.add(message)
            db.session.commit()
        
        return redirect(url_for('room', room_id=room_id))
    except Exception as e:
        print(f"Erreur envoi message: {e}")
        return redirect(url_for('room', room_id=room_id))

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
    
    if request.method == 'POST' and hasattr(user, 'id'):
        try:
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
                            if hasattr(user, 'profile_image'):
                                user.profile_image = f"data:{mime_type};base64," + base64.b64encode(image_data).decode('utf-8')
                        else:
                            flash('Image trop grande (max 2MB)')
                            return render_template('edit_profile.html', user=user)
                    else:
                        flash('Format d\'image non supporté')
                        return render_template('edit_profile.html', user=user)
            
            db.session.commit()
            flash('Profil mis à jour !')
            
            # Préserver le paramètre utilisateur pour 3DS
            user_param = request.args.get('user')
            if user_param:
                return redirect(url_for('profile', user=user_param))
            return redirect(url_for('profile'))
        except Exception as e:
            print(f"Erreur mise à jour profil: {e}")
            flash('Erreur lors de la mise à jour')
    
    return render_template('edit_profile.html', user=user)

@app.route('/friends')
@login_required
def friends():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    try:
        friends = user.get_friends() if hasattr(user, 'get_friends') else []
        
        # Demandes reçues avec l'ID de l'amitié
        pending_requests = []
        if hasattr(user, 'id'):
            friendships = db.session.query(Friendship, User).join(
                User, User.id == Friendship.requester_id
            ).filter(Friendship.addressee_id == user.id, Friendship.status == 'pending').all()
            
            for friendship, requester in friendships:
                requester.friendship_id = friendship.id  # Ajouter l'ID de l'amitié
                pending_requests.append(requester)
        
        return render_template('friends.html', user=user, friends=friends, pending_requests=pending_requests)
    except Exception as e:
        print(f"Erreur page amis: {e}")
        return render_template('friends.html', user=user, friends=[], pending_requests=[])

@app.route('/create_room', methods=['GET', 'POST'])
@login_required
def create_room():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        room_name = request.form.get('room_name', '').strip()
        is_public = request.form.get('visibility') == 'public'
        
        if room_name and len(room_name) <= 30 and hasattr(user, 'id'):
            try:
                # Générer un code pour les salons privés
                room_code = None if is_public else generate_room_code()
                
                room = Room()
                room.name = room_name
                room.owner_id = user.id
                room.is_public = is_public
                room.join_code = room_code
                
                db.session.add(room)
                db.session.commit()
                
                # Ajouter le créateur au salon
                room.add_member(user)
                db.session.commit()
                
                if not is_public and room_code:
                    flash(f'Salon privé créé ! Code d\'accès : {room_code}')
                
                return redirect(url_for('room', room_id=room.id))
            except Exception as e:
                print(f"Erreur création salon: {e}")
                flash('Erreur lors de la création du salon')
        else:
            flash('Nom de salon invalide (max 30 caractères)')
    
    return render_template('create_room.html', user=user)

@app.route('/join_private', methods=['GET', 'POST'])
@login_required
def join_private():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        room_code = request.form.get('room_code', '').strip()
        
        try:
            # Chercher le salon avec ce code
            room = Room.query.filter_by(join_code=room_code, is_public=False).first()
            if room:
                return redirect(url_for('room', room_id=room.id))
            else:
                flash('Code de salon invalide')
        except Exception as e:
            print(f"Erreur recherche salon: {e}")
            flash('Erreur lors de la recherche du salon')
    
    return render_template('join_private.html', user=user)

@app.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return redirect(url_for('login'))
        
    username = request.form.get('username', '').strip()
    user_param = request.args.get('user')
    
    try:
        if username == user.username:
            flash('Vous ne pouvez pas vous ajouter vous-même')
        else:
            friend = User.query.filter_by(username=username).first()
            if not friend:
                flash('Utilisateur introuvable')
            else:
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
                else:
                    # Créer la demande d'ami
                    friendship = Friendship()
                    friendship.requester_id = user.id
                    friendship.addressee_id = friend.id
                    friendship.status = 'pending'
                    db.session.add(friendship)
                    db.session.commit()
                    flash(f'Demande d\'ami envoyée à {username}')
    except Exception as e:
        print(f"Erreur ajout ami: {e}")
        flash('Erreur lors de l\'ajout d\'ami')
    
    if user_param:
        return redirect(url_for('friends', user=user_param))
    return redirect(url_for('friends'))

@app.route('/accept_friend/<int:friendship_id>')
@login_required
def accept_friend(friendship_id):
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return redirect(url_for('login'))
    
    user_param = request.args.get('user')
    
    try:
        friendship = Friendship.query.get(friendship_id)
        if friendship and friendship.addressee_id == user.id:
            friendship.status = 'accepted'
            db.session.commit()
            flash('Demande d\'ami acceptée')
    except Exception as e:
        print(f"Erreur acceptation ami: {e}")
        flash('Erreur lors de l\'acceptation')
    
    if user_param:
        return redirect(url_for('friends', user=user_param))
    return redirect(url_for('friends'))

@app.route('/decline_friend/<int:friendship_id>')
@login_required
def decline_friend(friendship_id):
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return redirect(url_for('login'))
    
    user_param = request.args.get('user')
    
    try:
        friendship = Friendship.query.get(friendship_id)
        if friendship and friendship.addressee_id == user.id:
            db.session.delete(friendship)
            db.session.commit()
            flash('Demande d\'ami refusée')
    except Exception as e:
        print(f"Erreur refus ami: {e}")
        flash('Erreur lors du refus')
    
    if user_param:
        return redirect(url_for('friends', user=user_param))
    return redirect(url_for('friends'))

@app.route('/private_messages')
@login_required
def private_messages():
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    try:
        # Récupérer les amis et créer des objets conversation
        friends = user.get_friends() if hasattr(user, 'get_friends') else []
        conversations = []
        
        for friend in friends:
            # Récupérer le dernier message avec cet ami
            last_message = PrivateMessage.query.filter(
                ((PrivateMessage.sender_id == user.id) & (PrivateMessage.receiver_id == friend.id)) |
                ((PrivateMessage.sender_id == friend.id) & (PrivateMessage.receiver_id == user.id))
            ).order_by(PrivateMessage.created_at.desc()).first()
            
            # Compter les messages non lus de cet ami
            unread_count = PrivateMessage.query.filter(
                PrivateMessage.sender_id == friend.id,
                PrivateMessage.receiver_id == user.id,
                PrivateMessage.is_read == False
            ).count()
            
            # Créer un objet conversation simple
            class Conversation:
                def __init__(self):
                    self.friend = None
                    self.last_message = None
                    self.unread_count = 0
            
            conversation = Conversation()
            conversation.friend = friend
            conversation.last_message = last_message
            conversation.unread_count = unread_count
            
            conversations.append(conversation)
        
        # Trier par dernière activité (conversations avec messages récents en premier)
        conversations.sort(key=lambda c: c.last_message.created_at if c.last_message else datetime.datetime.min, reverse=True)
        
        return render_template('private_messages.html', user=user, conversations=conversations)
    except Exception as e:
        print(f"Erreur private_messages: {e}")
        return render_template('private_messages.html', user=user, conversations=[])

@app.route('/get_conversations_update')
@login_required
def get_conversations_update():
    """Endpoint pour mettre à jour les conversations en temps réel"""
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return jsonify([])
    
    try:
        friends = user.get_friends() if hasattr(user, 'get_friends') else []
        conversations_data = []
        
        for friend in friends:
            # Récupérer le dernier message
            last_message = PrivateMessage.query.filter(
                ((PrivateMessage.sender_id == user.id) & (PrivateMessage.receiver_id == friend.id)) |
                ((PrivateMessage.sender_id == friend.id) & (PrivateMessage.receiver_id == user.id))
            ).order_by(PrivateMessage.created_at.desc()).first()
            
            # Compter les messages non lus
            unread_count = PrivateMessage.query.filter(
                PrivateMessage.sender_id == friend.id,
                PrivateMessage.receiver_id == user.id,
                PrivateMessage.is_read == False
            ).count()
            
            # Créer l'objet conversation pour JSON
            conv_data = {
                'friend': {
                    'id': friend.id,
                    'username': friend.username,
                    'profile_image': getattr(friend, 'profile_image', '')
                },
                'unread_count': unread_count,
                'last_message': None
            }
            
            if last_message:
                conv_data['last_message'] = {
                    'content': last_message.content,
                    'time': last_message.created_at.strftime('%H:%M'),
                    'is_from_user': last_message.sender_id == user.id
                }
            
            conversations_data.append(conv_data)
        
        # Trier par dernière activité
        conversations_data.sort(key=lambda c: c['last_message']['time'] if c['last_message'] else '00:00', reverse=True)
        
        return jsonify(conversations_data)
    except Exception as e:
        print(f"Erreur get_conversations_update: {e}")
        return jsonify([])

@app.route('/initiate_call/<int:friend_id>')
@login_required
def initiate_call(friend_id):
    """Initier un appel vers un ami"""
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return jsonify({'success': False, 'error': 'Utilisateur non authentifié'})
    
    try:
        # Vérifier que l'utilisateur ciblé est bien un ami
        friend = User.query.get(friend_id)
        if not friend:
            return jsonify({'success': False, 'error': 'Utilisateur introuvable'})
        
        # Vérifier l'amitié
        from sqlalchemy import and_, or_
        friendship = Friendship.query.filter(
            or_(
                and_(Friendship.requester_id == user.id, Friendship.addressee_id == friend_id),
                and_(Friendship.requester_id == friend_id, Friendship.addressee_id == user.id)
            ),
            Friendship.status == 'accepted'
        ).first()
        
        if not friendship:
            return jsonify({'success': False, 'error': 'Vous devez être amis pour appeler'})
        
        # Dans une vraie application, ici on enverrait une notification push
        # ou on utiliserait WebSockets pour notifier l'autre utilisateur
        
        return jsonify({
            'success': True, 
            'message': f'Appel initié vers {friend.username}',
            'friend_name': friend.username,
            'friend_avatar': getattr(friend, 'profile_image', '')
        })
        
    except Exception as e:
        print(f"Erreur initiate_call: {e}")
        return jsonify({'success': False, 'error': 'Erreur serveur'})

@app.route('/respond_to_call', methods=['POST'])
@login_required
def respond_to_call():
    """Répondre à un appel (accepter ou refuser)"""
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return jsonify({'success': False, 'error': 'Utilisateur non authentifié'})
    
    try:
        data = request.get_json()
        action = data.get('action')  # 'accept' ou 'decline'
        caller_id = data.get('caller_id')
        
        if action not in ['accept', 'decline']:
            return jsonify({'success': False, 'error': 'Action invalide'})
        
        caller = User.query.get(caller_id)
        if not caller:
            return jsonify({'success': False, 'error': 'Appelant introuvable'})
        
        # Dans une vraie application, ici on notifierait l'appelant de la réponse
        
        return jsonify({
            'success': True,
            'action': action,
            'message': f'Appel {"accepté" if action == "accept" else "refusé"}'
        })
        
    except Exception as e:
        print(f"Erreur respond_to_call: {e}")
        return jsonify({'success': False, 'error': 'Erreur serveur'})

@app.route('/end_call', methods=['POST'])
@login_required
def end_call():
    """Terminer un appel en cours"""
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return jsonify({'success': False, 'error': 'Utilisateur non authentifié'})
    
    try:
        data = request.get_json()
        other_user_id = data.get('other_user_id')
        call_duration = data.get('duration', 0)
        
        # Dans une vraie application, ici on sauvegarderait les statistiques d'appel
        # et on notifierait l'autre utilisateur que l'appel est terminé
        
        return jsonify({
            'success': True,
            'message': 'Appel terminé',
            'duration': call_duration
        })
        
    except Exception as e:
        print(f"Erreur end_call: {e}")
        return jsonify({'success': False, 'error': 'Erreur serveur'})

@app.route('/private_chat/<int:friend_id>')
@login_required
def private_chat(friend_id):
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return redirect(url_for('login'))
    
    try:
        friend = User.query.get(friend_id)
        if not friend or not user.is_friend_with(friend):
            flash('Utilisateur introuvable ou pas dans votre liste d\'amis')
            return redirect(url_for('private_messages'))
        
        # Récupérer les 50 derniers messages
        messages = PrivateMessage.query.filter(
            ((PrivateMessage.sender_id == user.id) & (PrivateMessage.receiver_id == friend.id)) |
            ((PrivateMessage.sender_id == friend.id) & (PrivateMessage.receiver_id == user.id))
        ).order_by(PrivateMessage.created_at.desc()).limit(50).all()[::-1]
        
        # Marquer les messages comme lus
        PrivateMessage.query.filter(
            PrivateMessage.sender_id == friend.id,
            PrivateMessage.receiver_id == user.id,
            PrivateMessage.is_read == False
        ).update({'is_read': True})
        db.session.commit()
        
        return render_template('private_chat.html', user=user, friend=friend, messages=messages)
    except Exception as e:
        print(f"Erreur chat privé: {e}")
        flash('Erreur d\'accès au chat privé')
        return redirect(url_for('private_messages'))

@app.route('/send_private_message/<int:friend_id>', methods=['POST'])
@login_required
def send_private_message(friend_id):
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return redirect(url_for('login'))
    
    try:
        friend = User.query.get(friend_id)
        if not friend or not user.is_friend_with(friend):
            return redirect(url_for('private_messages'))
        
        message_text = request.form.get('message', '').strip()
        if message_text and len(message_text) <= 500:
            message = PrivateMessage()
            message.sender_id = user.id
            message.receiver_id = friend.id
            message.content = message_text
            db.session.add(message)
            db.session.commit()
        
        return redirect(url_for('private_chat', friend_id=friend_id))
    except Exception as e:
        print(f"Erreur envoi message privé: {e}")
        return redirect(url_for('private_chat', friend_id=friend_id))

@app.route('/get_private_messages/<int:friend_id>')
@login_required
def get_private_messages(friend_id):
    """Endpoint pour récupérer les messages privés (polling pour 3DS)"""
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return ""
    
    try:
        friend = User.query.get(friend_id)
        if not friend or not user.is_friend_with(friend):
            return ""
        
        # Récupérer les 20 derniers messages
        messages = PrivateMessage.query.filter(
            ((PrivateMessage.sender_id == user.id) & (PrivateMessage.receiver_id == friend.id)) |
            ((PrivateMessage.sender_id == friend.id) & (PrivateMessage.receiver_id == user.id))
        ).order_by(PrivateMessage.created_at.desc()).limit(20).all()[::-1]
        
        # Retourner du HTML simple pour compatibilité 3DS
        html = ""
        for message in messages:
            is_own = message.sender_id == user.id
            sender_name = user.username if is_own else friend.username
            timestamp = message.created_at.strftime('%H:%M')
            css_class = 'own' if is_own else 'other'
            html += f'<div class="private-message {css_class}"><div class="message-content">{message.content}</div><div class="message-time">{timestamp}</div></div>'
        
        return html
    except Exception as e:
        print(f"Erreur get_private_messages: {e}")
        return ""

@app.route('/user_profile/<int:user_id>')
@login_required
def user_profile(user_id):
    user = get_current_user()
    if not user:
        return redirect(url_for('login'))
    
    try:
        profile_user = User.query.get(user_id)
        if not profile_user:
            flash('Utilisateur introuvable')
            return redirect(url_for('index'))
        
        return render_template('user_profile.html', user=user, profile_user=profile_user)
    except Exception as e:
        print(f"Erreur profil utilisateur: {e}")
        return redirect(url_for('index'))

@app.route('/get_messages/<int:room_id>')
def get_messages(room_id):
    """Endpoint pour récupérer les nouveaux messages (polling pour 3DS)"""
    user = get_current_user()
    if not user:
        return "[]"
    
    try:
        room = Room.query.get(room_id)
        if not room:
            return "[]"
        
        # Récupérer les 20 derniers messages
        messages = RoomMessage.query.filter_by(room_id=room_id).order_by(RoomMessage.created_at.desc()).limit(20).all()[::-1]
        members = room.members.all()
        
        # Retourner du HTML simple plutôt que du JSON pour compatibilité 3DS
        html = ""
        for msg in messages:
            username = msg.user.username if msg.user else 'Utilisateur'
            timestamp = msg.created_at.strftime('%H:%M')
            content = msg.content
            html += f'<div class="message"><span class="author">{username}</span> <span class="time">{timestamp}</span><br>{content}</div>'
        
        # Ajouter la liste des utilisateurs
        html += '<div id="users-list">'
        for member in members:
            if member.user:
                html += f'<span class="user-badge">{member.user.username}</span> '
        html += '</div>'
        
        return html
    except Exception as e:
        print(f"Erreur get_messages: {e}")
        return ""

@app.route('/leave_room/<int:room_id>')
@login_required
def leave_room(room_id):
    user = get_current_user()
    if not user or not hasattr(user, 'id'):
        return redirect(url_for('index'))
    
    try:
        room = Room.query.get(room_id)
        if room:
            # Retirer l'utilisateur du salon
            member = RoomMember.query.filter_by(room_id=room_id, user_id=user.id).first()
            if member:
                db.session.delete(member)
                db.session.commit()
            
            # Si l'utilisateur est le propriétaire d'un salon privé et qu'il n'y a plus de membres, supprimer le salon
            if (room.owner_id == user.id and 
                not room.is_public and 
                room.get_member_count() == 0):
                db.session.delete(room)
                db.session.commit()
    except Exception as e:
        print(f"Erreur leave_room: {e}")
    
    user_param = request.args.get('user')
    if user_param:
        return redirect(url_for('index', user=user_param))
    return redirect(url_for('index'))

# API endpoints pour 3DS homebrew
@app.route('/api/rooms')
def api_rooms():
    """API pour lister les salons publics"""
    try:
        rooms = Room.query.filter_by(is_public=True).all()
        rooms_data = []
        for room in rooms:
            rooms_data.append({
                'id': room.id,
                'name': room.name,
                'description': room.description,
                'member_count': room.get_member_count(),
                'message_count': room.get_message_count()
            })
        return jsonify(rooms_data)
    except Exception as e:
        print(f"Erreur API rooms: {e}")
        return jsonify([])

@app.route('/api/room/<int:room_id>/messages')
def api_room_messages(room_id):
    """API pour récupérer les messages d'un salon"""
    try:
        messages = RoomMessage.query.filter_by(room_id=room_id).order_by(RoomMessage.created_at.desc()).limit(20).all()
        messages_data = []
        for msg in messages:
            messages_data.append({
                'id': msg.id,
                'username': msg.user.username if msg.user else 'Utilisateur',
                'content': msg.content,
                'timestamp': msg.created_at.strftime('%H:%M')
            })
        return jsonify(list(reversed(messages_data)))
    except Exception as e:
        print(f"Erreur API messages: {e}")
        return jsonify([])