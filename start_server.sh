#!/bin/bash
gunicorn --env SCRIPT_NAME=/CKS -w 4 --bind 0.0.0.0:8000 'app:flask_app' --log-file record.log --log-level DEBUG --reload
