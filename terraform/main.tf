terraform {
  backend "s3" {
    bucket = "personal-agents-terraform-state"
    key    = "personal-agents/dev/terraform.tfstate"
    region = "us-east-1"
  }
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  required_version = ">= 1.2.0"
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "PersonalAgents"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
