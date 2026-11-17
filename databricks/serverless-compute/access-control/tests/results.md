# Test results

All runs happened on a Databricks Free Edition workspace on November 17, 2026, with Databricks CLI 1.24.0 and the direct deployment engine. The workspace admin ran everything. The service principal `obo-test-sp` was reached through the CLI profile `obo-sp` (OAuth on-behalf-of). Times are UTC. The service principal's application ID is shown as `<application-id>`.

Before any change, the permissions of both default objects were saved to `permissions_before.json`. Both had `users` with Can Use and `admins` with Can Manage, inherited from the parent object.

## Baseline, default permissions

| Test | Result |
| --- | --- |
| `sp_serverless_probe` runs as the service principal on Default Automated Compute | Succeeded in 23 s. The task printed the service principal as the current user and read 500 rows. |
| `SELECT count(*)` as the service principal on the SQL warehouse | Succeeded, 500 rows. |

## Remove the `users` group from Default Automated Compute

The change was made at 05:52:12. `admins` kept Can Manage.

| Time after the change | Test | Result |
| --- | --- | --- |
| 29 s | Probe job as the service principal | Succeeded in 16 s. The restriction had not taken effect yet. |
| 3 min 47 s | Probe job as the service principal | Failed after 1 s. `Run-as user '<application-id>' is not entitled to use serverless compute.` |
| 4 min | One-time serverless run submitted by the service principal | The API accepted it and returned a run ID. The run then failed after 1 s with the same message. |
| 4 min | `SELECT count(*)` as the service principal on the SQL warehouse | Still succeeded, 500 rows. |
| 4 min | A job run by the workspace admin | Succeeded in 16 s. |

The error appears in the run's state message from the Jobs API, in the task output, and on the run page under "Run failed with error message". The run state is `INTERNAL_ERROR` with result `FAILED`.

The restriction took effect somewhere between 29 seconds and 3 minutes 47 seconds after the change. This test did not narrow that window.

## A custom compute object for one identity

| Test | Result |
| --- | --- |
| Permissions of a new custom automated object, as created | The creator has Can Manage, and `admins` has Can Manage, inherited. The `users` group has no access, unlike the two default objects. |
| Grant the service principal Can Use on the custom object | Took effect immediately. The probe ran 16 s later. |
| Probe job pointed at the custom object, run as the service principal | Succeeded in 15 s, 500 rows, while Default Automated Compute still denied the service principal. |
| Deploy the probe job pointed at Default Automated Compute while it was restricted | Rejected by the API at update time with HTTP 403: `Run as user <application-id> cannot use the provided serverless compute (<default object id>): it does not exist, or the run-as user does not have permission to use it.` |

So there are two points where access is checked. A job that names a compute object is rejected when it is saved. A job that names none runs on Default Automated Compute and is rejected when it runs.

## Restore

At 06:02:38 the `users` group was put back with Can Use. Both default objects were then read back and compared with `permissions_before.json`, and both were identical, including which entries are inherited. The job was deployed again against Default Automated Compute and the probe succeeded in 15 s as the service principal.

## Setup problems that are not about serverless

- The first deploy failed because the user creating the job did not have the Service Principal User role on the service principal, even though the user had created it: `Cannot bind the service principal provided in 'run_as' field to the job. The user creating or updating the job must have 'servicePrincipal.user' role on the service principal.` The role is granted through the access control rule sets API, because the Permissions API does not accept service principals. It took about a minute to take effect.
- The first run failed in 1 s because the run as identity could not read the deployed notebook: `Unable to access the notebook ... the identity used to run this job ... lacks the required permissions.` The bundle now gives the service principal view access.
- Setting the permissions of Default Automated Compute with only `admins` left a second, direct entry for `admins` next to the inherited one. Putting back only `users` restored the original state exactly.

## Not covered

- Default Interactive Compute and Databricks Connect were not tested, because serverless Databricks Connect needs a supported Python version (3.12 for current releases), which the test machine did not have.
- The two audit queries from the docs were not run.
- Removing a single user instead of a group, pipelines, and the other features the docs list as not covered, apart from Databricks SQL, were not tested.
- Rate limits are in the sibling folder `rate-limits`.
