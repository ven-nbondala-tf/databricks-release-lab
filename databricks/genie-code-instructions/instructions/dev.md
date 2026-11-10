# Workspace instructions: DEV

This is the development workspace. Writing and running code here is expected. Work here is not final, and it reaches TEST and PROD only through a pull request and the CI/CD pipeline.

## What you can do

- Write, edit, refactor and run notebooks, SQL queries, jobs and pipelines.
- Create and change tables and views in the dev catalog.
- Fix errors and run the fixed code to check that it works.
- Add tests, explain code and suggest improvements.

## Team coding conventions

- Use three-level Unity Catalog names (catalog.schema.table). Do not hardcode the catalog or schema in a notebook. Read them from widgets or job parameters.
- Name tables in snake_case with a layer prefix: bronze_, silver_ or gold_.
- Use Delta tables. Use MERGE for upserts. Make jobs safe to run twice.
- Python: add type hints to functions, keep functions small, handle errors on purpose, and use logging instead of print in jobs.
- SQL: one statement per cell, write the column list instead of SELECT *, and add a comment when the reason for a filter is not obvious.
- Never put secrets, tokens or passwords in code. Read them from a secret scope, and never print them.
- Prefer serverless compute unless the task needs a specific cluster setup.
- Put shared logic in files under src/ and keep notebooks short.

## Guardrails

- Work only on DEV objects. Do not point code at TEST or PROD catalogs, schemas, volumes or jobs. If a name looks like TEST or PROD, ask first.
- Before DROP, TRUNCATE, DELETE without a WHERE condition, overwriting a table, VACUUM with a short retention, or deleting files, say exactly what will be affected, using the full object name. Wait for a clear yes before running it.
- Do not change permissions, workspace settings or the workspace instructions file.
- If a request is really a change to production, say so and point the user to the release process instead of working around it.

## Style

- Answer in plain language. Do not use em dashes, en dashes, arrows or emoji. Write the release path as words: DEV, then TEST, then PROD.
