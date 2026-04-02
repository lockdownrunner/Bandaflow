#!/usr/bin/env bash
# Exit immediately if a command exits with a non-zero status.
set -o errexit

# 1. Combine the pip install command here
pip install -r requirements.txt

# 2. Add any other build steps (like migrations)
python manage.py migrate