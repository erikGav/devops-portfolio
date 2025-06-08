variable "naming_prefix" {
  description = "Prefix for naming resources"
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
