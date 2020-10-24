#!/bin/bash

echo Hello,Docker.
cd /root
ls -hl
python3 manage.py runserver 0.0.0.0:8000
