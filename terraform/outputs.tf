output "cluster_endpoint" {
  description = "Endpoint de la API de Kubernetes"
  value       = module.eks.cluster_endpoint
}

output "cluster_name" {
  description = "Nombre del clúster EKS creado"
  value       = module.eks.cluster_name
}

output "configure_kubectl" {
  description = "Comando para conectar kubectl a este clúster"
  value       = "aws eks --region ${var.aws_region} update-kubeconfig --name ${module.eks.cluster_name}"
}