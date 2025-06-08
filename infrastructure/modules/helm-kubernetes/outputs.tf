output "argocd_status" {
  description = "Status of ArgoCD helm release"
  value       = helm_release.argocd.status
}

output "external_secrets_status" {
  description = "Status of External Secrets helm release"
  value       = helm_release.external_secrets.status
}
