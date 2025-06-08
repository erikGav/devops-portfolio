output "oidc_provider_arn" {
  description = "The ARN of the OIDC provider"
  value       = aws_iam_openid_connect_provider.eks_oidc.arn
}

output "ebs_csi_driver_role_arn" {
  description = "The ARN of the EBS CSI driver IAM role"
  value       = aws_iam_role.ebs_csi_driver_role.arn
}

output "external_secrets_role_arn" {
  description = "ARN of the External Secrets Operator IAM role"
  value       = aws_iam_role.external_secrets_role.arn
}

output "cert_manager_role_arn" {
  description = "ARN of the cert-manager IAM role"
  value       = aws_iam_role.cert_manager_role.arn

}
