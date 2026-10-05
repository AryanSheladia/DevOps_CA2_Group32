# Step 2 — Render deployment

Work started: 5 October 2026.

Repository: https://github.com/AryanSheladia/DevOps_CA2_Group32

## Files prepared

- Root `Dockerfile`: Python 3.12, pinned prediction requirements, saved model pair, one Uvicorn worker, and Render's `PORT` variable.
- Root `.dockerignore`: excludes local environments, secrets, caches, and old training outputs.
- Root `render.yaml`: records a free Docker web service with `/ready` as its health check and automatic deployment disabled for the later Jenkins stage.
- `app.py`: adds `/health`, `/ready`, and `/version`, and caches the existing model pair after its first load.
- `.gitignore`: keeps the serving models and sample CSV while excluding generated files and the unused credential-containing MongoDB test script.
- Original AWS Actions workflow: retained as manual-only so pushing this assessment project does not start an unrelated deployment.

## Intended Render settings

| Setting | Value |
|---|---|
| Name | networkx-devops-demo |
| Repository | AryanSheladia/DevOps_CA2_Group32 |
| Branch | main |
| Runtime | Docker |
| Root directory | empty; project is at repository root |
| Dockerfile path | ./Dockerfile |
| Docker context | . |
| Instance type | Free |
| Region | Singapore if available |
| Health-check path | /ready |
| Automatic deployment | Off |
| ENABLE_TRAINING | false |
| OMP_NUM_THREADS | 1 |
| OPENBLAS_NUM_THREADS | 1 |

## Verification

The updated app passed a local readiness and sample prediction check. Container build and hosted verification results will be recorded here when complete.

Hosted checks: `/docs`, `/ready`, `/version`, and a real CSV upload to `/predict`.

No credentials or Render deploy-hook URLs will be placed in committed evidence.

References: [Docker on Render](https://render.com/docs/docker), [Render environment variables](https://render.com/docs/environment-variables).
