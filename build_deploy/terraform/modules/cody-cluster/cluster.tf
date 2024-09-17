resource "azurerm_resource_group" "cody-azure" {
    name = "cody-resource_group"
    location = var.location
}

resource "azurerm_container_registry" "cody-azure" {
    name = "ccracr"
    location = azurerm_resource_group.cody-azure.location
    resource_group_name = azurerm_resource_group.cody-azure.name
    sku = "Basic"
}

resource "azurerm_kubernetes_cluster" "cody-azure" {
    name = "cody-cluster"
    location = azurerm_resource_group.cody-azure.location
    resource_group_name = azurerm_resource_group.cody-azure.name
    dns_prefix = "codycluster"
    kubernetes_version = var.kubernetes_version

    default_node_pool {
        name = "default"
        node_count = 1
        vm_size = "Standard_DS2_v2"
        type = "VirtualMachineScaleSets"
        os_disk_size_gb = 50
    }

    service_principal {
        client_id = var.serviceprincipal_id
        client_secret = var.serviceprincipal_key
    }

    linux_profile {
        admin_username = "codyadmin"
        ssh_key {
            key_data = var.ssh_key
        }
    }

    network_profile {
        network_plugin = "kubenet"
        load_balancer_sku = "standard"
    }
}