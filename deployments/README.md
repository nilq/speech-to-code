# Deployments

This directory contains Kubernetes deployment templates. Well-suited and tested using Github Actions release workflow.

*Currently assumes a single environment (production only 😎) for simplicity.*

## Getting started

### Using Github Actions


**Priming repository**

Populate the Github repository secrets with the following:

```
AZURE_TENANT_ID = <tenant ID from Azure>
AZURE_SUBSCRIPTION_ID = <subscription ID from Azure>
AZURE_CLIENT_ID = <client ID from Azure>
ACR_LOGIN_SERVER = <Azure Container Registry login server> (from Azure dashboard)
ACR_USERNAME = <Azure Container Registry username> (from Azure dashboard)
ACR_PASSWORD = <Azure Container Registry password> (from Azure dashboard)
```

**Release to deploy**

Create a release from your favourite branch of the repository and release a new version. (Note: for simplicity, credentials have only been given to the `test` tag)

This will automatically build and push the API and worker images to the Azure Container Registry - to the `api` and `worker` repositories respectively. When the images are built and pushed, the workflow will automatically deploy the service on Azure Kubernetes Service.


## Components

### API

#### Deployment

Deploys `speech-to-code` API pods, running and serving the FastAPI backend defined by the `api` package. This deployment pulls from the latest API image built and pushed to the API container registry.

#### Service

Deploys TCP service for API.

#### Ingress

Deploys HTTP application routing ingress, exposing the API root via HTTP.

#### HorizontalPodAutoscaler

Deploys horizontal pod autoscaler to scale the API deployments. Currently configured to scale between 2-4 nodes, as nodes exceed their 70% CPU utilisation threshold.

### Workers

#### Deployment

Deploys processing workers to the high-performance node pool using the processintg worker taint.

#### HorizontalPodAutoscaler

Deploys horizontal pod autoscaler to scale the API deployments. Currently configured to scale between 2-4 nodes, as nodes exceed their 70% CPU utilisation threshold.


## Examine deployed service

You can extract the Kube-config from `terraform` using either Terraform or OpenTofu (belowe `tofu`), using the below trick:

```
$ echo "$(tofu output kube_config)" > ./azurek8s
$ export KUBECONFIG=./azurek8s
```

Then monitor deployments using `kubectl`:

```
kubectl get pods --all-namespaces
```

Glorious.
