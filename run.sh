#!/usr/bin/env bash

#python -m aiohttp.web -H 0.0.0.0 -P ${APP_PORT} app:create_app
gunicorn app:create_app --bind 0.0.0.0:${APP_PORT} --worker-class aiohttp.GunicornWebWorker