from app import app, db
from models import Semestre, Bloc, Competence, User
from werkzeug.security import generate_password_hash

with app.app_context():
    print("Vérification de la base de données...")
    
    # 1. Vérifier et créer le Semestre
    s1 = Semestre.query.filter_by(nom="Semestre 1").first()
    if not s1:
        s1 = Semestre(nom="Semestre 1")
        db.session.add(s1)
        db.session.commit()
        print(" -> Semestre 1 ajouté")

    # 2. Vérifier et créer le Bloc
    b1 = Bloc.query.filter_by(nom="Administrer les réseaux").first()
    if not b1:
        b1 = Bloc(nom="Administrer les réseaux", semestre_id=s1.id)
        db.session.add(b1)
        db.session.commit()
        print(" -> Bloc ajouté")

    # 3. Vérifier et créer la Compétence
    c1 = Competence.query.filter_by(code="AC 11.02").first()
    if not c1:
        c1 = Competence(
            code="AC 11.02",
            nom="Exploiter des systèmes d'exploitation serveurs",
            niveau="acquis",
            bloc_id=b1.id
        )
        db.session.add(c1)
        db.session.commit()
        print(" -> Compétence ajoutée")

    # 4. Vérifier et créer l'Admin
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()
        print(" -> Compte admin ajouté")
        
    print("Script terminé avec succès ! Tout est en ordre.")