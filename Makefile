.SUFFIXES:

# Use bash if available, otherwise fall back to default shell
SHELL := $(shell which bash 2>/dev/null || echo /bin/sh)

# Find all directories containing metadata.hcl
FILES := $(shell find . -type f -name metadata.hcl)
DIRS  := $(patsubst %/,%,$(patsubst ./%,%,$(dir $(FILES))))

ifeq ($(DIRS),)
$(error No subdirectories with metadata.hcl files found)
endif

# Default supported distributions
DISTROS := $(shell sed -n '/variable "distributions"/,/}/ { s/^[[:space:]]*"\([^"]*\)".*/\1/p }' docker-bake.hcl)
# Default supported PostgreSQL majors
POSTGRES_MAJORS := $(shell sed -n '/variable "pgVersions"/,/]/ { s/^[[:space:]]*"\([^"]*\)".*/\1/p }' docker-bake.hcl)

# Find all extensions with AUTO_UPDATE_OS_LIBS = true
EXTENSIONS_WITH_OS_LIBS := $(shell \
  for dir in $(DIRS); do \
    value=$$(sed -n 's/.*auto_update_os_libs *= *//p' "$$dir/metadata.hcl" | tr -d ' '); \
    if [ "$$value" = "true" ]; then echo "$$dir"; fi; \
  done \
)

# Create push targets for each directory
PUSH_TARGETS := $(addprefix push-,$(DIRS))

# Create UPDATE_OS_LIBS targets for each extension
UPDATE_OS_LIBS_TARGETS := $(addprefix update-os-libs-,$(EXTENSIONS_WITH_OS_LIBS))

.PHONY: all check prereqs push $(DIRS) $(PUSH_TARGETS)

# Colours
GREEN := \033[0;32m
BLUE  := \033[0;34m
RED   := \033[0;31m
NC    := \033[0m

# Dry run flag
DRY_RUN ?= false

default: all

# --------------------------
# Prerequisite checks
# --------------------------
prereqs:
	@echo -e "$(BLUE)Checking prerequisites...$(NC)"
	@command -v docker >/dev/null 2>&1 || { echo -e "$(RED)Docker is not installed.$(NC)"; exit 1; }
	@docker --version >/dev/null 2>&1 || { echo -e "$(RED)Cannot run docker command.$(NC)"; exit 1; }
	@docker buildx version >/dev/null 2>&1 || { echo -e "$(RED)Docker Buildx not available.$(NC)"; exit 1; }
	@docker context inspect >/dev/null 2>&1 || { echo -e "$(RED)Docker context not configured.$(NC)"; exit 1; }
	@echo -e "$(GREEN)All prerequisites satisfied!$(NC)"

# --------------------------
# Dry-run or verification
# --------------------------
check: prereqs
	@echo -e "$(BLUE)Performing bake --check for all projects...$(NC)"
	@$(foreach dir,$(DIRS), \
		echo -e "$(BLUE)[CHECK] $(dir) $(NC)"; \
		docker buildx bake -f $(dir)/metadata.hcl -f docker-bake.hcl --check; \
	)

# --------------------------
# Update OS libraries for all images
# --------------------------
update-os-libs: prereqs $(UPDATE_OS_LIBS_TARGETS)
	@echo -e "$(GREEN)======================================================$(NC)"
	@echo -e "$(GREEN)OS libraries update for all projects: $(EXTENSIONS_WITH_OS_LIBS)$(NC)"
	@echo -e "$(GREEN)======================================================$(NC)"

# --------------------------
# Generic per-project OS libraries update
# Usage: make update-os-libs-<project>
# --------------------------
$(UPDATE_OS_LIBS_TARGETS): update-os-libs-%: prereqs
	@echo -e "$(BLUE)Performing an OS libraries update for $*...$(NC)"
	@mkdir -p "$*/system-libs" ;\
	for DISTRO in $(DISTROS); do \
		for MAJOR in $(POSTGRES_MAJORS); do \
			docker run --rm -u 0 "ghcr.io/cloudnative-pg/postgresql:18-minimal-$$DISTRO" \
				bash -c "apt-get update >/dev/null; apt-get install -qq --print-uris --no-install-recommends postgresql-$$MAJOR-$*" \
			| cut -d ' ' -f 2,4 \
			| grep '^lib' \
			| sort \
			> "$*/system-libs/$$MAJOR-$$DISTRO-os-libs.txt"; \
		done; \
	done

# --------------------------
# Push all images
# --------------------------
push: prereqs $(PUSH_TARGETS)
	@echo -e "$(GREEN)======================================================$(NC)"
	@echo -e "$(GREEN)Push successful for all projects: $(DIRS)$(NC)"
	@echo -e "$(GREEN)======================================================$(NC)"

# --------------------------
# Generic per-project push
# Usage: make push-<project>
# --------------------------
$(PUSH_TARGETS): push-%: prereqs
	@echo -e "$(BLUE)Performing bake --push for $*...$(NC)"
ifeq ($(DRY_RUN),true)
	@echo -e "$(GREEN)[DRY RUN] docker buildx bake -f $*/metadata.hcl -f docker-bake.hcl --push$(NC)"
else
	docker buildx bake -f $*/metadata.hcl -f docker-bake.hcl --push
endif
	@echo -e "$(GREEN)--- Successfully pushed $* ---$(NC)"

# --------------------------
# Build targets
# --------------------------
all: prereqs $(DIRS)
	@echo -e "$(GREEN)======================================================$(NC)"
	@echo -e "$(GREEN)Build successful for all projects: $(DIRS)$(NC)"
	@echo -e "$(GREEN)======================================================$(NC)"

# Per-project build
$(DIRS): %: %/metadata.hcl
	@echo -e "$(BLUE)--- Starting Docker Buildx Bake for target: $@ ---$(NC)"
ifeq ($(DRY_RUN),true)
	@echo -e "$(GREEN)[DRY RUN] docker buildx bake -f $@/metadata.hcl -f docker-bake.hcl$(NC)"
else
	docker buildx bake -f $@/metadata.hcl -f docker-bake.hcl
endif
	@echo -e "$(GREEN)--- Successfully built $@ ---$(NC)"
