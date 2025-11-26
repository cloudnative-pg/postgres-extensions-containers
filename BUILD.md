# Building Postgres Extensions Container Images for CloudNativePG

This guide explains how to build Postgres extensions operand images for
[CloudNativePG](https://cloudnative-pg.io) using
[Docker Bake](https://docs.docker.com/build/bake/) together with a
[GitHub Actions workflow](.github/workflows/bake.yml).

Although it is not necessary, we recommend you use
[GNU Make](https://www.gnu.org/software/make/) to build the images locally as
outlined below.

## Prerequisites

Before you begin, ensure that you have met the following
[prerequisites](https://github.com/cloudnative-pg/postgres-containers/blob/main/BUILD.md#prerequisites),
which primarily include:

1.  **Docker:** Must be installed and running.
2.  **Docker Command Line:** The `docker` command must be executable.
3.  **Docker Buildx:** The `docker buildx` plugin must be available.
4.  **Docker Context:** A valid Docker context must be configured.

---

## Usage and Targets

The `Makefile` dynamically discovers all subdirectories that contain a
`metadata.hcl` file (e.g., `./pgvector/metadata.hcl`) and creates individual
build targets for each project.

### 1. Check prerequisites only

To verify that Docker and Buildx are correctly installed and configured:

```bash
make prereqs
```

### 2. Build configuration check (dry run)

To verify the configuration (running `docker buildx bake --check`) for all
projects without building or pulling layers:

```bash
make check
```

### 3. Build all projects

To check prerequisites and build all discovered projects:

```bash
make
# or
make all
```

### 4. Build a specific project

To build a single project (e.g., the directory named `pgvector`):

```bash
make pgvector
```

### 5. Push all images

To build all images and immediately push them to the configured registry:

```bash
make push
```

### 6. Push images for a specific project

To push images for a single project (e.g., the directory named `pgvector`):

```bash
make push-pgvector
```

### 7. Dry run mode

To see the commands that would be executed without running the actual `docker
buildx bake` command, set the `DRY_RUN` flag:

```bash
make DRY_RUN=true
# or
make pgvector DRY_RUN=true
```
