terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "ap-south-1" # Mumbai - Strategic for Indian Defense
}

# 1. Create a VPC (Virtual Private Cloud) for Red-Black Isolation
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.1.1"

  name = "koshatrack-tier-zero-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["ap-south-1a", "ap-south-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = {
    Environment = "Production"
    Project     = "KoshaTrack-SSA"
  }
}

# 2. Create the EKS Cluster (The "Brain" for your K8s deployment)
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "19.15.3"

  cluster_name    = "koshatrack-prod-cluster"
  cluster_version = "1.32"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  eks_managed_node_groups = {
    nodes = {
      min_size     = 1
      max_size     = 3
      desired_size = 4

      instance_types = ["t3.medium"]
      capacity_type  = "ON_DEMAND"
    }
  }
}
