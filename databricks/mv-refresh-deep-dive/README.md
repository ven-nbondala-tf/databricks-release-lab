# Materialized view refresh deep dive

Work in progress. This folder holds the material for a later article about how streaming tables and materialized views refresh on serverless compute, and how to tell whether a refresh was incremental. Nothing here is finished or written up yet.

What is here:

- `databricks.yml` is the bundle for the test jobs. Each job runs one notebook from `src/`.
- `src/` has a generator that writes order files into a volume, the streaming table and materialized view in SQL and in Python, notebooks that refresh them, and one that reports the refresh history from the event log.
- `sql/` has the setup for the landing volume and a `REFRESH` statement used to test refreshing from a SQL warehouse.
- `diagrams/` has the Mermaid sources for the refresh flow and the refresh audit.
- `tests/results.md` has the test results from the first round, and `tests/screenshots/` the screenshots.

The folder that creates a materialized view from a notebook is `../materialized-view-serverless-notebook`. Its results are a subset of `tests/results.md` here.
