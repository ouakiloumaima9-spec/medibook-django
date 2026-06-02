#!/bin/sh
set -e

echo "MediBook : démarrage..."

if [ "${DB_ENGINE}" != "django.db.backends.sqlite3" ]; then
  echo "Attente de la base de données ${DB_HOST:-db}:${DB_PORT:-3306}..."

  python - <<'PY'
import os
import socket
import time
import sys

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "3306"))

for attempt in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            print("Base de données prête.")
            sys.exit(0)
    except OSError:
        print("Base de données non prête, nouvel essai dans 2s...")
        time.sleep(2)

print("Erreur : base de données non accessible après attente.")
sys.exit(1)
PY
fi

echo "Application des migrations..."
python manage.py migrate --noinput

if [ "${SEED_DATA:-true}" = "true" ]; then
  echo "Initialisation des données de démonstration..."
  python manage.py seed_data || true
fi

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "Lancement du serveur..."
exec "$@"