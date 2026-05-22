#!/bin/bash
arg="${1:-tests/functional/remote}"

TEST_SERVER=https://staging.lilianamedela.com.ar \
DJANGO_TEST_TOKEN='ooio4903_4uu3u_4rui344u890' \
DJANGO_TEST_ADMIN_USERNAME=admin \
DJANGO_TEST_ADMIN_PASSWORD=pasparafrasia \
DJANGO_TEST_ADMIN_EMAIL=admin@test.com \
pytest $arg
