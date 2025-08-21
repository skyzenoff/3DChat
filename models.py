from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    bio = db.Column(db.Text, default='')
    profile_image = db.Column(db.Text)  # Base64 encoded image
    status = db.Column(db.String(10), default='online')  # online/offline
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    sent_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.requester_id', backref='requester', lazy='dynamic')
    received_friend_requests = db.relationship('Friendship', foreign_keys='Friendship.addressee_id', backref='addressee', lazy='dynamic')
    sent_messages = db.relationship('PrivateMessage', foreign_keys='PrivateMessage.sender_id', backref='sender', lazy='dynamic')
    received_messages = db.relationship('PrivateMessage', foreign_keys='PrivateMessage.receiver_id', backref='receiver', lazy='dynamic')
    owned_rooms = db.relationship('Room', backref='owner', lazy='dynamic')
    room_messages = db.relationship('RoomMessage', backref='user', lazy='dynamic')
    room_memberships = db.relationship('RoomMember', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_friends(self):
        """Retourne la liste des amis acceptés"""
        friends_as_requester = db.session.query(User).join(
            Friendship, User.id == Friendship.addressee_id
        ).filter(Friendship.requester_id == self.id, Friendship.status == 'accepted').all()
        
        friends_as_addressee = db.session.query(User).join(
            Friendship, User.id == Friendship.requester_id
        ).filter(Friendship.addressee_id == self.id, Friendship.status == 'accepted').all()
        
        return friends_as_requester + friends_as_addressee
    
    def is_friend_with(self, user):
        """Vérifie si l'utilisateur est ami avec un autre utilisateur"""
        return Friendship.query.filter(
            ((Friendship.requester_id == self.id) & (Friendship.addressee_id == user.id)) |
            ((Friendship.requester_id == user.id) & (Friendship.addressee_id == self.id))
        ).filter(Friendship.status == 'accepted').first() is not None
    
    def has_pending_request_from(self, user):
        """Vérifie si l'utilisateur a une demande d'ami en attente de cet utilisateur"""
        return Friendship.query.filter(
            Friendship.requester_id == user.id,
            Friendship.addressee_id == self.id,
            Friendship.status == 'pending'
        ).first() is not None
    
    def has_sent_request_to(self, user):
        """Vérifie si l'utilisateur a envoyé une demande d'ami à cet utilisateur"""
        return Friendship.query.filter(
            Friendship.requester_id == self.id,
            Friendship.addressee_id == user.id,
            Friendship.status == 'pending'
        ).first() is not None

class Friendship(db.Model):
    __tablename__ = 'friendships'
    
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    addressee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(10), default='pending')  # pending/accepted/blocked
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('requester_id', 'addressee_id', name='unique_friendship'),)

class PrivateMessage(db.Model):
    __tablename__ = 'private_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(10), default='text')  # text/image/voice
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

class Room(db.Model):
    __tablename__ = 'rooms'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    is_public = db.Column(db.Boolean, default=True)
    code = db.Column(db.String(6))  # Code pour salons privés
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relations
    messages = db.relationship('RoomMessage', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    members = db.relationship('RoomMember', backref='room', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_member_count(self):
        return self.members.count()
    
    def get_recent_messages(self, limit=20):
        return list(reversed(self.messages.order_by(RoomMessage.created_at.desc()).limit(limit).all()))

class RoomMessage(db.Model):
    __tablename__ = 'room_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(10), default='text')  # text/image/voice/system
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RoomMember(db.Model):
    __tablename__ = 'room_members'
    
    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('room_id', 'user_id', name='unique_room_member'),)