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
    code = db.Column(db.String(20), nullable=False)
    nom = db.Column(db.String(200), nullable=False)
    niveau = db.Column(db.String(50))
    bloc_id = db.Column(db.Integer, db.ForeignKey('bloc.id'), nullable=False)
    
    # --- LES NOUVEAUX TEXTES DÉTAILLÉS ---
    ce_que_jai_fait = db.Column(db.Text, nullable=True)
    pourquoi = db.Column(db.Text, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    difficultes = db.Column(db.Text, nullable=True)
    appris = db.Column(db.Text, nullable=True)
    autrement = db.Column(db.Text, nullable=True)
    
    # --- LES IMAGES (Traces ciblées) ---
    # On stockera le nom du fichier image (ex: "script_ad.png")
    image1 = db.Column(db.String(200), nullable=True)
    image2 = db.Column(db.String(200), nullable=True)