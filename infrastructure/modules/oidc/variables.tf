variable "region" {
  description = "AWS region for the resources"
  type        = string
}

variable "naming_prefix" {
  description = "Prefix for naming resources"
  type        = string
}

variable "default_tags" {
  description = "Tags for the resources"
  type        = map(string)
}


variable "cluster_oidc_issuer_url" {
  description = "Name of the EKS cluster"
  type        = string
}
