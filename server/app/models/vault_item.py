from datetime import datetime, timezone
from app.extensions import db

class VaultItem(db.Model):
    __tablename__ = 'vault_items'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, index=True)
    title = db.Column(db.String(150), nullable=False)
    encrypted_payload = db.Column(db.Text, nullable=False)
    iv = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_viewed_at = db.Column(db.DateTime, nullable=True)