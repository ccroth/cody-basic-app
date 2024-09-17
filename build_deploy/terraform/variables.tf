variable "subscription_id" {
    description = "The subscription ID of the active Azure subscription."
}

variable "serviceprincipal_id" {
    description = "The application ID of the service principal."
}

variable "serviceprincipal_key" {
    description = "The value of the client secret for the service principal."
}

variable "tenant_id" {
    description = "The tenant ID."
}

variable "location" {
    default = "westus2"
}

variable "kubernetes_version" {
    default = "1.29.2"
}

variable "ssh_key" {
    description = "SSH key for the Linux profile."
}