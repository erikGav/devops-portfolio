variable "region" {
  description = "AWS region for the resources"
  type        = string
}

variable "naming_prefix" {
  description = "Prefix for naming resources"
  type        = string
}

variable "access_entry_user" {
  description = "IAM user for access entry"
  type        = string
}

variable "default_tags" {
  description = "Tags for the resources"
  type        = map(string)
}

variable "vpc_config" {
  description = "VPC configuration"
  type = object({
    cidr_block         = string
    public_subnet      = string
    private_subnets    = list(string)
    availability_zones = list(string)
  })
}

variable "eks_config" {
  description = "EKS cluster configuration including scaling, updates, and addons"
  type = object({
    scaling_config = object({
      desired_size = number
      max_size     = number
      min_size     = number
    })
    update_config = object({
      max_unavailable = number
    })
    addons = map(object({
      version = string
    }))
  })
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
