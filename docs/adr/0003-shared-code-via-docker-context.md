# Monorepo Shared Code via Docker Build Contexts

We decided to share common utilities (e.g., Celery configuration, data models) across our independent Worker containers by utilizing Docker build contexts rather than creating and publishing internal Python packages (e.g., via private PyPI).

All `Dockerfile`s will be executed from the root of the monorepo, allowing them to `COPY shared/ ./shared` into their respective container images. This avoids the overhead of package versioning and distribution for an early-stage project while still satisfying the requirement that Workers run in completely independent containers with isolated runtime dependencies.