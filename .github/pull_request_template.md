<!--
Thanks for contributing to the PostgreSQL Extensions Containers project!

This template is for changes other than adding a new extension (version bumps,
fixes, shared build/tooling changes, documentation, ...). If you are adding a
new extension, use the "new_extension" template instead by appending
`?template=new_extension.md` to the PR creation URL.

Before opening this PR, please read BUILD.md and the general CloudNativePG
CONTRIBUTING.md:
https://github.com/cloudnative-pg/governance/blob/main/CONTRIBUTING.md
-->

## Description

<!-- Explain what this PR does and why. -->



## Type of change

<!-- Tick the box that applies (put an "x" between the brackets, no spaces). -->

- [ ] Update to an existing extension (version bump, fix)
- [ ] Shared build infrastructure / tooling change
- [ ] Documentation only
- [ ] Other (please describe above)

<!-- If this fixes an open issue, reference it here, for example: Closes #123 -->


---

## Contributor checklist

- [ ] My commits are signed off for [DCO](https://developercertificate.org/)
      compliance (`git commit -s`).
- [ ] This PR targets the `main` branch of the upstream repository.
- [ ] `task checks:all` passes locally.
- [ ] For changes affecting one or more extensions, the relevant build and E2E
      tests pass (e.g. `task bake TARGET=<ext>`, `task e2e:test:full TARGET=<ext>`).
- [ ] Any `// renovate:` comments touched in `metadata.hcl` / `README.md` remain
      intact (`suite=`, `depName=`, `extractVersion=`).
- [ ] Documentation (`README.md`, `BUILD.md`, ...) updated where relevant.

---

## Maintainer review checklist

<!-- For maintainers only. -->

- [ ] CI is green for all affected targets / shared changes.
- [ ] DCO check passes.
- [ ] Change reviewed for correctness and scope; no unintended targets rebuilt.
- [ ] `// renovate:` annotations preserved so automated version tracking keeps
      working.
- [ ] If shared infrastructure changed, the `_shared` filter in
      `.github/workflows/bake.yml` was updated when all extensions must rebuild.
- [ ] PR targets `main` and is ready to merge.
