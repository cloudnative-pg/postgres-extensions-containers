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

To verify that all prerequisites are correctly installed and configured:

```bash
task prereqs
```

---

## Scaffolding a New Extension

To create a new extension project structure, use the `create-extension` task:

```bash
task create-extension NAME=<extension-name>
```

This command generates a new directory named after your extension with the
following scaffolded files:

- `Dockerfile`: The base file to build the extension container image.
- `metadata.hcl`: Provides specific metadata information used to build and test
  the extension.
- `README.md`: A template to help you document the extension's usage.

> [!NOTE]
> These files are generated from generic templates and should be customized to
> meet your extension's specific requirements.

### Advanced Scaffolding

For more complex setups, you can use the `dagger` command directly to customize
distributions or package names:

```bash
dagger call -sm ./dagger/maintenance/ create --name="<name>" [ARGUMENTS]
```

**Common Arguments:**

| Argument | Description | Default |
| --- | --- | --- |
| `--distros` | Debian distributions the extension supports. | `[trixie, bookworm]` |
| `--package-name` | The Debian package name (uses `%version%` placeholder). | `postgresql-%version%-<name>` |
| `--versions` | Supported Postgres major versions. | `[18]` |
| `--templates-dir` | Source directory containing custom template files. | Internal template dir |

---

## Usage and Targets

### 1. Build configuration check (dry run)

To verify the configuration (running `docker buildx bake --check`) for all
projects without building or pulling layers:

```bash
task checks:all
```

### 2. Build all projects

To build all discovered projects:

```bash
task
# or
task bake:all
```

### 3. Build a specific project

To build a single project (e.g., the directory named `pgvector`):

```bash
task bake TARGET=pgvector
```

### 4. Push all images

To build all images and immediately push them to the configured registry:

```bash
task bake:all PUSH=true
```

### 5. Push images for a specific project

To push images for a single project (e.g., the directory named `pgvector`):

```bash
task bake TARGET=pgvector PUSH=true
```

### 6. Dry run mode

To see the commands that would be executed without running the actual
`docker buildx bake` command, set the `DRY_RUN` flag:

```bash
task DRY_RUN=true
# or
task bake TARGET=pgvector DRY_RUN=true
```

## Local testing guide

Testing your extensions locally ensures high-quality PRs and faster iteration
cycles. This environment uses a local Docker container registry and a Kind
cluster with CloudNativePG pre-installed.

> [!IMPORTANT]
> **Pre-submission requirement:** You must successfully run local tests before
> submitting a Pull Request for any extension.

### The Fast Path (Automated Testing)

End-to-end (E2E) tests are powered by [Chainsaw](https://github.com/kyverno/chainsaw).
To simplify the workflow, use the `e2e:test:full` task.
This single command automates environment setup, image building, and test
execution:

```bash
# Replace <extension> with the name of the extension (e.g., pgvector)
task e2e:test:full TARGET="<extension>"
```

Example for testing the `pgvector` extension:

```bash
task e2e:test:full TARGET="pgvector"
```

**When to use the step-by-step guide:** If the automated test fails during
environment setup, image building, or test execution, the step-by-step guide
below provides granular control for debugging each phase independently.

---

## E2E step-by-step Guide

### Initialize the environment

The `e2e:setup-env` utility creates a Kind cluster and attaches a local Docker
registry (available at `localhost:5000`).

```bash
task e2e:setup-env
```

> [!NOTE]
> Use the `REGISTRY_HOST_PORT` variable to customize the local registry port.
> If changed, you must pass this variable to all subsequent tasks that interact
> with the registry to ensure connectivity.

### Get access to the cluster

To interact with the cluster via `kubectl` from your local terminal:

```bash
task e2e:export-kubeconfig KUBECONFIG_PATH=./kubeconfig
export KUBECONFIG=$PWD/kubeconfig
```

> [!IMPORTANT]
> The local registry running alongside the Kind cluster is
> reachable within Kubernetes at `registry.pg-extensions:5000`. When testing your
> local builds, you must point the extension's `reference` to this internal
> address.
> For example, if you are testing a locally built `pgvector` image, use:
> `reference: registry.pg-extensions:5000/pgvector-testing:<tag>`

To allow the test suite (which runs within the Docker network) to reach the
Kubernetes API server, export the internal Kubeconfig:

```bash
task e2e:export-kubeconfig KUBECONFIG_PATH=./kubeconfig INTERNAL=true
```

### Build and push the extension (`bake`)

Build the image and push it to the local registry. This command tags the image
for `localhost:5000` automatically.

```bash
task bake TARGET="<extension>" PUSH=true
```

> [!NOTE]
> The destination registry is controlled by the `registry` variable defined within the `docker/bake.hcl` file.

### Prepare testing values

Generate configuration values so Chainsaw knows which local image to target for
the E2E tests:

```bash
task e2e:generate-values TARGET="<extension>" EXTENSION_IMAGE="<my-local-image>"
```

### Execute End-to-End tests

Run the test suite using the internal Kubeconfig. This executes both the
generic tests (global `/test` folder) and extension-specific tests (target
`/test` folder).

```bash
task e2e:test TARGET="<extension>" KUBECONFIG_PATH="./kubeconfig"
```

---

### Tear down the local test environment

To clean up all the resources created by the `e2e:setup-env` task, run:

```bash
task e2e:cleanup
```
