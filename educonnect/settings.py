import os
from pathlib import Path
import firebase_admin
from firebase_admin import credentials, auth
import dj_database_url



DATABASES = {
    'default': dj_database_url.config(default="sqlite:///db.sqlite3")
}

# ✅ Définition du répertoire de base du projet
BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Chemin du fichier de configuration Firebase
FIREBASE_CREDENTIALS_PATH = os.path.join(BASE_DIR, 'core/firebase_config.json')

# ✅ Vérifier que le fichier Firebase JSON existe avant l'initialisation
if os.path.exists(FIREBASE_CREDENTIALS_PATH):
    cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
    if not firebase_admin._apps:  # ✅ Évite d'initialiser Firebase plusieurs fois
        firebase_admin.initialize_app(cred)
else:
    print("⚠️ Le fichier Firebase JSON est introuvable ! Vérifiez qu'il est bien placé dans core/firebase_config.json")

"""
Django settings for educonnect project.
Generated by 'django-admin startproject' using Django 5.1.7.
"""

# ✅ Clé secrète Django (⚠️ Ne pas exposer en production)
SECRET_KEY = 'django-insecure-c&))f@sy0kfwsm4fc^#!-jhro&i21yjte!^%r4#^!a&6+rlcyo'

# ✅ Ne pas activer DEBUG en production
DEBUG = True

ALLOWED_HOSTS = []

# ✅ Applications installées
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'core',  # ✅ Notre application principale
    'tailwind',  # ✅ Intégration de TailwindCSS
    'theme',  # ✅ Thème Tailwind
]

# ✅ Configuration de TailwindCSS
TAILWIND_APP_NAME = "theme"

# ✅ Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'educonnect.urls'

# ✅ Configuration des templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, "templates")],  # ✅ Dossier où stocker les pages HTML
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

WSGI_APPLICATION = 'educonnect.wsgi.application'

# ✅ Configuration de la base de données (SQLite pour Django, Firestore pour les autres données)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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

# ✅ Gestion des fichiers statiques
STATIC_URL = 'static/'

# ✅ Configuration par défaut des clés primaires
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
