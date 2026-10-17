import os

DATABASES: dict[str, dict[str, object]] = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "mysite",
        "USER": "postgres",
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": "localhost",
        "PORT": "5432",
    },
}
