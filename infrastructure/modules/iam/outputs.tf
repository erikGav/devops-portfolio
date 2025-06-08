output "cluster_role_arn" {
  description = "The ARN of the EKS cluster IAM role"
  value       = aws_iam_role.cluster_role.arn
}

output "cluster_node_group_role_arn" {
  description = "The ARN of the EKS cluster node group IAM role"
  value       = aws_iam_role.cluster_node_group_role.arn
}
