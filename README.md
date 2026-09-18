export DJANGO_SETTINGS_MODULE=config.settings.development

config/: configuración global.
organization/: lógica relacionada con organizaciones.
accounts/: autenticación y usuarios.
billing/: pagos y planes.
common/: utilidades compartidas.


condominios/
├── .env
├── .gitignore
├── manage.py
├── requirements.txt
├── README.md
│
├── config/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── apps/
│   ├── organization/
│   │   ├── migrations/
│   │   ├── templates/
│   │   │   └── organization/
│   │   │       ├── organization_list.html
│   │   │       ├── organization_form.html
│   │   │       └── organization_actions.html
│   │   ├── __init__.py
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── models.py
│   │   ├── selectors.py
│   │   ├── services.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── tests/
│   │       ├── test_models.py
│   │       ├── test_services.py
│   │       └── test_views.py
│   │
│   └── accounts/
│       ├── models.py
│       ├── forms.py
│       ├── views.py
│       └── urls.py
│
├── templates/
│   ├── base.html
│   ├── sections/
│   │   ├── head.html
│   │   └── navbar.html
│   └── registration/
│       └── login.html
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
└── media/

#############
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "apps.organization",
    "apps.accounts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES[0]["DIRS"] = [
    BASE_DIR / "templates",
]

WSGI_APPLICATION = "config.wsgi.application"

python manage.py runserver --settings=config.settings.development

En este proyecto no se usa por que no se conecta a la base de datos solo ApiRest
python manage.py migrate --settings=config.settings.development#condominio

#Build imagen dev
    docker build -f Dockerfile.dev -t condominios-dev .
#Levantar entorno dev
    docker compose -f compose.dev.yml up --build -d
#ver logs
    docker compose -f compose.dev.yml logs -f web
#apagar entorno
    compose -f compose.dev.yml down
#Limpiar contenedores e imágenes
    docker system prune -af --volumes
    docker rm -f $(docker ps -aq)

#Build imagen prod
    docker build -f Dockerfile.prod -t myapp-prod .
#Levantar entorno prod
    docker compose -f compose.prod.yml up -d --build
#Ver logs
    docker compose -f compose.prod.yml logs -f web
    docker compose -f compose.prod.yml logs -f nginx
#Apagar entorno
    docker compose -f compose.prod.yml down
#Limpiar recursos
    docker system prune -f    