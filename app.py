from flask import Flask, render_template
from models import db, User, Semestre, Bloc, Competence
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask import request, redirect, url_for, flash
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import json
import os

app = Flask(__name__)

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

# Dossier où seront sauvegardées les images envoyées depuis l'admin
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- ROUTES DES PAGES STATIQUES ---

@app.route('/')
def index():
    # On remplace le fichier JSON par un dictionnaire Python direct
    profil_data = {
        "nom": "Noa Jodry",
        "email": "jodrynoa7@gmail.com",
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
def competences_page():
    from models import Semestre, Bloc, Competence
    # On récupère le filtre dans l'URL (par défaut "all")
    filtre = request.args.get('filtre', 'all')
    semestres = Semestre.query.all()
    
    return render_template('competences.html', semestres=semestres, filtre=filtre)

@app.route('/mentions_legales')
def mentions_legales():
    return render_template('mentions_legales.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    semestres = Semestre.query.all()
    blocs = Bloc.query.all()
    competences = Competence.query.all()  # <-- LIGNE MANQUANTE AJOUTÉE ICI
    
    # On ajoute competences=competences à la fin pour les envoyer au tableau
    return render_template('admin.html', semestres=semestres, blocs=blocs, competences=competences)

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
    db.session.delete(comp)
    db.session.commit()
    flash("🗑️ Compétence supprimée.", "danger") # <-- LIGNE À AJOUTER
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
    # 1. On récupère les infos de base
    bloc_id = request.form.get('bloc_id')
    code = request.form.get('code')
    nom = request.form.get('nom')
    niveau = request.form.get('niveau')
    
    # 2. On récupère les textes détaillés
    fait = request.form.get('ce_que_jai_fait')
    pourquoi = request.form.get('pourquoi')
    comment = request.form.get('comment')
    diff = request.form.get('difficultes')
    appris = request.form.get('appris')
    autrement = request.form.get('autrement')
    
    # 3. Gestion des images
    image1_filename = None
    image2_filename = None
    
    if 'image1' in request.files:
        img1 = request.files['image1']
        if img1.filename != '':
            image1_filename = secure_filename(img1.filename)
            img1.save(os.path.join(app.config['UPLOAD_FOLDER'], image1_filename))
            
    if 'image2' in request.files:
        img2 = request.files['image2']
        if img2.filename != '':
            image2_filename = secure_filename(img2.filename)
            img2.save(os.path.join(app.config['UPLOAD_FOLDER'], image2_filename))

    # 4. On sauvegarde le tout dans la base de données
    nouvelle_comp = Competence(
        code=code, nom=nom, niveau=niveau, bloc_id=bloc_id,
        ce_que_jai_fait=fait, pourquoi=pourquoi, comment=comment,
        difficultes=diff, appris=appris, autrement=autrement,
        image1=image1_filename, image2=image2_filename
    )
    db.session.add(nouvelle_comp)
    db.session.commit()
    return redirect(url_for('admin_dashboard'))
    db.session.add(nouvelle_comp)
    db.session.commit()
    flash("✅ La compétence a bien été ajoutée !", "success") # <-- LIGNE À AJOUTER
    return redirect(url_for('admin_dashboard'))

@app.route('/edit_skill/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_skill(id):
    comp = Competence.query.get_or_404(id)
    blocs = Bloc.query.all()
    
    if request.method == 'POST':
        # Mise à jour des infos de base
        comp.code = request.form.get('code')
        comp.nom = request.form.get('nom')
        comp.niveau = request.form.get('niveau')
        comp.bloc_id = request.form.get('bloc_id')
        
        # Mise à jour des textes TinyMCE
        comp.ce_que_jai_fait = request.form.get('ce_que_jai_fait')
        comp.pourquoi = request.form.get('pourquoi')
        comp.comment = request.form.get('comment')
        comp.difficultes = request.form.get('difficultes')
        comp.appris = request.form.get('appris')
        comp.autrement = request.form.get('autrement')
        
        # Mise à jour des images (seulement si on en choisit de nouvelles)
        if 'image1' in request.files:
            img1 = request.files['image1']
            if img1.filename != '':
                filename1 = secure_filename(img1.filename)
                img1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
                comp.image1 = filename1
                
        if 'image2' in request.files:
            img2 = request.files['image2']
            if img2.filename != '':
                filename2 = secure_filename(img2.filename)
                img2.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
                comp.image2 = filename2
        
        db.session.commit()
        flash("✏️ La compétence a été modifiée avec succès !", "success")
        return redirect(url_for('admin_dashboard'))
        
    return render_template('edit_skill.html', comp=comp, blocs=blocs)

@app.route('/send_message', methods=['POST'])
def send_message():
    # 1. On récupère ce que l'utilisateur a tapé
    nom = request.form.get('nom')
    email = request.form.get('email')
    message = request.form.get('message')
    
    # 2. Simulation de réception (Ça va s'afficher dans ton terminal Docker !)
    print("\n" + "="*50)
    print(f"📩 NOUVEAU MESSAGE REÇU SUR LE PORTFOLIO !")
    print(f"👤 De : {nom} ({email})")
    print(f"💬 Message : {message}")
    print("="*50 + "\n")
    
    # 3. On affiche la bulle de confirmation grâce aux Flash Messages créés tout à l'heure
    flash(f"🚀 Merci {nom} ! Votre message a bien été envoyé. Je vous réponds très vite.", "success")
    
    # 4. On renvoie l'utilisateur sur la page d'accueil
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)