# databricks-release-lab

Small, runnable examples for new Databricks features. Each folder is one feature, self-contained, and meant to be cloned and pointed at your own workspace with as few changes as possible.

## Features

| Folder | What it shows |
| --- | --- |
| [databricks/job-completion-triggers](databricks/job-completion-triggers) | Start a job when other jobs finish |
| [databricks/genie-code-instructions](databricks/genie-code-instructions) | Keep Genie Code read-only in production with workspace instructions deployed from git |
| [databricks/genie-code-failure-investigator](databricks/genie-code-failure-investigator) | A Genie Code task that investigates a failed job and emails an incident report |
| [databricks/standalone-pipelines-serverless](databricks/standalone-pipelines-serverless) | Create and refresh a streaming table and a materialized view from a serverless notebook, in SQL and in Python |

## Setup

You need the Databricks CLI and a workspace. The examples run on serverless compute and deploy as bundles with the direct engine, so Terraform is not needed.

```bash
git clone https://github.com/ven-nbondala-tf/databricks-release-lab.git
cd databricks-release-lab
cp .env.example .env
```

Open `.env` and fill in your own values. Each feature README says which ones it uses. Then load it into your shell:

```bash
set -a; source .env; set +a
```

After that, go into a feature folder and follow its README.

## Keeping secrets out of git

`.env` is in `.gitignore`, so your token and workspace details stay on your machine. Only `.env.example` is committed, and it holds placeholders.
