terraform {
  required_providers {
    azurerm = {
      source = "hashicorp/azurerm"
      version = "4.2.0"
    }
  }
}

provider "azurerm" {
    subscription_id = var.subscription_id
    client_id = var.serviceprincipal_id
    client_secret = var.serviceprincipal_key
    tenant_id = var.tenant_id

    resource_provider_registrations = "none"
    
    features {}
}

module "cody-cluster" {
    source = "./modules/cody-cluster"
    serviceprincipal_id = var.serviceprincipal_id
    serviceprincipal_key = var.serviceprincipal_key
    ssh_key = var.ssh_key
    location = var.location
    kubernetes_version = var.kubernetes_version
}