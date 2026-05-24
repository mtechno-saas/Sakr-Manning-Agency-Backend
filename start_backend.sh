#!/bin/bash
cd /opt/sakr/Sakr-Manning-Agency-Backend
source venv/bin/activate
exec venv/bin/gunicorn saker.wsgi:application --bind 127.0.0.1:8000 --workers 3
