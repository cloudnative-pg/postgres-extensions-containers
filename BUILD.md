# Building Postgres Extensions Container Images for CloudNativePG

This guide explains how to build Postgres extensions operand images for
[CloudNativePG](https://cloudnative-pg.io) using
[Docker Bake](https://docs.docker.com/build/bake/) together with a
[GitHub Actions workflow](.github/workflows/bake.yml).

## Prerequisites

Before you begin, ensure that you have met the following
[prerequisites](https://github.com/cloudnative-pg/postgres-containers/blob/main/BUILD.md#prerequisites),
which primarily include:

1. **Task:** required to run tasks defined in the `Taskfile`.
2. **Dagger:** Must be installed and configured.
3. **Docker:** Must be installed and running.
4. **Docker Command Line:** The `docker` command must be executable.
5. **Docker Buildx:** The `docker buildx` plugin must be available.
6. **Docker Context:** A valid Docker context must be configured.

---

## Usage and Targets

### 1. Check prerequisites only

To verify that Docker and Buildx are correctly installed and configured:

```bash
task prereqs
```

### 2. Build configuration check (dry run)

To verify the configuration (running `docker buildx bake --check`) for all
projects without building or pulling layers:

```bash
task checks:all
```

### 3. Build all projects

To check prerequisites and build all discovered projects:

```bash
task
# or
task bake:all
```

### 4. Build a specific project

To build a single project (e.g., the directory named `pgvector`):

```bash
task bake TARGET=pgvector
```

### 5. Push all images

To build all images and immediately push them to the configured registry:

```bash
task bake:all PUSH=true
```

### 6. Push images for a specific project

To push images for a single project (e.g., the directory named `pgvector`):

```bash
task bake TARGET=pgvector PUSH=true
```

### 7. Dry run mode

To see the commands that would be executed without running the actual `docker
buildx bake` command, set the `DRY_RUN` flag:

```bash
task DRY_RUN=true
# or
task bake TARGET=pgvector DRY_RUN=true
```
