from app import app, db
from models import Semestre, Bloc, Competence, User
from werkzeug.security import generate_password_hash

with app.app_context():
    print("Vérification de la base de données...")
    
    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            username="admin",
            mdp=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()
        print(" -> Compte admin ajouté")
        
    print("Script terminé avec succès ! Tout est en ordre.")