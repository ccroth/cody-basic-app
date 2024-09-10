# Cody's Basic App

This is a simple web app designed to add, view, update, and delete basketball players. It is a Flask app using Gunicorn as its WSGI server. This app was built to meet the requirements of the LA Clippers Technical Assessment for DevOps Engineer. The acronym `cba`, which appears often, is short for `cody-basic-app`.

## A. Design and Architecture

The app consists of 3 basic layers:
- frontend
- backend
- database

The combination of Flask and Gunicorn handle the frontend and backened, which is packaged together as a container that I refer to as the `cba-app`. Refer to the `app/` directory for this stuff; in particular, the `Dockerfile` to launch the container. The database layer has its own separate `Dockerfile` and container which hosts a MySQL instance: refer to the `mysql/` directory. I refer to the database container as `cba-mysql`. <br>

The `cba-app` backend communicates with the database via port `3306`. The `cba-app` frontend web service is available over port `8080` locally. The database uses a volume to persist data between being brought up and down.<br>
