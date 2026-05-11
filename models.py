from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    mdp = db.Column(db.String(256), nullable=False) # Sécurité : mot de passe hashé

class Semestre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), nullable=False) # ex: Semestre 1
    blocs = db.relationship('Bloc', backref='semestre', lazy=True)

class Bloc(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(200), nullable=False) # ex: BC1 - Administrer
    semestre_id = db.Column(db.Integer, db.ForeignKey('semestre.id'), nullable=False)
    competences = db.relationship('Competence', backref='bloc', lazy=True)

class Competence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), nullable=False) # ex: AC11.01
    nom = db.Column(db.String(500), nullable=False)
    niveau = db.Column(db.String(100), default="non acquis") # Niveaux requis : non acquis, expert, etc.
    bloc_id = db.Column(db.Integer, db.ForeignKey('bloc.id'), nullable=False)