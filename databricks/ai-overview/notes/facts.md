# Fact sheet: Databricks AI overview

Checked on November 18, 2026 against official Databricks sources only: docs.databricks.com (AWS pages), learn.microsoft.com/azure/databricks and databricks.com (blog and product pages). One line per claim. Status: CONFIRMED, DIFFERS (the docs say something different from the claim in the brief), or NOT FOUND (no official source found, so it stays out of the article). Page dates are the "Last updated" dates shown on each page.

Base URLs used: U = https://docs.databricks.com/aws/en/

## Renames

| Claim | Status | Source |
| --- | --- | --- |
| Genie Spaces were renamed Genie Agents | CONFIRMED. "Genie Agents were formerly known as Genie Spaces." The product page adds "Genie Agents is the evolution of Genie Spaces. It's the same product with expanded capabilities." No rename date given. | U genie-agents/ (updated Nov 2, 2026); https://www.databricks.com/product/genie/agents |
| Databricks One was renamed Genie One | CONFIRMED (not in the brief). "Genie One was previously known as Databricks One." Old Databricks One documentation URLs (for example /aws/en/databricks-one/) return 404, so there is no redirect to cite. | U genie-one/ (updated Nov 18, 2026) |
| Databricks Assistant was renamed Genie Code | CONFIRMED (by redirect). The old Databricks Assistant docs URLs return HTTP 301 to Genie Code pages: docs.databricks.com/aws/en/notebooks/databricks-assistant-faq goes to /aws/en/genie-code, and /aws/en/notebooks/use-databricks-assistant goes to /aws/en/genie-code/features-capabilities (the older /en/...html URLs redirect the same way). No page states the rename in a sentence, and no date is given. | U notebooks/databricks-assistant-faq (301 to U genie-code); U notebooks/use-databricks-assistant (301 to U genie-code/features-capabilities); checked with curl on November 18, 2026 |
| AI Gateway was renamed Unity Gateway | CONFIRMED. "Unity Gateway is the new name for AI Gateway now that it has become part of Unity Catalog." (FAQ, "What is Unity Gateway, and how does it relate to Unity Catalog?"). Blog post "Expanding agent governance with Unity Gateway", April 15, 2026. The docs page at /ai-gateway/ is titled "AI governance with Unity Gateway" and the release notes say Unity Gateway became generally available on Aug 4, 2026. | https://www.databricks.com/blog/ai-gateway-governance-layer-agentic-ai ; U ai-gateway/ ; U release-notes/unity-gateway/ |

## Unity Catalog

| Claim | Status | Source |
| --- | --- | --- |
| "Unity Catalog is the unified governance layer for data and AI built into Databricks." | CONFIRMED | U data-governance/unity-catalog/ (Sep 11, 2026) |
| It operates beneath every data and AI interaction in a workspace | CONFIRMED. "...operates beneath every data and AI interaction in your workspaces automatically." | same page |
| Unity Gateway is built on Unity Catalog; AI assets are registered as securables with the same privileges as tables | CONFIRMED | U ai-gateway/ |
| Release status of Unity Catalog | NOT FOUND (no label on the page) | |
| It covers data, access control and lineage | CONFIRMED. "Manage who can access what using privileges, attribute-based policies, row and column filters, and workspace bindings." Lineage: "Automatically track how data and AI assets flow and connect, from source data through to models, services, and dashboards." The page says "access control" more often than "permissions". | U data-governance/unity-catalog/ (Sep 11, 2026) |

## Unity Gateway

| Claim | Status | Source |
| --- | --- | --- |
| It checks permissions | CONFIRMED. "Centrally manage access to models, agents, MCP servers, and tools with identity-aware policies and permissions." Unity Catalog grants decide whether a principal can call a service. | U unity-gateway/ (Oct 8, 2026); U data-governance/unity-catalog/service-policies/ (Nov 18, 2026) |
| It enforces rate limits | CONFIRMED. "Enforce consumption limits on model services and MCP services to manage capacity and cost." Exceeding a limit returns HTTP 429. | U ai-gateway/; U ai-gateway/rate-limits (Nov 6, 2026) |
| It tracks budgets | CONFIRMED, with a caveat. Actions: send email, block usage, trigger webhook (Beta). "Block usage thresholds are enforced approximately." "Do not use this feature as a way to ensure an absolute spend cap on final billed amounts." Provisioned throughput is not tracked by budgets. | U ai-gateway/budgets (Nov 13, 2026) |
| It has PII guardrails | CONFIRMED, as Beta. The guardrail is called "Sensitive Data Detection guardrail (Beta)" (Aug 13, 2026). The built-in detector system.ai.detect_sensitive_data "detects structured sensitive data (such as credit card numbers and Social Security numbers)". The overview page also says "Protect sensitive data with PII masking and maintain audit logs of AI activity." | U data-governance/unity-catalog/service-policies/; U release-notes/unity-gateway/; U unity-gateway/ |
| It writes usage logs | CONFIRMED, as system tables. "logs usage data to the system.ai_gateway.usage system table." Records are typically available within one hour. The overview page says "maintain audit logs of AI activity" (exact sentence confirmed on U unity-gateway/, Oct 8, 2026), so "audit logs" may be quoted from that page only. | U ai-gateway/usage-tracking (Nov 13, 2026); U unity-gateway/ |
| It covers models | CONFIRMED. Models hosted by Databricks, or capacity from providers such as OpenAI, Anthropic, Amazon Bedrock and Azure Foundry. | U unity-gateway/ |
| It covers MCP tools | CONFIRMED. Service policies apply to "MCP Services, Model Services, and Model Provider Services". | U unity-gateway/; U service-policies/ |
| It covers coding agents | CONFIRMED. "Use Codex CLI, Claude Code, GitHub Copilot, and ChatGPT desktop with supported open-source models through Unity Gateway." | U ai-gateway/ |
| Service policies cover agents | DIFFERS. The landing page lists agents, but service policies say "Agent Services are not supported." Service policies are Beta. | U data-governance/unity-catalog/service-policies/ |
| How a request flows | PARTLY FOUND. No numbered flow on any page. Stated pieces: Unity Catalog privileges are checked before the request reaches the service; input policies run before the service is invoked; output policies run after it responds; decisions are ALLOW, DENY or ASK. The order of rate limits and budgets relative to policies is not stated. | U data-governance/unity-catalog/service-policies/ |
| Who it is for | NOT FOUND as an explicit audience statement. Closest wording: "the Databricks governance solution for enterprise AI" and "a single control plane for model inference, tools, and skills across your AI applications and coding agents". | U ai-gateway/; U unity-gateway/ |
| Callers: coding agents | CONFIRMED. "Use Codex CLI, Claude Code, GitHub Copilot, and ChatGPT desktop with supported open-source models through Unity Gateway." Usage sources listed: AI Query, coding agents, Databricks Apps, AI Playground and other applications. | U ai-gateway/; U ai-gateway/usage-tracking |
| Callers: custom agents | PARTLY FOUND. "an agent is registered as a Unity Catalog model, and the tools it calls are governed as MCP services, functions, and connections." | U ai-gateway/ |
| Callers: Genie | PARTLY FOUND. No page says Genie sends requests through Unity Gateway in general. What the docs say: the Unity Gateway budgets page lists what budgets cover as pay-per-token usage, AI Functions and Genie ("Genie. See Manage budgets and cost controls for Genie."), and "Genie Code CLI usage is tracked through Unity Gateway." Genie Code has its own Genie budget that account admins manage. | U ai-gateway/budgets (Nov 13, 2026); U genie-code/genie-code-cli (Nov 16, 2026); U genie-code/ |
| Destinations: hosted models, your own provider, MCP tools | CONFIRMED. "frontier proprietary and open-weight models hosted by Databricks"; "bring your existing capacity from providers such as OpenAI, Anthropic, Amazon Bedrock, and Azure Foundry"; "Govern MCP servers registered as Unity Catalog securables, with tool filtering and service policies." | U unity-gateway/; U ai-gateway/ |
| Release status: Unity Gateway | GA. "Unity Gateway is now generally available." (Aug 4, 2026). "Some capabilities, including service policies and agent services, remain in Beta." | U release-notes/unity-gateway/ |
| Release status: API and developer tools; consumer access to query services | GA (Sep 16, 2026; Oct 15, 2026) | U release-notes/unity-gateway/ |
| Release status: service policies; Sensitive Data Detection; Smart Routing; unified trace table; budget webhooks; Skills | Beta (dates Aug to Nov 2026) | U release-notes/unity-gateway/; U service-policies/; U ai-gateway/budgets |
| Release status: base budgets, rate limits, usage tracking | NOT FOUND (no label on the pages) | |
| Release definitions: Beta "Available to most customers", Public Preview "Available to all customers", GA "fully supported and production-ready" | CONFIRMED | U release-notes/release-types (Oct 29, 2026) |

## Genie One

| Claim | Status | Source |
| --- | --- | --- |
| One chat across data, dashboards and apps | CONFIRMED in substance. "Business users who want a single chat interface across data assets, dashboards, and apps should use Genie One." Also: "the simplified Databricks UI for business users, a single entry point for interacting with data and AI". | U genie-agents/; U genie-one/ |
| It routes questions to Genie Agents | CONFIRMED. "Genie One automatically routes questions to the right Genie agent when it needs deeper domain analysis." Also "Genie One answers questions across your data estate and routes to Genie Agents for deep domain analysis." The docs add: "Genie One finds a relevant Genie Agent or data asset, writes and runs the SQL, and cites the sources it used." | https://www.databricks.com/product/genie/agents (FAQ and Related Products); U genie-one/ |
| Who it is for | CONFIRMED. Business users. | U genie-one/ |
| Release status | NOT FOUND for Genie One overall. Sub-features: desktop macOS app GA, Windows app Beta (Nov 11, 2026); Chrome extension Beta (Nov 10); Artifacts (slide decks) Beta. | U genie-one/desktop (Nov 12, 2026); U release-notes/product/2026/november |
| Billing | CONFIRMED. "Genie One and Genie Agents usage by users is free through January 31, 2027." Service principals are excluded from the promotion. | U genie-code/ (Nov 9, 2026) |

## Genie Agents

| Claim | Status | Source |
| --- | --- | --- |
| Up to 50 tables, views or metric views | CONFIRMED. "You can add up to 50 tables, views, or metric views to a Genie Agent." | U genie-agents/set-up (Nov 5, 2026); U agents/mcp-tools/genie-agent (Oct 23, 2026) |
| Files in volumes | CONFIRMED as Public Preview. Volumes have a separate cap: at most 10 volumes per agent and 250 per workspace. | U genie-agents/volumes (Nov 17, 2026) |
| MCP connectors | CONFIRMED as Beta. A workspace admin turns on "MCP tools in Genie Agents" on the Previews page. | U genie-agents/external-tools (Nov 9, 2026) |
| How it works | PARTLY FOUND. Data analysts curate each agent with Unity Catalog datasets, example SQL queries, SQL expressions and text instructions; business users ask questions and get SQL, result tables and visualizations. Setup: Genie Agents in the sidebar, New, choose data sources, Create. | U genie-agents/; U genie-agents/set-up |
| Who it is for | CONFIRMED. Analysts configure; business users query. Described as the no-code option for agents. | U genie-agents/set-up; U getting-started/starter-journey/agents |
| Use from other products | CONFIRMED. The Genie Agent MCP server (Public Preview) lets an agent query one Genie Agent; read-only, no conversation history. Admin turns on Managed MCP Servers. | U agents/mcp-tools/genie-agent |
| Release status of Genie Agents overall | NOT FOUND (no label on the index or set-up page) | |

## Genie Code

| Claim | Status | Source |
| --- | --- | --- |
| What it is | CONFIRMED. "Genie Code is the AI coding and data assistant for developers and technical practitioners in the Databricks workspace." | U genie-code/ (Nov 9, 2026) |
| Where it runs | CONFIRMED. "It runs in notebooks, the SQL editor, the Lakeflow Pipelines Editor, AI/BI dashboards, and MLflow". | U genie-code/ |
| Surfaces | CONFIRMED, spread over pages. Workspace: notebooks, the SQL editor, the Lakeflow Pipelines Editor, AI/BI dashboards and MLflow (overview); jobs and the file editor (features page). The Genie Code CLI is a separate product that runs in a terminal and "has its own tools, skills, and instructions". A Lakeflow Job task is documented separately. | U genie-code/; U genie-code/features-capabilities (Nov 12, 2026); U genie-code/genie-code-cli |
| As a Lakeflow Job task | CONFIRMED. "Use the Genie Code task to run an autonomous agent as part of a job." Jobs UI only: defining a Genie Code task in bundles, the Jobs API or the SDKs is not supported. The page carries no status label. | U jobs/tasks/genie-code (Nov 5, 2026) |
| What it does | CONFIRMED. "Genie Code is an autonomous agent. It plans solutions, retrieves relevant context, runs code, uses cell outputs to improve results". The term "agent mode" is not on the pages read. | U genie-code/ |
| Governance | CONFIRMED. "Genie Code is governed by your Unity Catalog permissions". | U genie-code/ |
| Billing | CONFIRMED. Pay-as-you-go with a per-user free monthly allowance, from July 8, 2026. Admins manage Genie budgets. | U genie-code/ |
| Genie Code CLI | "Genie Code CLI is now generally available" (release note Nov 18, 2026). The CLI page has no status label. It runs locally in a terminal. | U release-notes/product/2026/november; U genie-code/genie-code-cli (Nov 16, 2026) |
| Release status of Genie Code in the workspace | NOT FOUND (no label on the pages) | |

## Genie ZeroOps

| Claim | Status | Source |
| --- | --- | --- |
| It monitors jobs, pipelines and tables | CONFIRMED. "Genie ZeroOps is a background agent that monitors your jobs, pipelines, and tables". It does not monitor models or apps. It detects job and pipeline failures and data quality issues, not performance or cost regressions. | U zeroops/ (Nov 12, 2026) |
| It uses Genie Code | DIFFERS, so the article does not say it. The docs say "Unlike Genie Code, which responds when you prompt it, Genie ZeroOps runs continuously without a prompt" and it is "powered by Anthropic and OpenAI models on Databricks". What the docs do say: you set ZeroOps up and apply its fixes through Genie Code ("ask Genie Code to apply the proposed fix"). | U zeroops/; U zeroops/get-started (Nov 12, 2026) |
| It does not change production without human review | Use the docs' wording: "Genie ZeroOps doesn't change production data or code unless you approve the change." Caveat to include: if you name the repository's default branch, ZeroOps commits the fix directly to that branch, and the change skips pull request review. | U zeroops/ |
| How it works | CONFIRMED. Three steps: Detection, Root cause analysis, Resolution (proposes a fix and links to the source). Setup: choose assets on Jobs & Pipelines, Open ZeroOps; initial backfill covers the previous 24 hours; review an insight; ask Genie Code to apply the fix or do it yourself; for Git-backed jobs, Create PR after you confirm. | U zeroops/; U zeroops/get-started |
| Who it is for | NOT FOUND as an audience statement. It monitors assets where you have OWNER, CAN MANAGE or CAN VIEW permission. | U zeroops/ |
| Release status | CONFIRMED. Beta. A workspace admin turns on Genie ZeroOps from the Previews page. "Genie ZeroOps is now available in Beta." (Nov 12, 2026) | U zeroops/; U release-notes/product/2026/november |

## Agent Bricks

| Claim | Status | Source |
| --- | --- | --- |
| What it is | CONFIRMED. "Agent Bricks is the Databricks agent developer platform." Built for developers who write code, with any framework and any model. | U agents/ (Nov 12, 2026); U agents/concepts/ (Nov 17, 2026) |
| Start from a template with a CLI | CONFIRMED. The Agent Bricks CLI "scaffolds a project from a framework template, runs it locally for testing, and deploys it to the Databricks agent runtime." Commands: agentbricks init, agentbricks dev, agentbricks deploy. Templates: langgraph, openai. | U getting-started/starter-journey/agents (Nov 13, 2026); U agents/custom-agents/agent-bricks-cli (Nov 17, 2026) |
| Models through Unity Gateway | CONFIRMED. "Call models through Unity Gateway with one API, and switch models without changing your code." | U getting-started/starter-journey/agents |
| Genie Agents as tools | CONFIRMED. "A custom agent that you build with Agent Bricks can call Genie Agents as tools." | U getting-started/starter-journey/agents |
| Tools an agent can use | CONFIRMED. "Connect agents to Databricks-managed MCP servers for Genie Agents, AI Search, Unity Catalog functions, and SQL", and to custom and external MCP servers. The CLI page lists "a sandbox, a Databricks-managed MCP service, or a Unity Catalog function" in agent.toml. The pages say "MCP servers and tools", not "MCP tools" alone. | U agents/concepts/ (Nov 17, 2026); U agents/custom-agents/agent-bricks-cli |
| Test locally | CONFIRMED. agentbricks dev "runs the agent locally against Databricks model serving". | U agents/custom-agents/agent-bricks-cli |
| Deploy to the agent runtime | CONFIRMED. "Deploys an agent to the Databricks agent runtime." | U agents/custom-agents/agent-bricks-cli |
| Genie Agents are the no-code option | CONFIRMED. Genie Agents: "Agents that you configure without code". Agent Bricks: "Agents that you write in code, with any framework or harness". | U getting-started/starter-journey/agents |
| Older Agent Bricks products | The legacy page lists Knowledge Assistant, Supervisor Agent and custom multi-agent builders as legacy: "Don't use them for new agents." Use instead: Genie Agents (no code) or the Agent Bricks CLI (code). | U agents/legacy/ (Oct 13, 2026) |
| Release status | The Agent Bricks CLI is Beta. Agent Bricks overall and the agent runtime: NOT FOUND (no label). | U agents/custom-agents/agent-bricks-cli |

## AI Functions

| Claim | Status | Source |
| --- | --- | --- |
| What they are | CONFIRMED. "AI Functions are built-in functions that you can use to apply LLMs or state-of-the-art research techniques on data stored on Databricks for data transformation and analysis." | U large-language-models/ai-functions (Nov 11, 2026) |
| Where they run | CONFIRMED. "They can be run from Databricks SQL, notebooks, Lakeflow pipelines, and Workflows." Not available on classic SQL warehouses. | same page |
| AI on each row from SQL | PARTLY FOUND. The page does not say "every row" for AI Functions in general. Closest wording: "Apply AI models to your data from SQL to classify, extract, summarize, and parse documents." Row wording exists for single items: ai_enrich (Beta) "Generate new columns for each row", and the AI Function job task "runs an AI function on every file in a Unity Catalog volume or every row of a table". | U agents/ (Nov 12, 2026); U large-language-models/ai-functions |
| Who they are for | CONFIRMED. Analysts, and data engineers, data scientists and ML engineers for production batch pipelines. | same page |
| ai_query | CONFIRMED. "ai_query is a general-purpose AI Function that lets you query any supported AI model directly from SQL or Python." Requests to system.ai model services are routed through Unity Gateway. | U large-language-models/ai-query (Nov 17, 2026) |
| AI Functions usage counts in Unity Gateway budgets | CONFIRMED (release note Nov 1, 2026) | U release-notes/product/2026/november |
| Release status | Mixed. Several functions and the asynchronous API are labeled Beta. ai_query, ai_classify, ai_extract and ai_parse_document carry no label on the page, so GA is not confirmed. | U large-language-models/ai-functions |

## Not confirmed, so left out of the article

- The date of any rename.
- A GA, Public Preview or Beta status for Genie One overall, Genie Agents overall, Genie Code in the workspace, the Genie Code Lakeflow Job task, Agent Bricks overall, the agent runtime, Unity Catalog and AI Functions overall.
- Who Unity Gateway and ZeroOps are for, as an explicit statement from the docs.
- The order in which Unity Gateway applies permissions, rate limits, budgets and policies.
- That Genie in general sends requests through Unity Gateway (only Genie budgets and Genie Code CLI usage tracking are documented).
- That AI Functions apply to "every row" as a general statement.

## Where the article differs from the video script

- Genie as a Unity Gateway caller: the article names coding agents, your own agents and Genie Code CLI usage tracking, not Genie as a whole.
- AI Functions "on every row": the article says "apply AI models to your data from SQL".
- Genie Code "as a Lakeflow Job task": confirmed, with the Jobs UI only limit and no status label.
- ZeroOps: "you approve" instead of "human review", plus the default branch caveat; ZeroOps is not described as using Genie Code underneath.
- Unity Catalog "permissions": the docs say "access control" and "privileges".
- Agent Bricks tools: "MCP servers and tools" and Unity Catalog functions, Genie Agents among the managed MCP servers.
