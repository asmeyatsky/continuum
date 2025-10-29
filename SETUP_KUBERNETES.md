# Kubernetes Deployment Guide

Complete instructions for deploying Continuum to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster 1.20+ (EKS, GKE, AKS, or local kind/minikube)
- kubectl CLI 1.20+ configured
- helm 3.0+ (optional, for advanced deployments)
- 4 CPU cores, 8GB RAM minimum
- PersistentVolume provisioner (local or cloud)

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│ Kubernetes Cluster (continuum namespace)        │
├─────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────┐ │
│ │ Continuum API Deployment (3 replicas)       │ │
│ │ ├─ Service: LoadBalancer/ClusterIP          │ │
│ │ ├─ ConfigMap: Environment variables          │ │
│ │ ├─ Secret: Database credentials              │ │
│ │ ├─ HPA: Scale 3-10 replicas on metrics      │ │
│ │ └─ PDB: Min 2 available replicas             │ │
│ └─────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────┐ │
│ │ PostgreSQL StatefulSet                      │ │
│ │ ├─ Service: ClusterIP                       │ │
│ │ ├─ PersistentVolume: 10Gi                   │ │
│ │ └─ ConfigMap: Init scripts                   │ │
│ └─────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────┐ │
│ │ Redis Cache Deployment                     │ │
│ │ ├─ Service: ClusterIP                       │ │
│ │ └─ PersistentVolume: 5Gi                    │ │
│ └─────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────┐ │
│ │ Jaeger Tracing Deployment                   │ │
│ │ ├─ Service: ClusterIP + Ingress              │ │
│ │ └─ Ports: UDP (6831), HTTP (16686)          │ │
│ └─────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

## Quick Deployment

### 1. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml

# Verify
kubectl get ns continuum
```

### 2. Deploy Database & Cache

```bash
# PostgreSQL
kubectl apply -f k8s/postgres.yaml

# Wait for PostgreSQL
kubectl wait --for=condition=ready pod -l app=postgres -n continuum --timeout=300s

# Redis
kubectl apply -f k8s/redis.yaml

# Wait for Redis
kubectl wait --for=condition=ready pod -l app=redis -n continuum --timeout=300s
```

### 3. Deploy Supporting Services

```bash
# Tracing
kubectl apply -f k8s/jaeger.yaml

# Wait for Jaeger
kubectl wait --for=condition=ready pod -l app=jaeger -n continuum --timeout=300s
```

### 4. Deploy Configuration

```bash
kubectl apply -f k8s/configmap.yaml
```

### 5. Deploy Application

```bash
kubectl apply -f k8s/deployment.yaml

# Wait for replicas to be ready
kubectl rollout status deployment/continuum -n continuum --timeout=300s
```

## Verification

```bash
# Check all resources
kubectl get all -n continuum

# Check pod status
kubectl get pods -n continuum

# Check services
kubectl get svc -n continuum

# Check persistent volumes
kubectl get pv,pvc -n continuum

# View pod logs
kubectl logs -f deployment/continuum -n continuum

# Check pod events
kubectl describe pod <pod-name> -n continuum
```

## Access Services

### Port Forwarding (Development)

```bash
# API
kubectl port-forward svc/continuum 8000:8000 -n continuum

# Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n continuum

# Grafana
kubectl port-forward svc/grafana 3000:3000 -n continuum

# Jaeger
kubectl port-forward svc/jaeger 16686:16686 -n continuum
```

### LoadBalancer (Production)

```bash
# Get external IP
kubectl get svc continuum -n continuum

# Access API
curl http://<EXTERNAL-IP>:8000/health
```

## Scaling

### Manual Scaling

```bash
# Scale to specific number of replicas
kubectl scale deployment continuum --replicas=5 -n continuum

# Verify
kubectl get deployment continuum -n continuum
```

### Horizontal Pod Autoscaler

The deployment includes an HPA that automatically scales based on metrics:

```bash
# View HPA status
kubectl get hpa -n continuum

# Monitor scaling events
kubectl describe hpa continuum -n continuum

# Manual HPA adjustment (if needed)
kubectl patch hpa continuum -n continuum -p '{"spec":{"maxReplicas":20}}'
```

## Rolling Updates & Deployments

### Update Application Image

```bash
# Update image (if using external registry)
kubectl set image deployment/continuum continuum=your-registry/continuum:v1.1.0 -n continuum

# Watch rollout
kubectl rollout status deployment/continuum -n continuum

# Check rollout history
kubectl rollout history deployment/continuum -n continuum

# Rollback if needed
kubectl rollout undo deployment/continuum -n continuum
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap continuum-config -n continuum

# Rollout pods to apply changes
kubectl rollout restart deployment/continuum -n continuum
```

## Monitoring & Observability

### Prometheus Integration

```bash
# Port forward Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n continuum

# Query metrics
curl 'http://localhost:9090/api/v1/query?query=up'

# Example queries
# Request rate: rate(http_requests_total[5m])
# Error rate: rate(http_requests_total{status=~"5.."}[5m])
# Response time: histogram_quantile(0.95, http_request_duration_seconds)
```

### Jaeger Tracing

```bash
# Port forward Jaeger UI
kubectl port-forward svc/jaeger 16686:16686 -n continuum

# Access at http://localhost:16686
# Select continuum service from dropdown
# View distributed traces
```

### Logs

```bash
# View application logs
kubectl logs deployment/continuum -n continuum

# Stream logs
kubectl logs -f deployment/continuum -n continuum

# View logs from previous crashed container
kubectl logs <pod-name> -n continuum --previous

# View logs with timestamps
kubectl logs deployment/continuum -n continuum --timestamps

# View all pods' logs
kubectl logs -l app=continuum -n continuum --all-containers
```

## Database Management

### Access PostgreSQL

```bash
# Connect to PostgreSQL pod
kubectl exec -it <postgres-pod> -n continuum -- psql -U continuum_user -d continuum

# Or use port forward
kubectl port-forward svc/postgres 5432:5432 -n continuum
psql postgresql://continuum_user@localhost:5432/continuum
```

### Database Backup

```bash
# Create backup
kubectl exec <postgres-pod> -n continuum -- pg_dump -U continuum_user continuum > backup.sql

# Restore backup
kubectl exec -i <postgres-pod> -n continuum -- psql -U continuum_user continuum < backup.sql
```

## Troubleshooting

### Pod Pending

```bash
# Check events
kubectl describe pod <pod-name> -n continuum

# Check resource availability
kubectl top nodes
kubectl top pods -n continuum

# Check PVC status
kubectl get pvc -n continuum

# Increase available resources or delete unused PVCs
```

### Pod Crashing

```bash
# View logs
kubectl logs <pod-name> -n continuum

# Check previous logs
kubectl logs <pod-name> -n continuum --previous

# Check events
kubectl describe pod <pod-name> -n continuum

# Check resource limits
kubectl get pod <pod-name> -o yaml -n continuum | grep -A 5 resources
```

### Connection Issues

```bash
# Test connectivity between pods
kubectl exec <pod1> -n continuum -- ping <pod2>

# Test service DNS
kubectl exec <pod> -n continuum -- nslookup postgres

# Test database connection
kubectl exec <continuum-pod> -n continuum -- psql postgresql://continuum_user@postgres:5432/continuum -c "SELECT 1"
```

### Certificate Issues (TLS/Ingress)

```bash
# Check certificate
kubectl get certificates -n continuum

# Describe certificate
kubectl describe certificate <cert-name> -n continuum

# Check ingress
kubectl get ingress -n continuum
kubectl describe ingress <ingress-name> -n continuum
```

## Production Considerations

### RBAC & Security

```bash
# View service account
kubectl get sa -n continuum

# View role bindings
kubectl get rolebindings -n continuum

# Add network policies (optional)
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: continuum-network-policy
  namespace: continuum
spec:
  podSelector:
    matchLabels:
      app: continuum
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
      - namespaceSelector:
          matchLabels:
            name: continuum
      ports:
      - protocol: TCP
        port: 8000
  egress:
    - to:
      - namespaceSelector:
          matchLabels:
            name: continuum
EOF
```

### Resource Quotas

```bash
# Set namespace resource quotas
kubectl apply -f - <<EOF
apiVersion: v1
kind: ResourceQuota
metadata:
  name: continuum-quota
  namespace: continuum
spec:
  hard:
    requests.cpu: "10"
    requests.memory: "20Gi"
    limits.cpu: "20"
    limits.memory: "40Gi"
EOF
```

### Pod Disruption Budgets

Already configured in deployment, but can be customized:

```bash
# View PDB
kubectl get pdb -n continuum

# Modify if needed
kubectl patch pdb continuum -n continuum -p '{"spec":{"minAvailable":3}}'
```

## Backup & Disaster Recovery

### Backup Procedure

```bash
# Backup etcd (cluster state)
ETCDCTL_API=3 etcdctl --endpoints=<control-plane>:2379 snapshot save etcd-backup.db

# Backup application data
kubectl exec <postgres-pod> -n continuum -- pg_dump -U continuum_user continuum > db-backup.sql

# Backup PVC volumes (cloud-specific)
# AWS: aws ec2 create-snapshot --volume-id <vol-id>
# Azure: az snapshot create --name snap --resource-group rg
# GCP: gcloud compute disks snapshot <disk-name>
```

### Restore Procedure

```bash
# Restore database
kubectl cp db-backup.sql <postgres-pod>:/tmp/ -n continuum
kubectl exec <postgres-pod> -n continuum -- psql -U continuum_user continuum < /tmp/db-backup.sql

# Restart application pods to reconnect
kubectl rollout restart deployment/continuum -n continuum
```

## Cost Optimization

### Resource Requests & Limits

Already configured, but can be tuned:

```bash
# View current resources
kubectl get pods -n continuum -o json | jq '.items[].spec.containers[].resources'

# Update if needed
kubectl patch deployment continuum -n continuum -p '{"spec":{"template":{"spec":{"containers":[{"name":"continuum","resources":{"requests":{"cpu":"100m","memory":"128Mi"}}}]}}}}'
```

### Cluster Scaling

```bash
# Auto-scale node pool (cloud-specific)
# AWS: aws autoscaling set-desired-capacity --auto-scaling-group-name <asg> --desired-capacity 5
# Azure: az vmss scale --name <vmss> --resource-group rg --new-capacity 5
# GCP: gcloud compute instance-groups managed set-autoscaling <ig> --scale-based-on-cpu --target-cpu-utilization 0.6
```

## Advanced Topics

### Service Mesh (Optional)

For advanced networking, security, and observability:

```bash
# Install Istio (example)
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
./bin/istioctl install --set profile=demo -y

# Apply sidecar injection
kubectl label namespace continuum istio-injection=enabled

# Restart pods
kubectl rollout restart deployment/continuum -n continuum
```

### Multi-Cluster Deployment

For high availability across regions:

```bash
# Deploy to multiple clusters
for cluster in us-east eu-west ap-southeast; do
  kubectl config use-context $cluster
  kubectl apply -f k8s/
done

# Configure external DNS
# Configure service mesh for cross-cluster communication
```

## Next Steps

1. Set up ingress controller (nginx, traefik, etc.)
2. Configure TLS certificates (cert-manager)
3. Set up log aggregation (ELK, Loki, etc.)
4. Implement service mesh (Istio, Linkerd)
5. Configure backup automation
6. Set up monitoring dashboards
7. Implement CI/CD pipeline for auto-deployment
