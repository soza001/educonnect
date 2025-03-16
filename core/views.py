import matplotlib.pyplot as plt
import seaborn as sns
import io
import urllib, base64
from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from firebase_admin import auth, firestore, messaging
from fpdf import FPDF
from django.shortcuts import redirect
import firebase_admin
from firebase_admin import auth

db = firestore.client()


def home(request):
    """Rediriger la page d'accueil vers le tableau de bord"""
    return redirect('/dashboard/')


# 📌 TABLEAU DE BORD
def dashboard(request):
    """ Générer les statistiques et afficher le tableau de bord """
    # Récupération des données depuis Firestore
    total_eleves = len(list(db.collection("eleves").stream()))
    total_classes = len(list(db.collection("classes").stream()))
    total_enseignants = len(list(db.collection("enseignants").stream()))

    # Générer un graphique des élèves par classe
    classes = db.collection("classes").stream()
    data = {"Classes": [], "Nombre d'élèves": []}

    for classe in classes:
        class_id = classe.id
        nb_eleves = len(list(db.collection("eleves").where("class_id", "==", class_id).stream()))
        data["Classes"].append(classe.to_dict().get("name", "Inconnu"))
        data["Nombre d'élèves"].append(nb_eleves)

    # Création du graphique
    plt.figure(figsize=(8, 5))
    sns.barplot(x=data["Classes"], y=data["Nombre d'élèves"], palette="Blues_d")
    plt.xticks(rotation=45)
    plt.xlabel("Classes")
    plt.ylabel("Nombre d'élèves")
    plt.title("Répartition des élèves par classe")

    # Sauvegarde en format image
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    buffer.close()

    return render(request, "dashboard.html", {
        "total_eleves": total_eleves,
        "total_classes": total_classes,
        "total_enseignants": total_enseignants,
        "chart": image_base64
    })

# 📌 GESTION DES CLASSES
def view_classes(request):
    """Afficher la liste des classes"""
    classes = [doc.to_dict() | {'id': doc.id} for doc in db.collection('classes').stream()]
    return render(request, 'classes.html', {'classes': classes})

def add_class(request):
    """Créer une nouvelle classe"""
    name = request.GET.get('name')
    school_id = request.GET.get('school_id')

    if not name or not school_id:
        return JsonResponse({'error': 'Nom et ID école requis'}, status=400)

    class_ref = db.collection('classes').add({'name': name, 'school_id': school_id})
    return JsonResponse({'message': 'Classe ajoutée !', 'id': class_ref[1].id})

def delete_class(request):
    """Supprimer une classe"""
    class_id = request.GET.get('class_id')

    if not class_id:
        return JsonResponse({'error': 'ID classe requis'}, status=400)

    db.collection('classes').document(class_id).delete()
    return JsonResponse({'message': 'Classe supprimée !'})

# 📌 GESTION DES EMPLOIS DU TEMPS
def view_schedules(request):
    """Afficher la liste des emplois du temps"""
    schedules = [doc.to_dict() | {'id': doc.id} for doc in db.collection('schedules').stream()]
    return render(request, 'emplois.html', {'emplois': schedules})

def add_schedule(request):
    """Ajouter un emploi du temps pour une classe"""
    class_id = request.GET.get('class_id')
    day = request.GET.get('day')
    time = request.GET.get('time')
    subject = request.GET.get('subject')

    if not all([class_id, day, time, subject]):
        return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

    schedule_ref = db.collection('schedules').add({
        'class_id': class_id,
        'day': day,
        'time': time,
        'subject': subject
    })

    return JsonResponse({'message': 'Emploi du temps ajouté !', 'id': schedule_ref[1].id})

def delete_schedule(request):
    """Supprimer un emploi du temps"""
    schedule_id = request.GET.get('schedule_id')

    if not schedule_id:
        return JsonResponse({'error': 'ID requis'}, status=400)

    db.collection('schedules').document(schedule_id).delete()
    return JsonResponse({'message': 'Emploi du temps supprimé !'})

# 📌 GESTION DES NOTES
def view_notes(request):
    """Afficher la liste des notes"""
    notes = [doc.to_dict() for doc in db.collection('notes').stream()]
    return render(request, 'notes.html', {'notes': notes})

def add_note(request):
    """Ajouter une note pour un élève"""
    eleve_id = request.GET.get('eleve_id')
    matiere = request.GET.get('matiere')
    note = request.GET.get('note')

    if not all([eleve_id, matiere, note]):
        return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

    try:
        note = float(note)
    except ValueError:
        return JsonResponse({'error': 'La note doit être un nombre'}, status=400)

    note_ref = db.collection('notes').add({
        'eleve_id': eleve_id,
        'matiere': matiere,
        'note': note
    })

    return JsonResponse({'message': 'Note ajoutée !', 'id': note_ref[1].id})

# 📌 GÉNÉRATION DES BULLETINS SCOLAIRES
def generate_report_card(request):
    """Générer un bulletin scolaire en PDF"""
    eleve_id = request.GET.get('eleve_id')

    if not eleve_id:
        return JsonResponse({'error': 'ID élève requis'}, status=400)

    notes_snapshot = db.collection('notes').where('eleve_id', '==', eleve_id).stream()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Bulletin Scolaire", ln=True, align='C')

    for doc in notes_snapshot:
        data = doc.to_dict()
        pdf.cell(200, 10, txt=f"{data['matiere']}: {data['note']}", ln=True)

    file_path = f"bulletins/bulletin_{eleve_id}.pdf"
    pdf.output(file_path)

    return FileResponse(open(file_path, "rb"), content_type="application/pdf")

# 📌 NOTIFICATIONS
def send_notification(request):
    """Envoyer une notification aux utilisateurs"""
    title = request.GET.get('title')
    body = request.GET.get('body')

    if not all([title, body]):
        return JsonResponse({'error': 'Titre et message requis'}, status=400)

    message = messaging.Message(
        notification=messaging.Notification(title=title, body=body),
        topic="all_users"
    )

    messaging.send(message)
    return JsonResponse({'message': 'Notification envoyée !'})

# 📌 FORUM
def create_forum_topic(request):
    """Créer un sujet de forum"""
    title = request.GET.get('title')
    author = request.GET.get('author')

    if not all([title, author]):
        return JsonResponse({'error': 'Titre et auteur requis'}, status=400)

    topic_ref = db.collection('forums').add({'title': title, 'author': author})
    return JsonResponse({'message': 'Sujet créé !', 'id': topic_ref[1].id})

def add_forum_comment(request):
    """Ajouter un commentaire à un forum"""
    topic_id = request.GET.get('topic_id')
    author = request.GET.get('author')
    content = request.GET.get('content')

    if not all([topic_id, author, content]):
        return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)

    db.collection('forums').document(topic_id).collection('comments').add({
        'author': author,
        'content': content
    })

    return JsonResponse({'message': 'Commentaire ajouté !'})


def view_bulletins(request):
    """Afficher la page de génération des bulletins"""
    return render(request, 'bulletins.html')

def form_add_class(request):
    """Affiche le formulaire pour ajouter une classe"""
    return render(request, 'add_class.html')

def form_add_note(request):
    """Affiche le formulaire pour ajouter une note"""
    return render(request, 'add_note.html')

def form_add_schedule(request):
    """Affiche le formulaire pour ajouter un emploi du temps"""
    return render(request, 'add_schedule.html')

def register(request):
    """Affiche le formulaire d'inscription et gère l'enregistrement"""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        role = request.POST.get("role")  # Admin, Enseignant, Élève, Parent

        if not email or not password or not role:
            return JsonResponse({"error": "Tous les champs sont requis"}, status=400)

        try:
            user = auth.create_user(email=email, password=password)
            # Assigner un rôle à l'utilisateur dans Firestore
            db = firebase_admin.firestore.client()
            db.collection("users").document(user.uid).set({"role": role, "email": email})
            return redirect("login")
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return render(request, "register.html")


def login(request):
    """Affiche le formulaire de connexion"""
    return render(request, "login.html")


def authenticate_user(request):
    """Gère la connexion utilisateur"""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        if not email or not password:
            return JsonResponse({"error": "Email et mot de passe requis"}, status=400)

        try:
            user = auth.get_user_by_email(email)
            return JsonResponse({"message": "Connexion réussie", "user_id": user.uid})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return redirect("login")


def logout(request):
    """Déconnecte l'utilisateur"""
    response = redirect("login")
    response.delete_cookie("session")
    return response

def get_user_role(uid):
    """ Récupère le rôle d'un utilisateur à partir de Firestore """
    user_doc = db.collection("users").document(uid).get()
    if user_doc.exists:
        return user_doc.to_dict().get("role")
    return None

def role_required(allowed_roles=[]):
    """ Décorateur pour restreindre l’accès selon le rôle """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            uid = request.session.get("user_id")  # Vérifier si l'utilisateur est connecté
            if not uid:
                return redirect("login")

            role = get_user_role(uid)
            if role not in allowed_roles:
                return redirect("dashboard")  # Redirection si rôle interdit

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

@role_required(["Admin"])
def add_class(request):
    """ Ajoute une classe (réservé aux Admins) """
    if request.method == "POST":
        name = request.POST.get("name")
        school_id = request.POST.get("school_id")

        if not name or not school_id:
            return JsonResponse({"error": "Nom et ID école requis"}, status=400)

        db.collection("classes").add({"name": name, "school_id": school_id})
        return redirect("view_classes")

    return render(request, "add_class.html")


@role_required(["Admin", "Enseignant"])
def add_note(request):
    """ Ajoute une note (réservé aux Admins et Enseignants) """
    if request.method == "POST":
        eleve_id = request.POST.get("eleve_id")
        matiere = request.POST.get("matiere")
        note = request.POST.get("note")

        if not eleve_id or not matiere or not note:
            return JsonResponse({"error": "Tous les champs sont requis"}, status=400)

        db.collection("notes").add({"eleve_id": eleve_id, "matiere": matiere, "note": float(note)})
        return redirect("view_notes")

    return render(request, "add_note.html")


@role_required(["Admin", "Enseignant"])
def add_schedule(request):
    """ Ajoute un emploi du temps (réservé aux Admins et Enseignants) """
    if request.method == "POST":
        class_id = request.POST.get("class_id")
        day = request.POST.get("day")
        time = request.POST.get("time")
        subject = request.POST.get("subject")

        if not class_id or not day or not time or not subject:
            return JsonResponse({"error": "Tous les champs sont requis"}, status=400)

        db.collection("schedules").add({
            "class_id": class_id,
            "day": day,
            "time": time,
            "subject": subject
        })
        return redirect("view_schedules")

    return render(request, "add_schedule.html")


@role_required(["Élève", "Parent"])
def view_notes(request):
    """ Affiche les notes (accessibles aux Élèves et Parents) """
    uid = request.session.get("user_id")
    if not uid:
        return redirect("login")

    notes = [doc.to_dict() for doc in db.collection("notes").where("eleve_id", "==", uid).stream()]
    return render(request, "notes.html", {"notes": notes})
