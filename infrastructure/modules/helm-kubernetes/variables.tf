variable "naming_prefix" {
  description = "Prefix for naming resources"
  type        = string
}

variable "cluster_name" {
  description = "Name of the EKS cluster"
  type        = string
}

variable "external_secrets_role_arn" {
  description = "ARN of the IAM role for External Secrets Operator"
  type        = string
}

variable "cert_manager_role_arn" {
  description = "ARN of the IAM role for cert-manager"
  type        = string
}

variable "releases" {
  description = "Helm releases with their configuration"
  type = map(object({
    name       = string
    namespace  = string
    chart      = string
    repository = string
    version    = string
    values     = optional(string)
  }))
}

variable "region" {
  description = "AWS region for the resources"
  type        = string
}
