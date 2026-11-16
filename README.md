# SenAlert

Plateforme de signalement des rues, canaux et caniveaux bouchés : carte des signalements, formulaire de signalement, suivi par identifiant et espace administrateur.

- **Site (GitLab Pages, données de démonstration) :** voir *Deploy > Pages* dans le projet GitLab
- **Espace administrateur :** pas de lien public, on y accède en tapant `/admin` dans l'URL
  (compte de démonstration : `admin` / `demo123`)

L'application peut être lancée de deux façons : avec **Docker Compose** (simple, en local) ou sur **Kubernetes** (minikube).

## Structure (mono-repo)

```
.
├── backend/            API FastAPI + SQLAlchemy (PostgreSQL)
│   ├── app/            main.py, models.py, schemas.py, crud.py, seed.py
│   ├── tests/          tests pytest (SQLite)
│   └── Dockerfile
├── frontend/           Application Angular
│   ├── src/
│   ├── nginx.conf      sert le site et redirige /api vers le backend
│   └── Dockerfile      build Node puis image nginx
├── k8s/                manifestes Kubernetes (voir plus bas)
├── docker-compose.yml  Postgres + pgAdmin + backend + frontend
└── .gitlab-ci.yml      pipeline CI/CD GitLab
```

## Lancer avec Docker Compose

```bash
docker compose up -d --build
```

| Service  | URL                                 |
|----------|-------------------------------------|
| Frontend | http://localhost:3000               |
| API      | http://localhost:8001/docs (Swagger) |
| pgAdmin  | http://localhost:8081 (`admin@senalert.sn` / `admin1234`) |

Arrêt : `docker compose down` (ajouter `-v` pour effacer la base).

> Si l'ancienne interface s'affiche après une reconstruction, c'est le cache du navigateur :
> ouvrir en navigation privée ou faire `Ctrl + Shift + R`. Le `nginx.conf` envoie
> `Cache-Control: no-cache` sur `index.html` pour éviter ce problème aux prochains déploiements.

## Déployer sur Kubernetes (minikube)

Le dossier `k8s/` contient les manifestes. Ils reprennent les noms de services de Docker Compose
(`db-service`, `backend-service`), donc le code et les images n'ont pas besoin d'être modifiés.

| Fichier | Contenu |
|---------|---------|
| `00-namespace.yaml` | namespace `senalert` |
| `01-config.yaml`    | ConfigMap (paramètres) et Secret (mots de passe) |
| `10-postgres.yaml`  | PostgreSQL 17 : StatefulSet + volume persistant 1 Gi + Service `db-service` |
| `20-backend.yaml`   | API FastAPI : Deployment (1 réplica) + Service `backend-service` (port 8000) |
| `30-frontend.yaml`  | Frontend nginx : Deployment (2 réplicas) + Service NodePort 30080 |
| `40-pgadmin.yaml`   | pgAdmin (optionnel) : Deployment + Service NodePort 30081 |

Les numéros fixent l'ordre d'application : le namespace et la configuration doivent exister avant le reste.

### Prérequis

Docker Desktop et un cluster minikube démarré :

```bash
minikube start
kubectl get nodes          # le nœud doit être Ready
```

### Déploiement

```bash
# 1. Construire les images
docker compose build

# 2. Les charger dans minikube (il ne voit pas les images locales de Docker)
minikube image load senalert/backend:latest
minikube image load senalert/frontend:latest

# 3. Appliquer les manifestes
kubectl apply -f k8s/

# 4. Attendre que tous les pods soient Running
kubectl get pods -n senalert -w
```

### Accéder à l'application

```bash
kubectl port-forward -n senalert svc/frontend-service 8080:80
```

Puis ouvrir http://localhost:8080 (espace admin : http://localhost:8080/admin).
La fenêtre du terminal doit rester ouverte : `Ctrl + C` coupe le tunnel.
Après un redémarrage de l'ordinateur, relancer `minikube start` puis cette commande.

### Commandes utiles

```bash
kubectl get all -n senalert                          # vue d'ensemble
kubectl logs -n senalert deploy/backend              # journaux du backend
kubectl describe pod -n senalert <nom-du-pod>        # diagnostiquer un pod en erreur
kubectl scale deploy/frontend -n senalert --replicas=3
kubectl rollout restart deploy/frontend -n senalert  # redémarrer sans interruption
kubectl delete -f k8s/                               # tout supprimer
```

### Remarques

- Le backend est volontairement limité à **1 réplica** : le jeton administrateur est conservé en mémoire,
  donc avec plusieurs pods une connexion sur l'un serait refusée par l'autre. Redémarrer le pod du
  backend oblige à se reconnecter à `/admin` (les signalements restent dans la base).
- Les mots de passe du `Secret` sont des valeurs de démonstration. Ne pas les réutiliser en production.
- Le déploiement Kubernetes se fait à la main avec `kubectl` : il n'est pas inclus dans la pipeline GitLab.

## Développement sans Docker

```bash
# Frontend (mode démonstration, données en mémoire)
cd frontend && npm install && npx ng serve         # http://localhost:4200

# Backend
cd backend && python -m venv .venv && .venv/Scripts/pip install -r requirements-dev.txt
.venv/Scripts/python -m pytest                       # tests
```

Le frontend a deux modes, choisis à la compilation (`src/environments/`) :
- **démonstration** (`ng serve`, tests, GitLab Pages) : données en mémoire, aucun backend ;
- **docker** (`ng build --configuration docker`) : appels à l'API via `/api`.

## Pipeline CI/CD GitLab

| Stage  | Job              | Rôle |
|--------|------------------|------|
| test   | `test-backend`   | `pytest` sur l'API |
| test   | `test-frontend`  | tests unitaires Angular (vitest) |
| build  | `build-frontend` | `ng build` pour GitLab Pages |
| docker | `docker-images`  | build + push des images dans le Container Registry GitLab (`main` uniquement) |
| deploy | `pages`          | publication sur GitLab Pages (`main` uniquement) |
| deploy | `deploy-compose` | `docker compose up` sur un runner perso, **manuel** |

Les jobs `test`, `build`, `docker` et `pages` tournent sur les runners partagés de GitLab.com.

### Runner pour `deploy-compose` (optionnel)

Ce job déploie la stack Docker Compose sur une machine à vous : il faut y installer un runner avec le tag `senalert-deploy`.
Il n'est pas nécessaire pour le déploiement Kubernetes.

1. GitLab : *Settings > CI/CD > Runners > New project runner*, tag `senalert-deploy`, puis copier le jeton `glrt-...`.
2. Sur la machine (Docker Desktop lancé) :

```bash
docker run -d --name gitlab-runner --restart always \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v gitlab-runner-config:/etc/gitlab-runner \
  gitlab/gitlab-runner:latest

docker exec -it gitlab-runner gitlab-runner register \
  --url https://gitlab.com --token glrt-XXXXXXXX \
  --executor docker --docker-image docker:27 \
  --docker-volumes /var/run/docker.sock:/var/run/docker.sock
```

Sous PowerShell, les `\` de fin de ligne ne fonctionnent pas : mettre chaque commande sur une seule ligne.

3. Dans le pipeline de `main`, cliquer sur ▶ du job `deploy-compose`. L'application est ensuite servie sur http://localhost:3000 de cette machine.