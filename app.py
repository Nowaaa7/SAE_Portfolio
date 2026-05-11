from flask import Flask, render_template
from models import db, User, Semestre, Bloc, Competence
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, redirect, url_for, flash
from werkzeug.security import check_password_hash
import json
import os

app = Flask(__name__)

# Pour le développement, on peut utiliser SQLite. 
# On passera sur PostgreSQL quand on fera le Docker (Séance 1/4)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SECRET_KEY'] = 'une_cle_secrete_provisoire'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# On lie l'instance db (créée dans models.py) à notre application Flask
db.init_app(app)

# Création des tables dans la base de données au démarrage
with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- ROUTES DES PAGES STATIQUES ---

@app.route('/')
def index():
    # On remplace le fichier JSON par un dictionnaire Python direct
    profil_data = {
        "nom": "Noa Jodry",
        "email": "noajodry7@gmail.com",
        "bio": "Étudiant en BUT Réseaux & Télécommunications. Curieux des architectures réseau.",
        "github": "https://github.com/Nowaaa7",
        "linkedin": "https://www.linkedin.com/in/noa-jodry/"
    }
    return render_template('index.html', profil=profil_data)

@app.route('/cv')
def cv():
    return render_template('cv.html')

@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')

@app.route('/competences')
def competences():
    # On récupère tous les semestres, et grâce aux "relationships" dans models.py,
    # on aura accès aux blocs et aux compétences liés.
    tous_les_semestres = Semestre.query.all()
    return render_template('competences.html', semestres=tous_les_semestres)

@app.route('/mentions_legales')
def mentions_legales():
    return render_template('mentions_legales.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    semestres = Semestre.query.all()
    # On affiche aussi les blocs pour le formulaire d'ajout
    blocs = Bloc.query.all() 
    return render_template('admin.html', semestres=semestres, blocs=blocs)

# Route pour modifier le niveau d'une compétence existante
@app.route('/update_skill/<int:id>', methods=['POST'])
@login_required
def update_skill(id):
    comp = Competence.query.get_or_404(id)
    comp.niveau = request.form.get('niveau')
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/delete_skill/<int:id>', methods=['POST'])
@login_required
def delete_skill(id):
    # On récupère la compétence ou on renvoie une erreur 404 si elle n'existe pas
    comp = Competence.query.get_or_404(id)
    db.session.delete(comp)
    db.session.commit()
    # Message de confirmation (optionnel)
    return redirect(url_for('admin_dashboard'))

@app.route('/add_skill', methods=['POST'])
@login_required
def add_skill():
    # On récupère ce que tu as tapé dans le formulaire
    code = request.form.get('code')
    nom = request.form.get('nom')
    niveau = request.form.get('niveau')
    
    # On cherche le premier bloc par défaut (Administrer les réseaux)
    from models import Bloc
    bloc_par_defaut = Bloc.query.first()
    
    # On crée et on sauvegarde la nouvelle compétence
    nouvelle_comp = Competence(code=code, nom=nom, niveau=niveau, bloc_id=bloc_par_defaut.id)
    db.session.add(nouvelle_comp)
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))    

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # On récupère ce que l'utilisateur a tapé dans le formulaire
        form_username = request.form.get('username')
        form_password = request.form.get('password')
        
        # On cherche l'utilisateur dans la base de données
        user = User.query.filter_by(username=form_username).first()
        
        # Si l'utilisateur existe et que le mot de passe correspond
        if user and check_password_hash(user.mdp, form_password):
            login_user(user)
            return redirect(url_for('index')) # Ou vers une page '/admin' si tu en as une
        else:
            flash('Identifiants incorrects, veuillez réessayer.')
            
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_semester', methods=['POST'])
@login_required
def add_semester():
    nom = request.form.get('nom')
    nouveau_s = Semestre(nom=nom)
    db.session.add(nouveau_s)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/add_block', methods=['POST'])
@login_required
def add_block():
    nom = request.form.get('nom')
    semestre_id = request.form.get('semestre_id')
    nouveau_b = Bloc(nom=nom, semestre_id=semestre_id)
    db.session.add(nouveau_b)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# Modifie aussi ton ancienne route add_skill pour qu'elle accepte le bloc_id du formulaire
@app.route('/add_skill', methods=['POST'])
@login_required
def add_skill():
    code = request.form.get('code')
    nom = request.form.get('nom')
    niveau = request.form.get('niveau')
    bloc_id = request.form.get('bloc_id') # On récupère le bloc choisi
    
    nouvelle_comp = Competence(code=code, nom=nom, niveau=niveau, bloc_id=bloc_id)
    db.session.add(nouvelle_comp)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    app.run(debug=True)