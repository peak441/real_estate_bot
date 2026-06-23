from database.db import db
from database.models import User


def create_user(telegram_id, username):

    user = db.session.query(User).filter(User.telegram_id == telegram_id).first()

    if user:
        return user

    user = User(
        telegram_id=telegram_id,
        username=username
    )

    db.session.add(user)
    db.session.commit()

    return user