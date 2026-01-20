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

## Local testing guide

Testing your extensions locally ensures high-quality PRs and faster iteration
cycles. This environment uses a local Docker container registry and a Kind
cluster with CloudNativePG pre-installed.

> [!IMPORTANT]
> **Pre-submission requirement:** You must successfully run local tests before
> submitting a Pull Request for any extension.

### Run e2e tests for a specific extension

E2E tests are performed using [Chainsaw](https://github.com/kyverno/chainsaw)
which enables declarative testing through a set of specific manifests.
The Taskfile collects all the necessary steps to setup the environment and
to execute the tests into a single command:

```bash
task e2e:test:full TARGET="<extension>"
```

If issues arise, follow the step-by-step guide below for easier
troubleshooting and a better understanding of the process.

## E2E Step by Step Guide

### Initialize the environment

The `e2e:setup-env` utility automates the heavy lifting. It creates a Kind
cluster, attaches a local Docker registry (available at `localhost:5000`), and
installs the CloudNativePG operator.

```bash
task e2e:setup-env
```

### Get access to the cluster

Even though the cluster is running, your local `kubectl` doesn't know how to
talk to it yet. You need to "export" the credentials (the Kubeconfig).

If you want to run `kubectl get pods` from your own laptop's terminal, use the
standard export:

```bash
task e2e:export-kubeconfig KUBECONFIG_PATH=./kubeconfig
export KUBECONFIG=$PWD/kubeconfig
```

If you are running a test script that is also running inside a Docker container
on the same network, like in the case of Kind, it needs the "internal" address
to find the API server:

```bash
task e2e:export-kubeconfig KUBECONFIG_PATH=./kubeconfig INTERNAL=true
```

### Build and push the extension (`bake`)

Before the cluster can use your extension, you must build the image and push it
to the local registry (see ["Push images for a specific project" above](#6-push-images-for-a-specific-project)):

```bash
task bake TARGET="<extension>" PUSH=true
```

This command tags the image for `localhost:5000` and pushes it automatically.

> [!TIP]
> You can change the default registry through the `registry` environment variable
> (defined in the `docker/bake.hcl` file).

### Prepare testing values

We use [Chainsaw](https://github.com/kyverno/chainsaw) for declarative
end-to-end testing. Before running tests, you must generate specific
configuration values for your extension image.

Run the following command to export these values into your extension's
directory:

```bash
task e2e:generate-values TARGET="<extension>" EXTENSION_IMAGE="<my-local-image>"
```

For example, to generate the values for the local test of the local image, you could run something similar to the following:

```bash
# The actual name of the image might be different on your system
task e2e:generate-values TARGET=pgvector EXTENSION_IMAGE="localhost:5000/pgvector-testing:0.8.1-18-trixie"
```

### Execute End-to-End tests

The testing framework requires an internal Kubeconfig to communicate correctly
within the Docker network.

First, export the internal configuration as shown above:

```bash
task e2e:export-kubeconfig KUBECONFIG_PATH=./kubeconfig INTERNAL=true
```

Then, run the `e2e:test` task. This executes both the generic tests (located in
the global `/test` folder) and any extension-specific tests (located in the
target's `/test` folder):

```bash
task e2e:test TARGET="<extension>" KUBECONFIG_PATH="./kubeconfig"
```

You can test the `pgvector` extension with:

```bash
task e2e:test TARGET="pgvector" KUBECONFIG_PATH="./kubeconfig"
```

### Tear down the local test environment

To clean up all the resources created by the `e2e:setup-env` task, run:

```bash
task e2e:cleanup
```
