.SUFFIXES:

# Use bash if available, otherwise fall back to default shell
SHELL := $(shell which bash 2>/dev/null || echo /bin/sh)

# Find all directories containing metadata.hcl
FILES := $(shell find . -type f -name metadata.hcl)
DIRS  := $(patsubst %/,%,$(patsubst ./%,%,$(dir $(FILES))))

# Create push targets for each directory
PUSH_TARGETS := $(addprefix push-,$(DIRS))

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
# Push all images
# --------------------------
push: all $(PUSH_TARGETS)
	@echo -e "$(GREEN)======================================================$(NC)"
	@echo -e "$(GREEN)Push successful for all projects: $(DIRS)$(NC)"
	@echo -e "$(GREEN)======================================================$(NC)"

# --------------------------
# Generic per-project push
# Usage: make push-<project>
# --------------------------
$(PUSH_TARGETS): push-%: prereqs %
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
