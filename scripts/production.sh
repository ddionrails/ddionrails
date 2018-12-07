#!/bin/sh

paver elastic &
./manage.py rqworker --settings=settings.production &
