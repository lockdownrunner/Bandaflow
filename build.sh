#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Install dependencies
pip install -r requirements.txt

# 2. Collect Static Files (This fixes the "Plain Text" look)
python manage.py collectstatic --noinput

# 3. Run Database Migrations
python manage.py migrate