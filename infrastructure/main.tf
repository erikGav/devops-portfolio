module "iam" {
  source = "./modules/iam"

  naming_prefix = var.naming_prefix
  default_tags  = var.default_tags
}

module "network" {
  source = "./modules/network"

  naming_prefix = var.naming_prefix
  default_tags  = var.default_tags
  vpc_config    = var.vpc_config
}

module "cluster" {
  source = "./modules/cluster"

  naming_prefix               = var.naming_prefix
  default_tags                = var.default_tags
  access_entry_user           = var.access_entry_user
  eks_config                  = var.eks_config
  private_subnet_ids          = module.network.private_subnet_ids
  cluster_role_arn            = module.iam.cluster_role_arn
  cluster_node_group_role_arn = module.iam.cluster_node_group_role_arn
  ebs_csi_driver_role_arn     = module.oidc.ebs_csi_driver_role_arn

  depends_on = [
    module.iam,
    module.network,
  ]
}

module "oidc" {
  source = "./modules/oidc"

  region                  = var.region
  naming_prefix           = var.naming_prefix
  default_tags            = var.default_tags
  cluster_oidc_issuer_url = module.cluster.cluster_oidc_issuer_url
}

module "helm_kubernetes" {
  source = "./modules/helm-kubernetes"

  region                    = var.region
  naming_prefix             = var.naming_prefix
  releases                  = var.releases
  cluster_name              = module.cluster.cluster_name
  external_secrets_role_arn = module.oidc.external_secrets_role_arn
  cert_manager_role_arn     = module.oidc.cert_manager_role_arn

  depends_on = [
    module.cluster,
    module.oidc,
  ]
}
