data "aws_iam_user" "access_entry_user" {
  user_name = var.access_entry_user
}

resource "aws_eks_cluster" "cluster" {
  name = "${var.naming_prefix}-cluster"

  access_config {
    authentication_mode = "API"
  }

  role_arn = var.cluster_role_arn
  version  = "1.33"

  vpc_config {
    subnet_ids = var.private_subnet_ids
  }

  upgrade_policy {
    support_type = "EXTENDED"
  }
}

resource "aws_eks_addon" "cluster_addons" {
  for_each = var.eks_config.addons

  cluster_name  = aws_eks_cluster.cluster.name
  addon_name    = each.key
  addon_version = each.value.version

  service_account_role_arn = each.key == "aws-ebs-csi-driver" ? var.ebs_csi_driver_role_arn : null

  resolve_conflicts_on_create = "OVERWRITE"
  resolve_conflicts_on_update = "OVERWRITE"

}

resource "aws_eks_access_entry" "erik" {
  cluster_name  = aws_eks_cluster.cluster.name
  principal_arn = data.aws_iam_user.access_entry_user.arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "erik_admin" {
  cluster_name  = aws_eks_cluster.cluster.name
  principal_arn = aws_eks_access_entry.erik.principal_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }
}

resource "aws_eks_node_group" "cluster_node_group" {
  cluster_name    = aws_eks_cluster.cluster.name
  node_group_name = "${var.naming_prefix}-cluster-node-group"
  node_role_arn   = var.cluster_node_group_role_arn
  subnet_ids      = var.private_subnet_ids

  instance_types = ["t3a.medium"]

  scaling_config {
    desired_size = var.eks_config.scaling_config.desired_size
    max_size     = var.eks_config.scaling_config.max_size
    min_size     = var.eks_config.scaling_config.min_size
  }

  update_config {
    max_unavailable = var.eks_config.update_config.max_unavailable
  }
}
