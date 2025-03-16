import json
import os
from pathlib import Path
import dj_database_url
import firebase_admin
from firebase_admin import credentials, auth


# ✅ Définition du répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent


# ✅ Gestion de la clé secrète Django
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-CHANGE-ME")  # 🔒 Remplace en prod


# ✅ Gestion du mode DEBUG
DEBUG = os.getenv("DJANGO_DEBUG", "False").lower() == "true"  # 🔧 Désactivé par défaut en prod


# ✅ Définition des hôtes autorisés
ALLOWED_HOSTS = os.getenv("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# ✅ Configuration de Firebase
firebase_config_json = os.getenv("FIREBASE_CREDENTIALS")

if firebase_config_json:
    firebase_config = json.loads(firebase_config_json)
    if not firebase_admin._apps:  # ⚡ Évite les erreurs d'initialisation multiple
        cred = credentials.Certificate(firebase_config)
        firebase_admin.initialize_app(cred)
else:
    print("⚠️ Firebase credentials non trouvées ! Ajoutez-les en variable d'environnement.")


# ✅ Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # 🔥 API Django Rest Framework
    'core',  # 📌 Notre application principale
    'tailwind',  # 🎨 Intégration de TailwindCSS
    'theme',  # 🎨 Thème Tailwind
    'whitenoise.runserver_nostatic',  # 📦 Gestion des fichiers statiques pour Render
]


# ✅ Configuration de TailwindCSS
TAILWIND_APP_NAME = "theme"


# ✅ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 📦 Gestion des fichiers statiques optimisée
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ✅ URL principale
ROOT_URLCONF = 'educonnect.urls'


# ✅ Configuration des templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],  # 📌 Dossier où stocker les pages HTML
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# ✅ WSGI Application
WSGI_APPLICATION = 'educonnect.wsgi.application'


# ✅ Configuration de la base de données (SQLite en local, PostgreSQL en production)
DATABASES = {
    'default': dj_database_url.config(
        default="sqlite:///db.sqlite3", 
        conn_max_age=600, 
        ssl_require=False
    )
}


# ✅ Validation des mots de passe
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ✅ Configuration internationale
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# ✅ Gestion des fichiers statiques (Render & Django)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # 📌 Stockage des fichiers pour Render
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ✅ Configuration par défaut des clés primaires
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
