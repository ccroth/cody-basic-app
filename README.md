# Cody's Basic App

This is a simple web app designed to add, view, update, and delete **basketball players**. It is a Flask app using Gunicorn as its WSGI server. This app was built to meet the requirements of the LA Clippers Technical Assessment for DevOps Engineer. The acronym `cba`, which appears often, is short for `cody-basic-app`.

## Navigation
- [A. Design and Architecture](#A)
- [B. Deploy Locally](#B)
- [C. Deploy to Kubernetes](#C)
- [D. Using the App](#D)

<a id="A"></a>
## A. Design and Architecture

The app consists of 3 basic layers:
- frontend
- backend
- database

The combination of Flask and Gunicorn handle the frontend and backened, which is packaged together as a container that I refer to as the `cba-app`. Refer to the `app/` directory for this stuff; in particular, the `Dockerfile` to launch the container. The database layer has its own separate `Dockerfile` and container which hosts a MySQL instance: refer to the `mysql/` directory. I refer to the database container as `cba-mysql`. <br>

The `cba-app` backend communicates with the database via port `3306`. The `cba-app` frontend web service is available over port `8080` locally. The database uses a volume to persist data between being brought up and down.<br><br>

<a id="B"></a>
## B. Deploy Locally

### Prerequisites
- [Docker](https://docs.docker.com/engine/install/) installed and running

The app can be deployed locally via the `docker-compose.yaml` file. Before anything make sure to replace the placeholder values in this file for the following environment variables:
```yaml
      environment:
        . . .
        - db_pass=<password_here>
        . . .
        - secret_key=<secret_key_here>
    cba-mysql:
    . . .
      environment:
        - MYSQL_ROOT_PASSWORD=<password_here>
```
The values for `db_pass` and `MYSQL_ROOT_PASSWORD` must be identical. The value for `secret_key` can be any string - I recommend using a GUID. For *local development* you can use a tool like https://guidgenerator.com/ to generate one (Flask needs a secret key set for securing sessions). <br>

Then, build the images via:
```bash
docker compose build
```
Run the containers with:
```bash
docker compose up
```
The app will be available at `http://127.0.0.1:8080/`. <br><br>

<a id="C"></a>
## C. Deploy to Kubernetes

***Note:** For the sake of this assignment, the procedure below is written assuming the cluster is a *local minikube cluster*. However the same basic steps work for deploying to any k8s cluster, just make sure `kubectl` is communicating with the correct one.* <br>

### Prerequisites
- [Docker](https://docs.docker.com/engine/install/) installed and running
- [Minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download) installed and started
- [Helm](https://helm.sh/docs/intro/install/) installed

There is one Helm chart called `cba-chart` which deploys all the necessary resources to k8s for hosting this application. Importantly, review the `values.yaml` file in the `cba-chart/` directory. The following secrets **must be set before deployment**:
```yaml
secrets:
  db_pass: <encoded_pass_here>
  secret_key: <encoded_key_here>
```
Note that k8s expects these values are base64 encoded. A simple way to encode the values is via:
```bash
echo -n '<value_here>' | openssl base64
```
Other noteworthy aspects of the `values.yaml`:
- `replicaCount` determines the number of replicas for the frontend + backend deployment, thus allowing scaling of the app
- `appURL` sets the URL for which the app will be accessed (when using the ingress)
- I wouldn't recommend modifying the other values unless you had good reason too (though yes you can technically change the container ports, volume name, volume storage, etc.)

After setting `values.yaml`, install the chart:
```bash
cd build_deploy/
helm upgrade --install cba ./cba-chart
```
Once the release is installed, you can **access the service** using one of the two following methods. <br>

### Method 1: Using minikube service
Simply run the command:
```bash
minikube service cba-app-service
```
Minikube will launch the application in a new browser page automatically. Note the service name will be different if you changed `appName` in `values.yaml`. <br><br>

### Method 2: Using the ingress (*requires root access*)<br>
(a) Enable the nginx ingress controller:
```bash
minikube addons enable ingress 
```
(b) Ensure the ingress has an IP set (by default this application's ingress is named `cba-ingress`):
```bash
kubectl get ingress
```
(c) Add the ingress `appURL` to `/etc/hosts` (put the line at the end of the file):
```bash
127.0.0.1 <appURL_here>
```
(d) Enable the minikube tunnel:
```bash
minikube tunnel
```
Make sure to enter root/admin password if prompted. The app will be available over `http://<appURL>/` (so `http://cba.ccr.test/` by default). <br><br>

### Cleaning Up
The release can be uninstalled via:
```bash
helm uninstall cba
```
I designed the volume (i.e. the PersistentVolumeClaim object) to persist on uninstall via the `helm.sh/resource-policy` so that the database doesn't lose data. If this ever needs to be removed for some reason, use:
```bash
kubectl delete PersistentVolumeClaims db-volume
```
**Warning:** deleting the volume will cause the database to lose any added data.<br><br>

<a id="D"></a>
## D. Using the App

The app's frontend is relatively simple and straightforward to navigate. Click "Add New Player" to fill in details for an NBA basketball player. The home screen is populated by all players currently in the database. Click on any player's name to see their details, along with buttons to update their details or delete the player altogether. The database will start out empty with no players, but any players you add will persist (unlesss you delete the volume for some reason). 