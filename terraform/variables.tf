variable "aws_region" {
  description = "Región de AWS donde se creará la infraestructura"
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "Nombre del clúster de Kubernetes"
  type        = string
  default     = "devops-django-cluster"
}

variable "environment" {
  description = "Ambiente de despliegue"
  type        = string
  default     = "production"
}