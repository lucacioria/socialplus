#!/bin/sh
jade DJANGO_GAE/public/html/
jade DJANGO_GAE/pages/
coffee -c DJANGO_GAE/public/js/coffee/
sass --update DJANGO_GAE/public/css/