from sqlalchemy.orm import Session

import models
import schemas


def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user_id: str):
    db_user = models.User(id=user_id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_or_create_user(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        return db_user
    return create_user(db, user_id)


def get_stocks(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    return db_user.stocks


def update_stocks(db: Session, user_id: str, stocks: list[str]):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.stocks = stocks
    db.commit()
    db.refresh(db_user)
    return db_user.stocks


def update_openai_key(db: Session, user_id: str, openai_key: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    db_user.openai_key = openai_key
    db.commit()
    db.refresh(db_user)
    return db_user.openai_key


def check_openai_key(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    return db_user.openai_key is not None
