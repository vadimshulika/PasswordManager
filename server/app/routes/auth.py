import jwt
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.user import User
from app.models.session import Session

auth_bp = Blueprint('auth', __name__)

def generate_tokens(user_id):
    """Вспомогательная функция для генерации JWT Access и Refresh токенов."""
    access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=15)
    refresh_token_expires = datetime.now(timezone.utc) + timedelta(days=7)

    access_payload = {
        'user_id': user_id,
        'exp': access_token_expires,
        'type': 'access'
    }
    
    refresh_payload = {
        'user_id': user_id,
        'exp': refresh_token_expires,
        'type': 'refresh'
    }

    secret = current_app.config['JWT_SECRET_KEY']
    
    access_token = jwt.encode(access_payload, secret, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, secret, algorithm='HS256')

    return access_token, refresh_token, refresh_token_expires


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}

    nickname = data.get('nickname')
    email = data.get('email')
    password_hash = data.get('password_hash')  # Auth Hash от клиента
    kdf_salt = data.get('kdf_salt')

    if not all([nickname, email, password_hash, kdf_salt]):
        return jsonify({'error': 'Все поля обязательны: nickname, email, password_hash, kdf_salt'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Пользователь с таким email уже существует'}), 409

    # Хэшируем Auth Hash на стороне сервера для защиты в БД
    server_password_hash = generate_password_hash(password_hash)

    new_user = User(
        nickname=nickname,
        email=email,
        password_hash=server_password_hash,
        kdf_salt=kdf_salt
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Пользователь успешно зарегистрирован'}), 201


@auth_bp.route('/kdf-salt', methods=['GET'])
def get_kdf_salt():
    email = request.args.get('email')
    
    if not email:
        return jsonify({'error': 'Параметр email обязателен'}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Пользователь не найден'}), 404

    return jsonify({'kdf_salt': user.kdf_salt}), 200


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}

    email = data.get('email')
    password_hash = data.get('password_hash')
    device_info = data.get('device_info', 'Unknown Device')

    if not email or not password_hash:
        return jsonify({'error': 'Требуются email и password_hash'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password_hash, password_hash):
        return jsonify({'error': 'Неверный email или пароль'}), 401

    # Генерация токенов
    access_token, refresh_token, refresh_expires = generate_tokens(user.id)

    # Сохраняем сессию в БД
    new_session = Session(
        user_id=user.id,
        refresh_token_hash=generate_password_hash(refresh_token),
        device_info=device_info,
        ip_address=request.remote_addr,
        expires_at=refresh_expires
    )

    db.session.add(new_session)
    db.session.commit()

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': user.id,
            'nickname': user.nickname,
            'email': user.email
        }
    }), 200