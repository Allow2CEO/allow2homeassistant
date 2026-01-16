# Home Assistant Publishing Research

This document provides comprehensive research on publishing Home Assistant custom integrations and add-ons, based on analysis of the official Home Assistant add-ons example repository and HACS documentation.

## Table of Contents

1. [Distribution Approaches Comparison](#1-distribution-approaches-comparison)
2. [Add-on Repository Structure](#2-add-on-repository-structure)
3. [HACS Integration Structure](#3-hacs-integration-structure)
4. [Recommendation for Allow2](#4-recommendation-for-allow2)
5. [GitHub Workflow Requirements](#5-github-workflow-requirements)
6. [Container Registry Options](#6-container-registry-options)
7. [my.home-assistant.io Button Format](#7-myhome-assistantio-button-format)
8. [Current Repository Analysis](#8-current-repository-analysis)

---

## 1. Distribution Approaches Comparison

### Option A: HACS (Home Assistant Community Store)

**What it is:** HACS is a community store that allows users to install custom integrations directly into their Home Assistant instance without Docker containers.

**How it works:**
- Users install HACS as an integration
- They can then browse and install custom integrations from GitHub repositories
- The integration files are downloaded directly to `custom_components/` folder

**Pros:**
- Simpler distribution - no Docker images required
- Faster installation for users
- Works on all Home Assistant installation types (Core, Container, Supervised, OS)
- Lower maintenance burden (no container builds)
- Widely adopted by the community

**Cons:**
- Requires users to install HACS first
- Not included in official Home Assistant UI by default

### Option B: Add-on Approach

**What it is:** Add-ons are Docker containers that run alongside Home Assistant, managed by the Supervisor.

**How it works:**
- Users add your repository URL to Home Assistant Supervisor
- The Supervisor pulls your Docker image and runs it
- The add-on can then install/manage the custom component

**Pros:**
- Official Home Assistant UI integration
- Can provide additional services beyond the integration
- Automatic updates through Supervisor

**Cons:**
- Only works on Supervised/OS installations (NOT Core or Container)
- Requires building and maintaining Docker images for 5 architectures
- More complex CI/CD pipeline
- Higher maintenance burden
- For a pure integration, it's overkill

### Option C: Both Approaches (Dual Distribution)

**What it is:** Provide both distribution methods simultaneously.

**How it works:**
- Same repository serves both HACS (via `custom_components/` folder) and Add-on (via config.yaml, Dockerfile, etc.)
- Users choose their preferred installation method

**Pros:**
- Maximum user reach
- Flexibility for different installation types

**Cons:**
- Highest maintenance burden
- More complex repository structure
- Must keep both methods in sync

---

## 2. Add-on Repository Structure

Based on the official [home-assistant/addons-example](https://github.com/home-assistant/addons-example) repository:

### Complete Directory Structure

```
repository-root/
├── .github/
│   └── workflows/
│       ├── builder.yaml          # Multi-arch Docker build workflow
│       └── lint.yaml             # Add-on linting workflow
├── addon-name/                   # Each add-on in its own folder
│   ├── rootfs/                   # Files to copy into container root
│   │   └── etc/
│   │       └── services.d/       # S6-overlay services
│   │           └── addon-name/
│   │               └── run       # Main service script
│   ├── translations/             # Localization files
│   │   └── en.yaml
│   ├── apparmor.txt              # Security profile (optional)
│   ├── build.yaml                # Build configuration per architecture
│   ├── CHANGELOG.md              # Version history
│   ├── config.yaml               # Add-on configuration (REQUIRED)
│   ├── Dockerfile                # Container definition (REQUIRED)
│   ├── DOCS.md                   # Detailed documentation
│   ├── icon.png                  # 256x256 icon
│   ├── logo.png                  # Logo image
│   └── README.md                 # Brief overview
├── .devcontainer.json            # Development container config
├── LICENSE                       # License file
├── README.md                     # Repository README
└── repository.yaml               # Repository metadata (REQUIRED)
```

### Required Files

#### 1. repository.yaml (Repository Root)

```yaml
name: Your Repository Name
url: https://github.com/your-org/your-repo
maintainer: Your Name <email@example.com>
```

#### 2. config.yaml (Add-on Folder)

```yaml
# Required fields
name: Add-on Name
version: "1.0.0"
slug: addon-slug
description: Brief description of the add-on
arch:
  - armhf
  - armv7
  - aarch64
  - amd64
  - i386

# Optional but recommended
url: https://github.com/your-org/your-repo
startup: application          # initialize, system, services, application, once
boot: auto                    # auto, manual, manual_only
init: false                   # Use S6-overlay init system

# Container configuration
image: ghcr.io/your-org/addon-name-{arch}

# Directory mappings
map:
  - config:rw                 # Read/write access to HA config
  - share:rw                  # Shared folder access
  - ssl:ro                    # SSL certificates (read-only)

# User options
options:
  option_name: "default_value"

schema:
  option_name: str?           # str, bool, int, float, email, url, port

# API access
homeassistant_api: true       # Enable Home Assistant API access
hassio_api: true              # Enable Supervisor API access

# Ports
ports:
  8080/tcp: 8080
ports_description:
  8080/tcp: Web Interface
```

#### 3. build.yaml (Add-on Folder)

```yaml
build_from:
  aarch64: ghcr.io/home-assistant/aarch64-base:3.15
  amd64: ghcr.io/home-assistant/amd64-base:3.15
  armhf: ghcr.io/home-assistant/armhf-base:3.15
  armv7: ghcr.io/home-assistant/armv7-base:3.15
  i386: ghcr.io/home-assistant/i386-base:3.15

labels:
  org.opencontainers.image.title: "Add-on Title"
  org.opencontainers.image.description: "Add-on description"
  org.opencontainers.image.source: "https://github.com/your-org/repo"
  org.opencontainers.image.licenses: "MIT"

args:
  TEMPIO_VERSION: "2021.09.0"
```

#### 4. Dockerfile (Add-on Folder)

```dockerfile
ARG BUILD_FROM
FROM $BUILD_FROM

# Build arguments
ARG TEMPIO_VERSION BUILD_ARCH

# Install tempio (template engine)
RUN curl -sSLf -o /usr/bin/tempio \
    "https://github.com/home-assistant/tempio/releases/download/${TEMPIO_VERSION}/tempio_${BUILD_ARCH}"

# Copy root filesystem
COPY rootfs /
```

---

## 3. HACS Integration Structure

Based on [HACS documentation](https://hacs.xyz/docs/publish/integration):

### Required Directory Structure

```
repository-root/
├── custom_components/
│   └── your_integration/
│       ├── __init__.py           # Integration setup
│       ├── manifest.json         # Integration manifest (REQUIRED)
│       ├── config_flow.py        # Configuration UI (if config_flow: true)
│       ├── const.py              # Constants
│       ├── sensor.py             # Sensor platform
│       ├── binary_sensor.py      # Binary sensor platform
│       ├── strings.json          # UI strings
│       └── translations/
│           └── en.json
├── hacs.json                     # HACS manifest (REQUIRED)
├── README.md                     # Documentation (REQUIRED)
└── LICENSE                       # License file
```

### Required Files

#### 1. manifest.json (Integration Folder)

```json
{
  "domain": "your_integration",
  "name": "Your Integration",
  "codeowners": ["@your-github-username"],
  "config_flow": true,
  "dependencies": [],
  "documentation": "https://github.com/your-org/repo",
  "integration_type": "service",
  "iot_class": "cloud_polling",
  "issue_tracker": "https://github.com/your-org/repo/issues",
  "requirements": ["some-package>=1.0.0"],
  "version": "1.0.0"
}
```

**Required Fields:**
- `domain` - Unique identifier (must match folder name)
- `name` - Display name
- `codeowners` - GitHub usernames
- `dependencies` - Other integrations required
- `documentation` - URL to docs
- `integration_type` - Category (device, entity, hardware, helper, hub, service, system, virtual)
- `iot_class` - Connectivity type (cloud_polling, local_polling, cloud_push, local_push, assumed_state, calculated)
- `requirements` - Python packages
- `version` - REQUIRED for custom integrations

#### 2. hacs.json (Repository Root)

```json
{
  "name": "Your Integration",
  "render_readme": true,
  "homeassistant": "2024.1.0",
  "zip_release": true,
  "filename": "integration.zip",
  "hide_default_branch": false,
  "country": ["US", "GB"],
  "content_in_root": false
}
```

**Available Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Display name in HACS |
| `content_in_root` | bool | No | If true, files are at root (not in custom_components/) |
| `zip_release` | bool | No | Use zipped release archives |
| `filename` | string | No | Name of zip file (required if zip_release is true) |
| `hide_default_branch` | bool | No | Don't offer default branch for download |
| `country` | array | No | ISO 3166-1 alpha-2 country codes for regional repos |
| `homeassistant` | string | No | Minimum Home Assistant version |
| `hacs` | string | No | Minimum HACS version |
| `render_readme` | bool | No | Render README in HACS UI |
| `persistent_directory` | string | No | Directory kept safe during upgrades |

### GitHub Repository Requirements for HACS

1. **Public repository** - Must be publicly accessible
2. **Description** - Brief summary displayed in HACS
3. **Topics** - Add `hacs` topic for discoverability
4. **README.md** - Documentation explaining usage
5. **Releases** - Use GitHub releases for versioning (preferred)

---

## 4. Recommendation for Allow2

### Primary Recommendation: HACS Distribution

**Reasoning:**

1. **Allow2 is a pure integration** - It only needs to create sensors and binary sensors. It doesn't need to run a separate service or provide additional functionality that would benefit from containerization.

2. **Wider user base** - HACS works on ALL Home Assistant installation types:
   - Home Assistant OS (supported)
   - Home Assistant Supervised (supported)
   - Home Assistant Container (supported)
   - Home Assistant Core (supported)

   Add-ons ONLY work on OS and Supervised.

3. **Simpler maintenance** - No Docker images to build and maintain across 5 architectures.

4. **Community standard** - Most custom integrations use HACS. Users expect it.

5. **Faster installation** - Direct file copy vs. Docker image pull.

### Secondary Option: Keep Add-on for Advanced Users

If you want to provide the add-on as well (for users who prefer Supervisor-managed installations), you can maintain both. The current repository structure already supports this.

### What to Remove if Going HACS-Only

If choosing HACS-only distribution:
- Remove: `Dockerfile`, `build.yaml`, `run.sh`, `config.yaml` (add-on config)
- Remove: `.github/workflows/build.yaml` (Docker build)
- Keep: `repository.yaml` (rename to support HACS), `hacs.json`, `custom_components/`

### What to Keep for Dual Distribution

Current structure is correct for dual distribution. No changes needed.

---

## 5. GitHub Workflow Requirements

### For HACS Distribution Only

#### .github/workflows/validate.yaml

```yaml
name: Validate

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  validate-hacs:
    name: HACS Validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: HACS Validation
        uses: hacs/action@main
        with:
          category: integration

  validate-hassfest:
    name: Hassfest Validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Hassfest
        uses: home-assistant/actions/hassfest@master
```

#### .github/workflows/release.yaml

```yaml
name: Release

on:
  release:
    types:
      - published

jobs:
  release:
    name: Create release archive
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Create ZIP archive
        run: |
          cd custom_components
          zip -r ../allow2.zip allow2 -x "*/__pycache__/*" -x "*.pyc"

      - name: Upload to release
        uses: softprops/action-gh-release@v1
        with:
          files: allow2.zip
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### For Add-on Distribution (Docker)

Based on [home-assistant/addons-example](https://github.com/home-assistant/addons-example):

#### .github/workflows/builder.yaml

```yaml
name: Builder

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

env:
  BUILD_ARGS: "--test"
  MONITORED_FILES: "build.yaml config.yaml Dockerfile rootfs"

jobs:
  init:
    name: Initialize
    runs-on: ubuntu-latest
    outputs:
      changed_addons: ${{ steps.changed_addons.outputs.addons }}
      changed: ${{ steps.changed_addons.outputs.changed }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Get changed files
        id: changed_files
        uses: jitterbit/get-changed-files@v1

      - name: Find add-ons
        id: addons
        uses: home-assistant/actions/helpers/find-addons@master

      - name: Get changed add-ons
        id: changed_addons
        run: |
          declare -a changed_addons
          for addon in ${{ steps.addons.outputs.addons }}; do
            if [[ "${{ steps.changed_files.outputs.all }}" =~ $addon ]]; then
              for file in ${{ env.MONITORED_FILES }}; do
                if [[ "${{ steps.changed_files.outputs.all }}" =~ $addon/$file ]]; then
                  if [[ ! "${changed_addons[@]}" =~ $addon ]]; then
                    changed_addons+=("\"${addon}\",");
                  fi
                fi
              done
            fi
          done

          changed=$(echo ${changed_addons[@]} | rev | cut -c 2- | rev)

          if [[ -n ${changed} ]]; then
            echo "changed=true" >> $GITHUB_OUTPUT
            echo "addons=[${changed}]" >> $GITHUB_OUTPUT
          else
            echo "changed=false" >> $GITHUB_OUTPUT
          fi

  build:
    name: Build ${{ matrix.arch }} ${{ matrix.addon }}
    needs: init
    runs-on: ubuntu-latest
    if: needs.init.outputs.changed == 'true'
    permissions:
      contents: read
      packages: write
    strategy:
      matrix:
        addon: ${{ fromJson(needs.init.outputs.changed_addons) }}
        arch:
          - aarch64
          - amd64
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Login to GHCR
        if: github.event_name != 'pull_request'
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build add-on
        uses: home-assistant/builder@2025.11.0
        with:
          args: |
            ${{ env.BUILD_ARGS }}
            --${{ matrix.arch }}
            --target /data/${{ matrix.addon }}
            --docker-hub ghcr.io/${{ github.repository_owner }}
```

#### .github/workflows/lint.yaml

```yaml
name: Lint

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main
  schedule:
    - cron: "0 0 * * *"

jobs:
  find:
    name: Find add-ons
    runs-on: ubuntu-latest
    outputs:
      addons: ${{ steps.addons.outputs.addons_list }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Find add-ons
        id: addons
        uses: home-assistant/actions/helpers/find-addons@master

  lint:
    name: Lint ${{ matrix.path }}
    runs-on: ubuntu-latest
    needs: find
    strategy:
      matrix:
        path: ${{ fromJson(needs.find.outputs.addons) }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Lint
        uses: frenck/action-addon-linter@v2.21
        with:
          path: "./${{ matrix.path }}"
```

---

## 6. Container Registry Options

### Option 1: GitHub Container Registry (GHCR) - Recommended

**URL Format:** `ghcr.io/owner/repo-name`

**Advantages:**
- Integrated with GitHub Actions (native authentication via `GITHUB_TOKEN`)
- Free for public repositories
- No separate account needed
- Better integration with GitHub ecosystem
- Supports organization-level permissions

**Setup:**
1. Enable in repository settings: Settings > Actions > General > Workflow permissions
2. Grant "Read and write permissions"
3. Use `ghcr.io/${{ github.repository }}` in workflows

**config.yaml reference:**
```yaml
image: ghcr.io/allow2/allow2homeassistant-{arch}
```

### Option 2: Docker Hub

**URL Format:** `docker.io/owner/repo-name` or `owner/repo-name`

**Advantages:**
- Industry standard
- Larger ecosystem
- Better for distribution outside GitHub

**Disadvantages:**
- Requires separate Docker Hub account
- Rate limits on pulls (100 pulls/6 hours for anonymous)
- Requires storing Docker Hub credentials as secrets

**Setup:**
1. Create Docker Hub account
2. Create repository on Docker Hub
3. Add secrets: `DOCKER_USERNAME`, `DOCKER_PASSWORD`
4. Login in workflow:
   ```yaml
   - uses: docker/login-action@v3
     with:
       username: ${{ secrets.DOCKER_USERNAME }}
       password: ${{ secrets.DOCKER_PASSWORD }}
   ```

### Recommendation

**Use GitHub Container Registry (GHCR)** for Allow2:
- Native GitHub integration
- No additional accounts needed
- Simpler CI/CD setup
- Free for public repos
- Already configured in current workflows

---

## 7. my.home-assistant.io Button Format

### For Add-on Repository

The my.home-assistant.io service allows creating one-click installation buttons.

**Redirect Type:** `supervisor_add_addon_repository`

**URL Format:**
```
https://my.home-assistant.io/redirect/supervisor_add_addon_repository?repository_url=ENCODED_URL
```

**Example:**
```
https://my.home-assistant.io/redirect/supervisor_add_addon_repository?repository_url=https%3A%2F%2Fgithub.com%2FAllow2%2Fallow2homeassistant
```

**Markdown Badge:**
```markdown
[![Add Repository](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository?repository_url=https%3A%2F%2Fgithub.com%2FAllow2%2Fallow2homeassistant)
```

**HTML:**
```html
<a href="https://my.home-assistant.io/redirect/supervisor_add_addon_repository?repository_url=https%3A%2F%2Fgithub.com%2FAllow2%2Fallow2homeassistant">
  <img src="https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg" alt="Add Repository">
</a>
```

### For HACS Integration (Custom Link)

HACS doesn't have an official my.home-assistant.io redirect, but you can link to HACS:

**Manual HACS Installation Instructions:**
```markdown
## Installation via HACS

1. Open HACS in Home Assistant
2. Click the three dots menu (top right)
3. Select "Custom repositories"
4. Add: `https://github.com/Allow2/allow2homeassistant`
5. Category: Integration
6. Click "Add"
7. Search for "Allow2" and install
```

### Other Useful my.home-assistant.io Buttons

**Start Config Flow (after integration is installed):**
```markdown
[![Add Integration](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=allow2)
```

**View Integration:**
```markdown
[![Open Integration](https://my.home-assistant.io/badges/integration.svg)](https://my.home-assistant.io/redirect/integration?domain=allow2)
```

---

## 8. Current Repository Analysis

### Current State

The Allow2 repository currently has a **dual distribution structure** supporting both:
- HACS distribution (via `custom_components/allow2/` and `hacs.json`)
- Add-on distribution (via `config.yaml`, `Dockerfile`, `build.yaml`, etc.)

### Files Analysis

| File | Purpose | Needed for HACS | Needed for Add-on |
|------|---------|-----------------|-------------------|
| `custom_components/allow2/*` | Integration code | Yes | Yes (copied to container) |
| `hacs.json` | HACS configuration | Yes | No |
| `manifest.json` | Integration manifest | Yes | Yes |
| `config.yaml` | Add-on configuration | No | Yes |
| `Dockerfile` | Container definition | No | Yes |
| `build.yaml` | Build configuration | No | Yes |
| `run.sh` | Container entrypoint | No | Yes |
| `repository.yaml` | Add-on repo metadata | No | Yes |
| `.github/workflows/build.yaml` | Docker builds | No | Yes |
| `.github/workflows/release.yaml` | Release assets | Yes | Yes |
| `.github/workflows/lint.yaml` | Code linting | Yes | Yes |
| `.github/workflows/test.yaml` | Testing | Yes | Yes |

### Recommendations for Current Repository

1. **hacs.json Corrections:**
   - Remove `domains` (not a valid HACS field)
   - Remove `iot_class` (only in manifest.json)

   Current:
   ```json
   {
     "name": "Allow2",
     "render_readme": true,
     "domains": ["sensor", "binary_sensor"],
     "country": ["AU", "US", "GB", "NZ", "CA"],
     "homeassistant": "2024.1.0",
     "iot_class": "cloud_polling",
     "zip_release": true,
     "filename": "allow2.zip"
   }
   ```

   Corrected:
   ```json
   {
     "name": "Allow2",
     "render_readme": true,
     "country": ["AU", "US", "GB", "NZ", "CA"],
     "homeassistant": "2024.1.0",
     "zip_release": true,
     "filename": "allow2.zip"
   }
   ```

2. **manifest.json Improvements:**
   - Add `codeowners` with GitHub usernames

   ```json
   {
     "domain": "allow2",
     "name": "Allow2",
     "codeowners": ["@Allow2"],
     ...
   }
   ```

3. **Add HACS Validation Workflow:**
   Create `.github/workflows/hacs.yaml`:
   ```yaml
   name: HACS Validation

   on:
     push:
     pull_request:

   jobs:
     hacs:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
         - uses: hacs/action@main
           with:
             category: integration
   ```

4. **Add GitHub Topics:**
   Add these topics to the repository:
   - `hacs`
   - `home-assistant`
   - `home-assistant-custom-component`
   - `parental-controls`

---

## Summary

### Key Takeaways

1. **HACS is the recommended primary distribution method** for Allow2 because it's a pure custom integration without need for containerization.

2. **The add-on approach can be maintained as secondary** for users preferring Supervisor-managed installations.

3. **GitHub Container Registry (GHCR)** is preferred over Docker Hub for container hosting.

4. **Current repository structure is mostly correct** but needs minor fixes to hacs.json.

5. **Use my.home-assistant.io buttons** in README for easy installation.

### Quick Decision Matrix

| If you want... | Choose... |
|----------------|-----------|
| Maximum user reach | HACS only |
| Simplest maintenance | HACS only |
| Full control over installation | Add-on only |
| Both user bases | Dual distribution |
| To match community standards | HACS only |

### Next Steps

1. Fix `hacs.json` (remove invalid fields)
2. Add HACS validation workflow
3. Add GitHub topics for discoverability
4. Update README with my.home-assistant.io buttons
5. Submit to HACS default repositories (optional, for maximum visibility)
