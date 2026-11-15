# SenAlert sur Kubernetes

Correspondance avec docker-compose.yml :

| Docker Compose        | Kubernetes                                   |
|-----------------------|----------------------------------------------|
| `db-service` + volume | StatefulSet `postgres` + PVC + Service       |
| `backend-service`     | Deployment `backend` + Service (port 8000)   |
| `frontend-service`    | Deployment `frontend` (2 réplicas) + NodePort 30080 |
| `pgadmin-service`     | Deployment `pgadmin` + NodePort 30081        |
| `environment:`        | ConfigMap + Secret                           |
| `depends_on: healthy` | initContainer `wait-for-db` + probes         |

## Déploiement (Docker Desktop avec Kubernetes activé)

```powershell
kubectl config use-context docker-desktop
docker compose build                 # crée senalert/backend:latest et senalert/frontend:latest
kubectl apply -f k8s/
kubectl get pods -n senalert -w
```

Application : http://localhost:30080 — admin : http://localhost:30080/admin
pgAdmin : http://localhost:30081

Si le NodePort ne répond pas : `kubectl port-forward -n senalert svc/frontend-service 8080:80`
puis http://localhost:8080.

## Commandes utiles

```powershell
kubectl get all -n senalert
kubectl logs -n senalert deploy/backend
kubectl describe pod -n senalert <nom-du-pod>
kubectl scale deploy/frontend -n senalert --replicas=3
kubectl rollout restart deploy/frontend -n senalert
kubectl delete -f k8s/               # tout supprimer
```
