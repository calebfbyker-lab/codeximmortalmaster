#!/usr/bin/env bash
set -euo pipefail

# CodexImmortal dependency stub generator
# Adds minimal requirements.txt / package.json files for apps and packages.

ROOT="${1:-codeximmortal-warlab}"

if [ ! -d "$ROOT" ]; then
  echo "[CodexImmortal] Root $ROOT does not exist. Run setup.sh first." >&2
  exit 1
fi

cd "$ROOT"

echo "[CodexImmortal] Generating dependency stubs in $(pwd)" 

mkfile() {
  local path="$1"
  local dir
  dir="$(dirname "$path")"
  mkdir -p "$dir"
  if [ ! -f "$path" ]; then
    cat > "$path" << 'EOF'
# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# Placeholder dependency file. Fill with exact versions per module.
EOF
  fi
}

# Python package requirements
for pkg in shared-core pqc-utils storage-mesh neural-fabric nft-attestation playbook-engine osint-fusion integration; do
  mkfile "packages/${pkg}/requirements.txt"
  mkfile "packages/${pkg}/pyproject.toml"
done

# App service requirements
for app in sentinel-api strategist-graph archivist-memory executor-orchestrator threat-board-api; do
  mkfile "apps/${app}/requirements.txt"
done

# Dashboard frontend package.json
if [ ! -f "apps/dashboard/package.json" ]; then
  cat > apps/dashboard/package.json << 'EOF'
{
  "name": "codeximmortal-dashboard",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "typescript": "^5.0.0",
    "@types/react": "^18.0.0",
    "@types/react-dom": "^18.0.0",
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  }
}
EOF
fi

# Root-level Python monorepo requirements
mkfile requirements.txt
mkfile pyproject.toml

# Root-level Node tooling (optional)
mkfile package.json

cat << EOF
[CodexImmortal] Dependency stubs created.
Review and pin exact versions per module before production use.
EOF