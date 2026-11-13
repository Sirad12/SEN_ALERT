# SenAlert

Plateforme de signalement des rues, canaux et caniveaux bouchés : carte des signalements, formulaire de signalement, suivi par identifiant et espace administrateur.

- **Site (GitLab Pages, données de démonstration) :** voir *Deploy > Pages* dans le projet GitLab
- **Compte administrateur de démonstration :** `admin` / `demo123`

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

### Runner pour `deploy-compose`

Ce job déploie la stack complète sur une machine à vous : il faut y installer un runner avec le tag `senalert-deploy`.

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

3. Dans le pipeline de `main`, cliquer sur ▶ du job `deploy-compose`. L'application est ensuite servie sur http://localhost:3000 de cette machine.
