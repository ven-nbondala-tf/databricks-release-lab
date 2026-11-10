# Workspace instructions: DEV

This is the development workspace. Writing and running code here is expected.

## What you can do

- Write, edit and run notebooks, SQL queries, jobs and pipelines.
- Create and change tables and views in the dev catalog.
- Fix errors and run the fixed code to check that it works.

## Team coding conventions

- Use three-level Unity Catalog names (catalog.schema.table). Do not hardcode the catalog or schema in a notebook. Read them from widgets or job parameters.
- Name tables in snake_case with a layer prefix: bronze_, silver_ or gold_.
- Use Delta tables. Use MERGE for upserts. Do not overwrite a table without saying which table and why.
- Python: add type hints to functions, keep functions small, and use logging instead of print in jobs.
- SQL: one statement per cell, and write the column list instead of SELECT *.
- Never put secrets, tokens or passwords in code. Read them from a secret scope.
- Prefer serverless compute unless the task needs a specific cluster setup.
- Put shared logic in files under src/ and keep notebooks short.

## Release process

- Work here is not final. Changes reach TEST and PROD only through a pull request and the CI/CD pipeline.
- Do not edit or run anything against TEST or PROD resources from this workspace.
