# Building Postgres Extensions Container Images for CloudNativePG

This guide explains how to build Postgres extensions container images for
[CloudNativePG](https://cloudnative-pg.io) locally, using
[Docker Bake](https://docs.docker.com/build/bake/).

## Prerequisites

Before you begin, ensure that you have met the following
[prerequisites](https://github.com/cloudnative-pg/postgres-containers/blob/main/BUILD.md#prerequisites),
which primarily include:


1. **[Task](https://taskfile.dev/):** required to run tasks defined in the `Taskfile`.
2. **[Dagger](https://dagger.io/):** Must be installed and configured.
3. **Docker:** Must be installed and running.
4. **Docker Command Line:** The `docker` command must be executable.
5. **Docker Buildx:** The `docker buildx` plugin must be available.
6. **Docker Context:** A valid Docker context must be configured.

---

## Usage and Targets

### 1. Check prerequisites only

To verify that all prerequisites are correctly installed and configured:

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

To build all discovered projects:

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

To see the commands that would be executed without running the actual
`docker buildx bake` command, set the `DRY_RUN` flag:

```bash
task DRY_RUN=true
# or
task bake TARGET=pgvector DRY_RUN=true
```

## Testing locally

Local testing can be performed by using a local Docker container registry and a Kind cluster with CNPG installed.
The Taskfile includes utilities to set up and tear down such an environment.

### Create a local test environment

The `e2e:setup-env` task takes care of setting up a Kind cluster with a local Docker container registry connected to the same
Docker network and installs CloudNativePG by default.

```bash
task e2e:setup-env
```

The local container registry will be exposed locally at `localhost:5000`.

The Kubeconfig to connect to the Kind cluster can be retrieved with:

```bash
task e2e:export-kubeconfig KUBECONFIG_PATH=<path-to-export-kubeconfig>
```

### Build & Push the images to the registry

Any public registry can be used to test the extension images, but using the local registry
is the recommended approach for local testing.
The `task bake` command can be used to build and push the images, which by default
targets the local registry, but can be configured differently by setting the `registry` env variable.

```bash
task bake TARGET=<extension> PUSH=true
```

### Generate testing values for Chainsaw

Local testing is performed using [Chainsaw](https://github.com/kyverno/chainsaw), which requires a set
of specific values to be generated for the targeted extension image.
The `e2e:generate-values` task generates these values and export them in the extension directory:

```bash
task e2e:generate-values EXTENSION_IMAGE="<my-local-image>" TARGET="<extension>"
```

### Execute the end-to-end tests

The first step to run the end-to-end tests is getting the internal Kubeconfig for the Kind cluster so it
can be provided to the test command:

```bash
task e2e:export-kubeconfig KUBECONFIG_PATH=./kubeconfig INTERNAL=true
```
This command will export the Kubeconfig file to `./kubeconfig` file.

The end-to-end tests can then be executed using the `e2e:test` task:

```bash
task e2e:test TARGET="<extension>" KUBECONFIG_PATH="./kubeconfig"
```
The framework executes by default a set of generic tests defined in the `test` folder, but
more specific tests can be defined in the extension directory under the `test` folder which will be
included automatically.

### Tear down the local test environment

To clean up all the resources created by the `e2e:setup-env` task, run:

```bash
task e2e:cleanup
```
