# Contributing: Adding a New PostgreSQL Extension

This guide walks you through the lifecycle of adding a new extension, from
setting up your environment to submitting a Pull Request.

> [!IMPORTANT]
> Please ensure you have also read the general
> [CONTRIBUTING.md](https://github.com/cloudnative-pg/governance/blob/main/CONTRIBUTING.md)
> for CloudNativePG before proceeding.

## 1. Phase One: Fork, Clone, and Validate

Before proposing a change, ensure your local machine is compatible with the
[build stack](BUILD.md).

1. **Fork** the [cloudnative-pg/postgres-extensions-containers](https://github.com/cloudnative-pg/postgres-extensions-containers) repository.
2. **Clone** your fork and enter the directory:
```sh
git clone https://github.com/<your-username>/postgres-extensions-containers.git
cd postgres-extensions-containers
```
3. **Verify the Environment:** Run the following to ensure you can build the
   existing project ecosystem.
```sh
task prereqs      # Check if Go, Task, and Docker are ready
task checks:all   # Validate current configurations
task bake:all     # Build all existing extensions to confirm the Dagger engine
```

---

## 2. Phase Two: The Proposal & Package Discovery

To maintain high standards and avoid duplicated effort or architectural
conflicts, every new extension begins with a formal proposal.
During this phase, you must verify that the extension is available in the PGDG
(PostgreSQL Global Development Group) repositories and identify its versioning
logic.

### Identify the Package & Version

You must verify the package across both the current Debian `stable` and
`oldstable` distributions to ensure compatibility. Use a temporary container to
search the repositories:

For Debian `stable` (13, `trixie`):

```sh
docker run -u root -ti --rm ghcr.io/cloudnative-pg/postgresql:18-minimal-trixie
```

For Debian `olstable` (12, `bookworm`):

```sh
docker run -u root -ti --rm ghcr.io/cloudnative-pg/postgresql:18-minimal-bookworm
```

Then, inside the container:

```sh
apt update && apt search <EXTENSION_NAME>
```

#### Understanding the Version String

Take note of both the **package name** and the **version string**.
Using `pgvector` as an example, you will notice that while the package name
remains constant, the versioning reflects the underlying Debian release:

- `trixie`: `0.8.2-1.pgdg13+1`
- `bookworm`: `0.8.2-1.pgdg12+1`

> [!IMPORTANT]
> The `pgdg13` or `pgdg12` suffix is critical. Correctly identifying this
> versioning pattern ensures that `renovate` can automatically monitor the
> upstream repositories and trigger update Pull Requests once your extension is
> merged.

#### Inspecting the Package Content

If you want to get a list of the files contained in the package, you need to
first install the extension in the disposable container:

```sh
apt install <package-name>
```

Then, list the content of the package with:

```sh
dpkg -L <full-package-name>
```

Confirm that `.control` and `.sql` files are present in the expected PostgreSQL
paths.

> [!IMPORTANT]
> If the package doesn't contain any `.control` file, it is likely to be a
> **PostgreSQL module** rather than an extension. In this case, remember to set
> the `create_extension` option to `false` in your `metadata.hcl` file.

### Open an Issue

> [!IMPORTANT]
> **Community Commitment:** By opening the issue, you are confirming your
> intent to help maintain this extension on behalf of the CloudNativePG
> community.

After gathering the package details and verifying the extension's license,
submit your proposal:

1. Point your browser to ["New Extension Proposal"](https://github.com/cloudnative-pg/postgres-extensions-containers/issues/new/choose).
2. Provide the package name, versioning info, and a link to the upstream source.
3. State the licence clearly:
    - CNCF-Allowed: licenses on the [CNCF Allowlist](https://github.com/cncf/foundation/blob/main/policies-guidance/allowed-third-party-license-policy.md) (e.g., Apache-2.0, MIT, or PostgreSQL) are generally pre-approved.
    - Other Open Source: licenses like FSF-approved (GNU GPL) will be evaluated on a case-by-case basis.
    - Redistribution: since we redistribute unmodified software, ensure you
      identify where the upstream source code can be found (required for GNU
      GPL compliance).

> [!NOTE]
> You do not need to wait for maintainer approval to begin development or
> submit your PR. You are encouraged to proceed immediately; however, please be
> aware that if a fundamental issue (e.g., licensing) is discovered during the
> proposal review, you may need to modify or discard your work.

---

## 3. Phase Three: Implementation & Scaffolding

### Create a Branch

```sh
git checkout -b dev/<extension-name>
```

### Scaffolding

Generate the directory structure automatically:

```sh
task create-extension NAME=<extension-name>
```

> [!NOTE]
> For advanced scaffolding (custom distros or versions), see
> [`BUILD.md`](./BUILD.md).

### Customizing the Files

The scaffolding generates `metadata.hcl`, `Dockerfile`, and `README.md`.
Follow the specific instructions and "TODO" comments found within each
generated file to finalize your extension.

> [!TIP]
> Pay close attention to the `// renovate:` comments in the metadata; these are
> required for automated version tracking.

---

## 4. Phase Four: Local Testing & Validation

Testing is the most critical part of the lifecycle.

### Automated E2E Testing

> [!NOTE]
> For a detailed breakdown of the testing infrastructure, refer to
> [`BUILD.md`](./BUILD.md).

The repository provides a framework for full End-to-End validation. Ensure that
the entire pipeline is working:

```sh
task checks:all
```

Then run the full E2E tests for the extension. This task will build your image,
push it to a local registry, spin up a Kind cluster, and run the functional
tests:

```sh
task e2e:test:full TARGET="<extension-name>"
```

### Local Manual Verification

Once the image is built, we recommend pulling it from your local registry,
inspecting it manually to ensure the file structure is correct, and testing it
with CloudNativePG.

Once the image is built and pushed to the local registry (`localhost:5000`),
you should verify the generated tags. You can use `skopeo` to inspect the local
registry:

```bash
skopeo list-tags --tls-verify=false docker://localhost:5000/<extension-name>-testing
```

> [!IMPORTANT]
> Remember to add the `-testing` suffix to the container registry.

You should see an output similar to this, confirming all PostgreSQL and Debian
version combinations were built correctly.

### Extending Tests

While the framework provides a generic smoke test, we highly encourage you to
add **extension-specific tests**. Review the [`postgis`](./postgis) directory
for an example of additional testing using the Chainsaw framework.

## 5. Phase Five: Documentation & The Pull Request

### The `README.md` file

The `README.md` is typically the last file you complete. A clear, professional
`README.md` makes an extension successful. Ensure it includes YAML examples for
`Cluster` and `Database` resources so users can immediately adopt your work.

### Commit and Submit

Once you have verified your extension locally and are satisfied with the
results, it is time to submit your contribution.

To maintain a clean and searchable history, we require a specific commit
format. If you have multiple experimental commits on your branch, please squash
them into a single commit before submitting.

Format:

```text
feat: add `<extension-name>` container image

<DESCRIPTION: Explain what the extension does and why it's being added.>

Closes #<issue-id>
```

Submission Requirements:

- **DCO Compliance**: All commits must be signed (`git commit -s`) to certify
  that you have the right to submit the code under the project's license.
- **Upstream Target**: Ensure your Pull Request is targeting the `main` branch of
  the upstream repository.

By submitting, you confirm your commitment to maintain this extension on behalf
of the CloudNativePG Community.
