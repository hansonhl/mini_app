#!/usr/bin/env bash
read -s -p "Enter database password:" pwd
flask-sqlacodegen \
  "mysql://root:$pwd@127.0.0.1/food_db" \
  --tables $1 \
  --outfile "common/models/$1.py" \
  --flask