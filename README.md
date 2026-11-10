# CS-CAS: Cruise Ship Cabin Allocation System

Django + django-ninja API backed by PostgreSQL, Redis and S3-compatible object storage.

## Local development

Requirements: Python 3.12 (the version in `.python-version`) and Docker with Compose.

```bash
cp .env.example .env              # then fill in the values
docker compose up -d              # PostgreSQL and Redis
python -m venv venv
venv/bin/pip install -r requirements.txt -r requirements-dev.txt
venv/bin/python manage.py migrate
venv/bin/python manage.py pgtrigger install
venv/bin/python manage.py runserver
```

API docs: http://localhost:8000/api/docs.

Object storage is not part of `compose.yaml` yet, so the ship photo endpoints fail until an S3-compatible service is
configured through the `S3_*` variables in `.env`.

## Dependencies

Dependencies are managed with [pip-tools](https://pip-tools.readthedocs.io/). Edit the `.in` files, never the `.txt`
lockfiles.

- `requirements.in`: runtime dependencies. Compiled to `requirements.txt`.
- `requirements-dev.in`: development tools. Compiled to `requirements-dev.txt`, constrained by `requirements.txt`.

```bash
# Upgrade everything to the newest compatible versions
venv/bin/pip-compile --strip-extras --upgrade requirements.in
venv/bin/pip-compile --strip-extras --upgrade requirements-dev.in
# Make the virtualenv match the lockfiles exactly
venv/bin/pip-sync requirements.txt requirements-dev.txt
```

## Git

Run Git from inside WSL. Git for Windows reading this repository through `\\wsl.localhost` reports false changes to
file modes and line endings. Line endings are normalised to LF by `.gitattributes`.
