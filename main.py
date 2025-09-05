from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text, DateTime, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from security import hash_password, check_password, encrypt_message, decrypt_message
import datetime
import os
import sys

# Настройка базы данных
Base = declarative_base()
engine = create_engine("sqlite:///social_network.db")
Session = sessionmaker(bind=engine)

# Таблица участников чатов
chat_members = Table(
    'chat_members', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('chat_id', Integer, ForeignKey('chats.id'))
)

# Модели
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    password_hash = Column(String(60))
    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")
    sent_messages = relationship("Message", back_populates="sender")

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'))
    post_id = Column(Integer, ForeignKey('posts.id'))
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

class Chat(Base):
    __tablename__ = 'chats'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    members = relationship("User", secondary=chat_members)
    messages = relationship("Message", back_populates="chat")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    content_encrypted = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    sender_id = Column(Integer, ForeignKey('users.id'))
    chat_id = Column(Integer, ForeignKey('chats.id'))
    sender = relationship("User", back_populates="sent_messages")
    chat = relationship("Chat", back_populates="messages")

# Логика

def init_db():
    Base.metadata.create_all(engine)

def create_user(username, password):
    session = Session()
    if session.query(User).filter_by(username=username).first():
        print(f"⚠️ Пользователь '{username}' уже существует.")
        return session.query(User).filter_by(username=username).first()
    hashed = hash_password(password)
    user = User(username=username, password_hash=hashed)
    session.add(user)
    session.commit()
    print(f"✅ Пользователь '{username}' создан.")
    return user

def authenticate(username, password):
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    if user and check_password(password, user.password_hash):
        print(f"🔐 Вход выполнен как {username}")
        return user
    print("❌ Ошибка входа.")
    return None

def create_post(user_id, content):
    session = Session()
    user = session.query(User).get(user_id)
    post = Post(content=content, author=user)
    session.add(post)
    session.commit()
    print(f"📝 Пост от {user.username}: {content}")

def comment_on_post(user_id, post_id, content):
    session = Session()
    user = session.query(User).get(user_id)
    post = session.query(Post).get(post_id)
    if post and user:
        comment = Comment(content=content, author=user, post=post)
        session.add(comment)
        session.commit()
        print(f"💬 Комментарий от {user.username}: {content}")
    else:
        print("❌ Пост или пользователь не найден.")

def create_chat(user_ids, name=None):
    session = Session()
    users = session.query(User).filter(User.id.in_(user_ids)).all()
    chat = Chat(name=name, members=users)
    session.add(chat)
    session.commit()
    print(f"💬 Чат '{name or 'Private'}' создан.")
    return chat

def send_message(chat_id, sender_id, content):
    session = Session()
    encrypted = encrypt_message(content)
    message = Message(content_encrypted=encrypted, chat_id=chat_id, sender_id=sender_id)
    session.add(message)
    session.commit()
    print(f"📨 Сообщение отправлено.")

def read_messages(chat_id):
    session = Session()
    chat = session.query(Chat).get(chat_id)
    if not chat:
        print("❌ Чат не найден.")
        return
    messages = session.query(Message).filter_by(chat_id=chat_id).order_by(Message.timestamp).all()
    print(f"\n🔓 Сообщения в чате: {chat.name or 'Private'}")
    for msg in messages:
        decrypted = decrypt_message(msg.content_encrypted)
        print(f"[{msg.timestamp}] {msg.sender.username}: {decrypted}")

# Запуск
if __name__ == "__main__":
    # Проверка наличия ключа
    if not os.path.exists("secret.key"):
        print("❗ Сначала создай ключ: открой Python и вызови generate_key() из security.py")
        sys.exit(1)

    init_db()

    # Создание пользователей
    alice = create_user("alice", "alicepass")
    bob = create_user("bob", "bobpass")

    # Вход
    alice = authenticate("alice", "alicepass")
    bob = authenticate("bob", "bobpass")

    if not alice or not bob:
        print("❌ Ошибка входа.")
        sys.exit(1)

    # Пост и комментарий
    create_post(alice.id, "Это мой первый пост!")
    comment_on_post(bob.id, 1, "Поздравляю!")

    # Чат и сообщения
    chat = create_chat([alice.id, bob.id], name="Чат друзей")
    send_message(chat.id, alice.id, "Привет, Боб!")
    send_message(chat.id, bob.id, "Привет, Алиса!")

    # Просмотр
    read_messages(chat.id)
