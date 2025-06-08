variable "naming_prefix" {
  description = "Prefix for naming resources"
  type        = string
}

variable "default_tags" {
  description = "Tags for the resources"
  type        = map(string)
}
