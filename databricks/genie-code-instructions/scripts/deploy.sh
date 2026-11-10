#!/usr/bin/env bash
# Upload one instructions file as the workspace instructions file.
#
# Usage: scripts/deploy.sh instructions/prod.md
#
# Authentication comes from the environment (DATABRICKS_HOST and
# DATABRICKS_TOKEN). The CLI reads them itself.
set -euo pipefail

src="${1:?usage: deploy.sh instructions/<env>.md}"
target="/Workspace/.assistant_workspace_instructions.md"

databricks workspace import "$target" --file "$src" --format AUTO --overwrite

# The file must land as a plain workspace file, not as a notebook.
kind=$(databricks workspace get-status "$target" -o json | jq -r .object_type)
if [ "$kind" != "FILE" ]; then
  echo "Expected object_type FILE at $target but got $kind" >&2
  exit 1
fi

echo "Deployed $src to $target"
