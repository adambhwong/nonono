terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "default"
  region  = "ap-east-1"
}

resource "aws_dynamodb_table" "basic-dynamodb-table" {
  name           = "ShortenUrl"
  billing_mode   = "PROVISIONED"
  read_capacity  = 1000
  write_capacity = 20
  hash_key       = "ShortenUrl"
  range_key      = "OriginalUrl"

  attribute {
    name = "ShortenUrl"
    type = "S"
  }

  attribute {
    name = "OriginalUrl"
    type = "S"
  }

  ttl {
    attribute_name = "TimeToExist"
    enabled        = false
  }

  global_secondary_index {
    name               = "OriginalUrlIndex"
    hash_key           = "OriginalUrl"
    range_key          = "ShortenUrl"
    write_capacity     = 20
    read_capacity      = 20
    projection_type    = "ALL"
  }
  
  tags = {
    Name        = "shorten-url-table"
    Environment = "production"
  }
}
