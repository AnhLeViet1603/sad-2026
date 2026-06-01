import os
from pathlib import Path


def env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return value.lower() in {"1", "true", "yes", "on"}


def configure(globals_dict, service_name, local_app, db_kind="sqlite"):
    base_dir = Path(globals_dict["__file__"]).resolve().parent.parent

    globals_dict.update(
        BASE_DIR=base_dir,
        SECRET_KEY=os.getenv("DJANGO_SECRET_KEY", "dev-secret"),
        JWT_SECRET=os.getenv("JWT_SECRET", "jwt-secret"),
        DEBUG=env_bool("DEBUG", True),
        ALLOWED_HOSTS=os.getenv("ALLOWED_HOSTS", "*").split(","),
        ROOT_URLCONF=f"{service_name}.urls",
        WSGI_APPLICATION=f"{service_name}.wsgi.application",
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        LANGUAGE_CODE="en-us",
        TIME_ZONE="UTC",
        USE_I18N=True,
        USE_TZ=True,
        STATIC_URL="static/",
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "django.contrib.staticfiles",
            "rest_framework",
            "corsheaders",
            local_app,
        ],
        MIDDLEWARE=[
            "corsheaders.middleware.CorsMiddleware",
            "django.middleware.security.SecurityMiddleware",
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.middleware.common.CommonMiddleware",
            "django.middleware.csrf.CsrfViewMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
        ],
        CORS_ALLOW_ALL_ORIGINS=True,
        REST_FRAMEWORK={
            "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
            "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
        },
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            }
        ],
    )

    if db_kind == "postgres":
        database = {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.getenv("POSTGRES_HOST", "localhost"),
            "PORT": os.getenv("POSTGRES_PORT", "5432"),
            "NAME": os.getenv("POSTGRES_DB", "ecom"),
            "USER": os.getenv("POSTGRES_USER", "ecom"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "ecom"),
        }
    elif db_kind == "mysql":
        database = {
            "ENGINE": "django.db.backends.mysql",
            "HOST": os.getenv("MYSQL_HOST", "localhost"),
            "PORT": os.getenv("MYSQL_PORT", "3306"),
            "NAME": os.getenv("MYSQL_DATABASE", "ecom"),
            "USER": os.getenv("MYSQL_USER", "ecom"),
            "PASSWORD": os.getenv("MYSQL_PASSWORD", "ecom"),
        }
    else:
        database = {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": base_dir / "db.sqlite3",
        }

    globals_dict["DATABASES"] = {"default": database}

