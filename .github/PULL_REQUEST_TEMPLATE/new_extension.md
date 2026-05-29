<!--
Thanks for contributing a new extension to the PostgreSQL Extensions Containers
project!

Before opening this PR, please make sure you have read:
  - CONTRIBUTING_NEW_EXTENSION.md (lifecycle for adding an extension)
  - BUILD.md (build system)
  - the general CloudNativePG CONTRIBUTING.md:
    https://github.com/cloudnative-pg/governance/blob/main/CONTRIBUTING.md
-->

## Extension

<!-- Name of the extension and a short description of what it does and its
     primary use case. -->



Closes #<!-- proposal issue id -->

---

## Contributor checklist

<!-- All items must be addressed before requesting a review. -->

- [ ] My commits are signed off for [DCO](https://developercertificate.org/)
      compliance (`git commit -s`).
- [ ] Experimental commits have been squashed into a single, well-formed commit.
- [ ] This PR targets the `main` branch of the upstream repository.
- [ ] A [New Extension Proposal](https://github.com/cloudnative-pg/postgres-extensions-containers/issues/new/choose)
      issue exists and is referenced via `Closes #<id>` above.
- [ ] The commit message follows the format:
      ``feat: add `<extension-name>` container image``.
- [ ] The Debian package was verified to exist in the `main` component on both
      Debian `stable` (`trixie`) and `oldstable` (`bookworm`) via `apt search`.
- [ ] The extension was scaffolded with `task create-extension NAME=<ext>` and all
      `TODO` comments in the generated files were resolved.
- [ ] `metadata.hcl` sets the correct `package` (full Debian version) and, when
      `create_extension = true`, the matching `sql` (catalog) version.
- [ ] `create_extension` is set correctly (`false` for PostgreSQL *modules* with
      no `.control` file, verified with `dpkg -L`).
- [ ] The `renovate:` annotations in `metadata.hcl` and `README.md` are present
      and intact (`suite=`, `depName=`, `extractVersion=`).
- [ ] Every component in the image is covered by a license on the
      [CNCF Allowlist](https://github.com/cncf/foundation/blob/main/policies-guidance/allowed-third-party-license-policy.md);
      SPDX `licenses` in `metadata.hcl` are accurate.
- [ ] `task checks:all` passes locally.
- [ ] Full E2E passes: `task e2e:test:full TARGET="<extension-name>"`.
- [ ] `README.md` is complete and includes a working `Cluster` example (plus a
      `Database` example with `CREATE EXTENSION` when `create_extension = true`).
- [ ] An entry for the new extension folder was added to
      [`CODEOWNERS`](https://github.com/cloudnative-pg/postgres-extensions-containers/blob/main/CODEOWNERS)
      with the component owner's GitHub handle(s).
- [ ] I confirm my commitment to maintain this extension on behalf of the
      CloudNativePG community.

---

## Maintainer review checklist

<!-- For maintainers only. Do not merge until every item is verified. -->

- [ ] The linked proposal issue is approved (label `new-extension`) and the
      `Closes #<id>` reference is correct.
- [ ] CI is green: the `bake` workflow built the new target for the full
      `pgVersions × distributions × {amd64, arm64}` matrix.
- [ ] DCO check passes and history is a single clean commit with the required
      `feat: add ...` message format.
- [ ] License compliance reviewed: all redistributed components (extension +
      transitive/system libs) are on the CNCF Allowlist; SPDX `licenses` match.
- [ ] `metadata.hcl` reviewed: `package`/`sql` versions, `create_extension`,
      runtime settings (`shared_preload_libraries`, `*_path`, `env`,
      `required_extensions`) and behavior flags are correct.
- [ ] `renovate:` annotations are intact so automated version PRs will track
      the package going forward.
- [ ] `Dockerfile` reviewed: final stage is `FROM scratch` and contains only the
      expected artifacts; the `USER 65532:65532` directive matches the nonroot
      convention.
- [ ] E2E / Chainsaw tests pass: the extension is registered (when
      `create_extension = true`), or the Cluster reaches Healthy with the image
      mounted for preload-only modules.
- [ ] `README.md` is clear and its `Cluster` example (and `Database` example
      when `create_extension = true`) are valid.
- [ ] `CODEOWNERS` entry is present and the component owner(s) accept the
      long-term maintenance commitment.
- [ ] PR targets `main` and is ready to merge.
