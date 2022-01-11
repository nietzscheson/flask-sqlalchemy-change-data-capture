from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from sqlalchemy.orm.attributes import get_history
from uuid import uuid4
from flask import g
import json
db = SQLAlchemy()


class Resource(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())


class User(Resource):
    __tablename = "user"
    __versioned__ = {}
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(120), nullable=False)

    
class Post(Resource):
    __tablename = "post"
    __versioned__ = {}
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text(), nullable=True)


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payload = db.Column(db.Text(), nullable=True)
    model = db.Column(db.String(80), nullable=False)
    model_id = db.Column(db.Integer)
    event = db.Column(db.String(80), nullable=False)
    

@event.listens_for(db.session, 'after_flush')
def db_after_flush(session, flush_context):
    for instance in session.new:
        if hasattr(instance, "__versioned__"):
            data = { x.name: str(getattr(instance, x.name)) for x in instance.__table__.columns }
            al = AuditLog(model=instance.__tablename__, model_id=instance.id,  event="create", payload=str(data), )
            session.add(al)


@event.listens_for(db.session, 'before_flush')
def db_before_flush(session, flush_context, instances):
    for instance in session.dirty:
        if hasattr(instance, "__versioned__"):
            history = { x.name: str(getattr(instance, x.name)) for x in instance.__table__.columns if get_history(instance, x.name).deleted }
            if len(history):
                al = AuditLog(model=instance.__tablename__, model_id=instance.id,  event="edit", payload=json.dumps(history))
                session.add(al)

    for instance in session.deleted:
        if hasattr(instance, "__versioned__"):
            history = { x.name: str(get_history(instance, x.name).unchanged[0]) for x in instance.__table__.columns }
            if len(history):
                al = AuditLog(model=instance.__tablename__, model_id=instance.id,  event="delete", payload=json.dumps(history))
                session.add(al)