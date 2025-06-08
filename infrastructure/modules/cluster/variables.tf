variable "naming_prefix" {
  description = "Prefix for naming resources"
  type        = string
}

variable "default_tags" {
  description = "Tags for the resources"
  type        = map(string)
}

variable "private_subnet_ids" {
  description = "Subnet ID"
  type        = list(string)
}

variable "access_entry_user" {
  description = "IAM user for access entry"
  type        = string
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

variable "cluster_role_arn" {
  description = "The ARN of the EKS cluster IAM role"
  type        = string
}

variable "cluster_node_group_role_arn" {
  description = "The ARN of the EKS cluster node group IAM role"
  type        = string
}

variable "ebs_csi_driver_role_arn" {
  description = "The ARN of the EBS CSI driver IAM role"
  type        = string
}
