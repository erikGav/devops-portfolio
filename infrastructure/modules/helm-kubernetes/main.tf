terraform {
  required_providers {
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "1.19.0"
    }
  }
}

resource "helm_release" "argocd" {
  name       = var.releases.argocd.name
  namespace  = var.releases.argocd.namespace
  chart      = var.releases.argocd.chart
  repository = var.releases.argocd.repository
  version    = var.releases.argocd.version

  create_namespace = true

  values = [
    file("${path.module}/../../helm-values/${var.releases.argocd.name}-values.yaml")
  ]

  wait          = true
  wait_for_jobs = true
  timeout       = 600
}

resource "helm_release" "external_secrets" {
  name       = var.releases.external-secrets.name
  namespace  = var.releases.external-secrets.namespace
  chart      = var.releases.external-secrets.chart
  repository = var.releases.external-secrets.repository
  version    = var.releases.external-secrets.version

  create_namespace = true

  values = [
    templatefile("${path.module}/../../helm-values/${var.releases.external-secrets.name}-values.yaml", {
      external_secrets_role_arn = var.external_secrets_role_arn
    })
  ]

  wait          = true
  wait_for_jobs = true
  timeout       = 600
}

resource "helm_release" "kube_prometheus_stack" {
  name       = var.releases.kube-prometheus-stack.name
  namespace  = var.releases.kube-prometheus-stack.namespace
  chart      = var.releases.kube-prometheus-stack.chart
  repository = var.releases.kube-prometheus-stack.repository
  version    = var.releases.kube-prometheus-stack.version

  create_namespace = true

  values = [
    file("${path.module}/../../helm-values/${var.releases.kube-prometheus-stack.name}-values.yaml")
  ]

  wait          = true
  wait_for_jobs = true
  timeout       = 600
}

resource "kubernetes_namespace_v1" "cert_manager" {
  metadata {
    name = "cert-manager"
  }
}

resource "kubectl_manifest" "cluster_secret_store" {
  yaml_body = yamlencode({
    apiVersion = "external-secrets.io/v1"
    kind       = "ClusterSecretStore"
    metadata = {
      name = "aws-secrets-manager-cluster"
    }
    spec = {
      provider = {
        aws = {
          service = "SecretsManager"
          region  = var.region
          auth = {
            jwt = {
              serviceAccountRef = {
                name      = "external-secrets-sa"
                namespace = "external-secrets"
              }
            }
          }
        }
      }
    }
  })
  depends_on = [helm_release.external_secrets]
}

resource "kubectl_manifest" "gitlab_external_secret" {
  yaml_body = yamlencode({
    apiVersion = "external-secrets.io/v1"
    kind       = "ExternalSecret"
    metadata = {
      name      = "gitlab-credentials"
      namespace = "argocd"
    }
    spec = {
      refreshInterval = "5m"
      secretStoreRef = {
        name = "aws-secrets-manager-cluster"
        kind = "ClusterSecretStore"
      }
      target = {
        name           = "gitlab-secret"
        creationPolicy = "Owner"
        template = {
          metadata = {
            annotations = {
              "managed-by" = "argocd.argoproj.io"
            }
            labels = {
              "argocd.argoproj.io/secret-type" = "repository"
            }
          }
          type = "Opaque"
        }
      }
      data = [
        {
          secretKey = "type"
          remoteRef = {
            key      = "${var.naming_prefix}/gitlab"
            property = "TYPE"
          }
        },
        {
          secretKey = "url"
          remoteRef = {
            key      = "${var.naming_prefix}/gitlab"
            property = "URL"
          }
        },
        {
          secretKey = "project"
          remoteRef = {
            key      = "${var.naming_prefix}/gitlab"
            property = "PROJECT"
          }
        },
        {
          secretKey = "sshPrivateKey"
          remoteRef = {
            key      = "${var.naming_prefix}/gitlab"
            property = "SSH_KEY"
          }
        }
      ]
    }
  })
  depends_on = [
    helm_release.argocd,
    kubectl_manifest.cluster_secret_store
  ]
}

resource "kubectl_manifest" "cert_manager_sa" {
  yaml_body = yamlencode({
    apiVersion = "v1"
    kind       = "ServiceAccount"
    metadata = {
      name      = "cert-manager"
      namespace = kubernetes_namespace_v1.cert_manager.metadata[0].name
      annotations = {
        "eks.amazonaws.com/role-arn" = var.cert_manager_role_arn
      }
      labels = {
        "app"                         = "cert-manager"
        "app.kubernetes.io/component" = "controller"
        "app.kubernetes.io/instance"  = "cert-manager"
        "app.kubernetes.io/name"      = "cert-manager"
      }
    }
    automountServiceAccountToken = true
  })
}

resource "kubectl_manifest" "infra-app-of-apps" {
  yaml_body = yamlencode({
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "Application"
    metadata = {
      name      = "infra-app-of-apps"
      namespace = var.releases.argocd.namespace
    }
    spec = {
      project = "default"
      source = {
        path           = "infra-app"
        repoURL        = "git@gitlab.com:bootcamp1531414/portfolio-gitops.git"
        targetRevision = "HEAD"
      }
      destination = {
        server    = "https://kubernetes.default.svc"
        namespace = var.releases.argocd.namespace
      }
      syncPolicy = {
        automated = {
          prune    = true
          selfHeal = true
        }
        syncOptions = [
          "CreateNamespace=true",
          "ServerSideApply=true"
        ]
      }
    }
  })
  depends_on = [
    helm_release.kube_prometheus_stack,
    kubectl_manifest.gitlab_external_secret,
    kubectl_manifest.cluster_secret_store,
    kubectl_manifest.cert_manager_sa
  ]
}

resource "kubectl_manifest" "chat-app-of-apps" {
  yaml_body = yamlencode({
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "Application"
    metadata = {
      name      = "chat-app-of-apps"
      namespace = var.releases.argocd.namespace
    }
    spec = {
      project = "default"
      source = {
        path           = "chat-app"
        repoURL        = "git@gitlab.com:bootcamp1531414/portfolio-gitops.git"
        targetRevision = "HEAD"
      }
      destination = {
        server    = "https://kubernetes.default.svc"
        namespace = var.releases.argocd.namespace
      }
      syncPolicy = {
        automated = {
          prune    = true
          selfHeal = true
        }
        syncOptions = [
          "CreateNamespace=true",
          "ServerSideApply=true"
        ]
      }
    }
  })
  depends_on = [kubectl_manifest.infra-app-of-apps]
}

resource "kubernetes_storage_class" "gp3" {
  metadata {
    name = "gp3"
    annotations = {
      "storageclass.kubernetes.io/is-default-class" = "true"
    }
  }

  storage_provisioner    = "ebs.csi.aws.com"
  reclaim_policy         = "Delete"
  volume_binding_mode    = "WaitForFirstConsumer"
  allow_volume_expansion = true

  parameters = {
    type      = "gp3"
    fsType    = "ext4"
    encrypted = "true"
  }
}
