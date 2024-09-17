# Cody's Basic App

This is a simple web app designed to add, view, update, and delete **basketball players**. It is a Flask app using Gunicorn as its WSGI server. This app was built to meet the requirements of the LA Clippers Technical Assessment for DevOps Engineer. The acronym `cba`, which appears often, is short for `cody-basic-app`.

## Navigation
- [A. Design and Architecture](#A)
- [B. Deploy Locally](#B)
- [C. Deploy to Minikube](#C)
- [D. Deploy to AKS Cluster](#D)
- [E. Using the App](#E)

<a id="A"></a>
## A. Design and Architecture

The app consists of 3 basic layers:
- frontend
- backend
- database

The combination of Flask and Gunicorn handle the frontend and backened, which is packaged together as a container that I refer to as the `cba-app`. Refer to the `app/` directory for this stuff; in particular, the `Dockerfile` to launch the container. The database layer has its own separate `Dockerfile` and container which hosts a MySQL instance: refer to the `mysql/` directory. I refer to the database container as `cba-mysql`. <br>

The `cba-app` backend communicates with the database via port `3306`. The `cba-app` frontend web service is available over port `8080` locally. The database uses a volume to persist data between being brought up and down (recall that container storage is ephemeral by default).<br><br>

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
The app will be available at `http://127.0.0.1:8080/`. <br>

**Warning:** the environment variables set for the `cba-mysql` container are saved in the volume specified in the `docker-compose.yaml` file (i.e. `db_volume` by default). That means if you for some reason want to change variables such as `MYSQL_ROOT_PASSWORD` after deployment, you must either delete the existing volume, or specify a different volume.
<br><br>

<a id="C"></a>
## C. Deploy to Minikube

### Prerequisites
- [Docker](https://docs.docker.com/engine/install/) installed and running
- [Kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- [Minikube](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fbinary+download) installed and started
- [Helm](https://helm.sh/docs/intro/install/) installed

In this section, we use the Helm chart called `cba-chart` which deploys all the necessary resources to Minikube for hosting this application. Importantly, review the `values.yaml` file in the `charts/cba-chart/` directory. The following secrets **must be set before deployment**:
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
- `appURL` sets the URL for which the app will be accessed (when using the ingress - see **Method 2** below)
- I wouldn't recommend modifying the other values unless you had good reason to (although there are times when you might change `volume.name` - see [Cleaning Up](#cleaning-up))

After setting `values.yaml`, install the chart:
```bash
cd build_deploy/
helm upgrade --install cba ./charts/cba-chart
```
Once the chart is installed, you can **access the service** using one of the two following methods. <br>

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
Make sure to enter root/admin password if prompted. The app will be available over `http://<appURL>/` (i.e. `http://cba.ccr.test/` by default). <br><br>

### Cleaning Up
The chart can be uninstalled via:
```bash
helm uninstall cba
```
I designed the volume (i.e. the PersistentVolumeClaim object) to persist on uninstall via the `helm.sh/resource-policy` so that the database doesn't lose data. If this ever needs to be removed for some reason, use (make sure to uninstall the chart *before* running this command):
```bash
kubectl delete PersistentVolumeClaims db-volume
```
**Warning:** deleting the volume will cause the database to lose any added data. Again, recall that the environment variables for the `cba-mysql` deployment will be stored in the volume. Thus, if after deploying, you make any changes to database related values (e.g. `db_pass` or `db_database`) in `values.yaml`, you will need to either delete the existing volume with the above command, or change the `volume.name` value in `values.yaml` to something different (i.e. create a new volume).<br>

Tear down minikube cluster:
```bash
minikube delete --all
```
<br>


<a id="D"></a>
## D. Deploy to AKS Cluster

**Note:** this section contains information specifically for the bonus part of the assessment. <br>

### Prerequisites
- Azure account with an active Azure subscription: [more info](https://azure.microsoft.com/en-us/pricing/purchase-options/azure-account)
- [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli) installed
- [Helm](https://helm.sh/docs/intro/install/) installed
- [Kubectl](https://kubernetes.io/docs/tasks/tools/) installed
- [Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) installed <br>

### Provision the AKS Cluster
We use Terraform to provision a cluster in AKS which our app will use. Review the `terraform/` directory within `build_deploy/`. The `cody-cluster/` Terraform module provisions three resources:
- a resource group called "cody-resource_group"
- an ACR registry called "ccracr"
- an AKS cluster called "cody-cluster"

Before provisioning, we need to do some initial setup and gather the required variables, which will be set in the `terraform/values.tfvars` file. Make sure to put all the values inside the quotes.

First, login to Azure via the CLI:
```bash
az login
```
Follow the prompts to ensure that the **correct subscription and tenant are selected**. Run the following command and record the subscription ID and tenant ID in `values.tfvars`:
```bash
az account list -o table
```
Next, create the service principal `cba-sp` (required for Terraform to provision the cluster):
```bash
az ad sp create-for-rbac --skip-assignment --name cba-sp -o json
```
From this output, use the `appId` to set `serviceprincipal_id` and `password` to set `serviceprincipal_key` in `values.tfvars`.

Grant this service principal the Contributer role (make sure to fill in the values of `appId` and `subscriptionId`):
```bash
az role assignment create \
--assignee <appId> \
--scope "/subscriptions/<subscriptionId>" \
--role Contributor
```
Finally, generate an SSH key to be used for the cluster's Linux profile (substitute the email for your Azure account in the command below):
```bash
ssh-keygen -t rsa -b 4096 -C "<your_email_here>"
```
Use the value of the public key that was generated for `ssh_key` in `values.tfvars`. The `ssh-keygen` output will explicitly state which file the public key was saved to.

Now, we are ready to provision. Run these commands from the `terraform/` directory. Initialize Terraform by running:
```bash
terraform init
```
Use the following command to see what changes Terraform intends to make:
```bash
terraform plan -var-file values.tfvars
```
If everything looks good, provision the resources with:
```bash
terraform apply -var-file values.tfvars
```
**Note:** it can take several minutes to fully provision the cluster. <br><br>

### Deploying to the Cluster
Once the resource group and cluster are active in AKS, we need to configure `kubectl` to connect to our cluster:
```bash
az aks get-credentials --resource-group cody-resource_group --name cody-cluster
```
Build and push the container images to the container registry:
```bash
# for cba-app
cd app/
az acr build --image cba-app:latest --registry ccracr --file Dockerfile .
# for cba-mysql
cd mysql/
az acr build --image cba-mysql:latest --registry ccracr --file Dockerfile .
```
Deploy NGINX ingress controller to cluster:
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm install ingress-nginx ingress-nginx/ingress-nginx \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/azure-load-balancer-health-probe-request-path"=/healthz \
  --set controller.service.externalTrafficPolicy=Local
```
Use this command to watch for when the `EXTERNAL-IP` becomes available (can take a few minutes):
```bash
kubectl get service --namespace default ingress-nginx-controller --output wide --watch
```
Once it is, we are ready to deploy our application. Review `values.yaml` in the `cba-chart-azure/` chart and ensure to set the required secrets:
```yaml
secrets:
  db_pass: <encoded_pass_here>
  secret_key: <encoded_key_here>
```
Refer to section **C.** above for how to base64 encode the secrets. Note the image repository values now are defaulted to use the ACR registry. <br>

Deploy the chart with:
```bash
cd build_deploy/
helm upgrade --install cba ./charts/cba-chart-azure
```
Once deployed, put the `EXTERNAL-IP` of the ingress controller into a web browser to access the application. Note that the database container sometimes take a minute or two to fully come up. <br><br>

### Cleaning Up
The chart can be uninstalled via:
```bash
helm uninstall cba
```
The ingress controller can be deleted via:
```bash
kubectl delete Deployment ingress-nginx-controller
```
The volume claim can be deleted via:
```bash
kubectl delete PersistentVolumeClaims db-volume
```
The same **warning** from section **C.** above applies here. <br>

The cluster and resource group can be deprovisioned by running:
```bash
cd build_deploy/terraform/
terraform apply -destroy -var-file values.tfvars
```
<br>

<a id="E"></a>
## E. Using the App

The app's frontend is relatively simple and straightforward to navigate. Click "Add New Player" to fill in details for an NBA basketball player. The home screen is populated by all players currently in the database. Click on any player's name to see their details, along with buttons to update their details or delete the player altogether. The database will start out empty with no players, but any players you add will persist (unlesss you delete the volume for some reason).


