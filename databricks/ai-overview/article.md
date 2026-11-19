# Databricks AI Explained: Genie, Unity Gateway, Agent Bricks

Subtitle: Databricks AI explained: what Genie One, Genie Agents, Genie Code, ZeroOps, Unity Gateway and Agent Bricks do, and when to use each.

Databricks AI now has many new names, and older articles still use the old ones. Genie One, Genie Agents, Genie Code, Genie ZeroOps, Unity Gateway, Agent Bricks and AI Functions all work on top of Unity Catalog, and it is hard to tell what each one does or who it is for. This guide explains each product in the same four parts, shows how they connect, and ends with a table that tells you which one to use and when. The fact sheet and diagrams for this guide are on GitHub: [ai-overview](https://github.com/ven-nbondala-tf/databricks-release-lab/tree/main/databricks/ai-overview).

[VIDEO: https://youtu.be/aMSk4GJJdaU]
Caption: A three-minute visual tour of how the pieces fit together.

## The new names

Four products changed names. Old documentation links for the first two now open the new pages.

- Databricks One is now Genie One.
- Databricks Assistant is now Genie Code. Old Databricks Assistant documentation links open the Genie Code pages.
- Genie Spaces is now Genie Agents.
- AI Gateway is now Unity Gateway, because it became part of Unity Catalog.

## The big picture

The products sit in three layers. At the bottom, Unity Catalog governs data and AI assets: who can access what, and how assets connect through lineage. Above it, Unity Gateway governs the calls that AI makes to models, MCP servers and tools. On top are the six tools you work with: Genie One, Genie Agents, Genie Code, Genie ZeroOps, Agent Bricks and AI Functions.

[image: ai-architecture.png | Caption: Unity Catalog at the bottom, Unity Gateway in the middle and six tools on top. | Alt: A diagram with three layers. Six tools on top: Genie ZeroOps is set up and fixed through Genie Code, Genie One routes questions to Genie Agents, and Agent Bricks calls Genie Agents as tools. A dashed arrow labeled model and tool calls leads to Unity Gateway, which checks permissions, rate limits and budgets, PII guardrails and usage logs. An arrow leads from Unity Gateway to Unity Catalog, which covers data, access control and lineage.]

The dashed arrow shows that model and tool calls are governed at the gateway. The documentation describes this for agents built with Agent Bricks, for AI Functions, and for coding agents, and Genie usage counts toward Unity Gateway budgets.

## Unity Catalog

**What it is.** Unity Catalog is the unified governance layer for data and AI built into Databricks. It operates beneath every data and AI interaction in a workspace.

**Who it is for.** Teams that govern data and AI assets.

**How it works.**
1. You register data and AI assets, such as tables, volumes and models, in catalogs.
2. You control access with privileges, attribute-based policies, and row and column filters.
3. Unity Catalog tracks lineage from source data through to models, services and dashboards.

**Use it when.** You need one place to manage access and lineage for both data and AI assets. The other products in this guide work inside its permissions.

## Unity Gateway

**What it is.** Unity Gateway is the Databricks governance solution for enterprise AI, and it is part of Unity Catalog. It is the control point for the models, MCP servers, tools and coding agents that your organization uses.

**Who it is for.** Teams that govern AI cost, security and access.

**How it works.**
1. Callers send requests through it: agents you build, coding agents such as Claude Code and Codex CLI, and AI Functions.
2. Four controls apply. Permissions decide who can call a service. Rate limits and budgets cap use, and budgets can send an email, block usage or trigger a webhook (Beta). Guardrails such as the Sensitive Data Detection guardrail (Beta) detect structured sensitive data, for example card numbers. Usage is written to the system.ai_gateway.usage system table.
3. Requests reach their destination: a Databricks-hosted model, a model from your own provider such as OpenAI or Anthropic, or an MCP server.

**Use it when.** You want one place to govern which models and tools people and agents can use, how much they use, and what is logged. Budget blocks are enforced approximately, so do not treat them as an exact cap on the final bill.

## Genie One

**What it is.** Genie One is the simplified Databricks UI for business users, a single entry point for interacting with data and AI. It was previously known as Databricks One.

**Who it is for.** Business users.

**How it works.**
1. You ask a question in plain language in one chat that spans data, dashboards and apps.
2. Genie One finds a relevant Genie Agent or data asset. When a question needs deeper domain analysis, it routes the question to the right Genie Agent, for example a sales agent.
3. The agent writes and runs the SQL.
4. You get the answer as SQL, a results table and a chart, and the sources are cited.

**Use it when.** Business users need answers from data without writing SQL. Usage of Genie One and Genie Agents by users is free through January 31, 2027.

## Genie Agents

**What it is.** A Genie Agent answers questions about a defined set of your data, with no code. It was formerly known as Genie Spaces.

**Who it is for.** Analysts set up each agent, and business users ask it questions in the chat.

**How it works.**
1. Open Genie Agents in the sidebar and click New.
2. Choose the data sources: up to 50 tables, views or metric views.
3. Add example SQL queries and text instructions, so the agent understands your business terms.
4. Optionally add files in volumes (Public Preview) and MCP connectors (Beta).
5. Share the agent. Users get back SQL queries, results tables and visualizations.

**Use it when.** You want a trusted agent for one domain, such as sales, and you do not want to write code. If you need to write agent code, use Agent Bricks.

## Genie Code

**What it is.** Genie Code is the AI coding and data assistant for developers and technical practitioners in the Databricks workspace. It is an autonomous agent that plans solutions, retrieves context, runs code and uses the output to improve its results.

**Who it is for.** Developers and technical practitioners.

**How it works.**
1. You ask for a task, such as a pipeline or a dashboard.
2. It reads context from your workspace and your data, within your Unity Catalog permissions.
3. It builds the code.
4. It runs the code and fixes problems using the output.
5. You review the result.

Genie Code is available in the workspace, as the Genie Code CLI in your terminal (generally available), and as a task in a Lakeflow Job. The job task is set up in the Jobs UI only.

**Use it when.** You want help writing, running and fixing code, in the workspace, in a terminal or as a step in a job.

## Genie ZeroOps

**What it is.** Genie ZeroOps is a background agent that monitors your jobs, pipelines and tables. It runs continuously without a prompt, and it is in Beta.

**Who it is for.** Data teams that own jobs, pipelines and tables. It monitors the assets where you have OWNER, CAN MANAGE or CAN VIEW permission.

**How it works.**
1. A workspace admin turns on Genie ZeroOps from the Previews page. You choose the assets to watch on the Jobs & Pipelines page.
2. ZeroOps watches them and detects job and pipeline failures and data quality issues. It does not detect performance or cost regressions.
3. It investigates and finds the root cause.
4. It proposes a fix. For jobs backed by Git, you can create a pull request after you confirm.
5. You approve. Genie ZeroOps does not change production data or code unless you approve the change.

You set up ZeroOps and apply its fixes through Genie Code.

**Good to know.** If you name your repository's default branch, Genie ZeroOps commits the fix directly to that branch, and the change skips pull request review.

**Use it when.** You want failures and data quality issues investigated for you, with a fix that you review.

## Agent Bricks

**What it is.** Agent Bricks is the Databricks agent developer platform, for building and deploying agents. It is built for developers who write code, with any framework and any model.

**Who it is for.** Developers who write code.

**How it works.**
1. Start a project from a template with the Agent Bricks CLI, which is in Beta. The templates use LangGraph or OpenAI.
2. Connect models through Unity Gateway with one API, and switch models without changing your code.
3. Add tools: Genie Agents, MCP servers and tools, and Unity Catalog functions.
4. Test the agent locally.
5. Deploy it to the Databricks agent runtime, with the tools and permissions the agent needs.

**Use it when.** You want to write your own agent in code. For an agent without code, use Genie Agents. The older Knowledge Assistant and Supervisor Agent are legacy, and the documentation says not to use them for new agents.

## AI Functions

**What it is.** AI Functions are built-in functions that apply AI models to data stored on Databricks. You can run them from Databricks SQL, notebooks, Lakeflow pipelines and Workflows.

**Who it is for.** Analysts and data engineers.

**How it works.**
1. You write a SQL query that calls an AI Function: the general-purpose ai_query, or a task-specific function such as ai_classify, ai_extract or ai_parse_document.
2. The function runs on Databricks. Requests from ai_query to system.ai model services are routed through Unity Gateway.
3. The results come back in your query like any other values, ready for the next step.
4. Usage counts toward Unity Gateway budgets.

**Use it when.** You want to apply AI models to the data in a table from SQL, for example to classify, extract or summarize. AI Functions are not available on classic SQL warehouses.

## How they connect

Four links tie the products together.

1. Genie One routes to Genie Agents. When a question needs deeper domain analysis, Genie One routes it to the right Genie Agent.
2. Genie ZeroOps and Genie Code work together. You set up ZeroOps in a Genie Code chat and ask Genie Code to apply the fix. ZeroOps runs without a prompt, and Genie Code responds when you prompt it.
3. Agent Bricks calls Genie Agents as tools. A custom agent can call a Genie Agent, so code you write can reuse an agent you configured without code.
4. Unity Gateway governs the calls to models and tools, and Unity Catalog governs the data and AI assets underneath.

## Which one when

[image: ai-which-one-when.png | Caption: Which product to use, and when. | Alt: A table with three columns: product, who it is for, and use it when. It has one row for each of Unity Catalog, Unity Gateway, Genie One, Genie Agents, Genie Code, Genie ZeroOps, Agent Bricks and AI Functions.]

The same table as a list:

- Unity Catalog: you need one place for access control and lineage across data and AI assets.
- Unity Gateway: you want one control point for the models, MCP servers and coding agents your organization uses.
- Genie One: business users want one chat to ask questions across data, dashboards and apps.
- Genie Agents: you want a no-code agent over a defined set of tables for one domain.
- Genie Code: you want help writing code and building pipelines and dashboards, in the workspace, a terminal or a job.
- Genie ZeroOps: you want failures and data quality issues investigated, with a proposed fix you approve.
- Agent Bricks: you build and deploy your own agent with any framework and any model.
- AI Functions: you want to apply AI models to your data from SQL.

## What you can use today

These are the statuses the documentation gives, as of November 2026. Products that are not listed carry no status label in the documentation. Check the release notes before you plan, because statuses change.

[image: ai-status.png | Caption: Release status as of November 2026. | Alt: A table with three columns: product, status, and source date. Unity Gateway and the Genie Code CLI are generally available. Genie ZeroOps, MCP connectors in Genie Agents, the Agent Bricks CLI and the PII guardrail in Unity Gateway are in Beta. Files in Genie Agents are in Public Preview.]

## Summary

Databricks AI is easier to follow once you see the three layers: Unity Catalog governs data and AI assets, Unity Gateway governs the calls AI makes, and six tools sit on top. Genie One, Genie Agents and Genie ZeroOps work without code, Genie Code helps developers, Agent Bricks builds code agents, and AI Functions bring AI into SQL. Start with who will use the product, check its status, and keep Unity Catalog permissions as the foundation.

Which of these products would change your own work first?

## References

- [What is Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/), Databricks documentation
- [Unity Gateway](https://docs.databricks.com/aws/en/unity-gateway/), Databricks documentation
- [AI governance with Unity Gateway](https://docs.databricks.com/aws/en/ai-gateway/), Databricks documentation
- [Unity Gateway release notes](https://docs.databricks.com/aws/en/release-notes/unity-gateway/), Databricks documentation
- [Expanding agent governance with Unity Gateway](https://www.databricks.com/blog/ai-gateway-governance-layer-agentic-ai), Databricks blog
- [Genie One](https://docs.databricks.com/aws/en/genie-one/), Databricks documentation
- [Genie Agents](https://docs.databricks.com/aws/en/genie-agents/), Databricks documentation
- [Set up a Genie Agent](https://docs.databricks.com/aws/en/genie-agents/set-up), Databricks documentation
- [Genie Agents product page](https://www.databricks.com/product/genie/agents), Databricks
- [Genie Code](https://docs.databricks.com/aws/en/genie-code/), Databricks documentation
- [Genie Code CLI](https://docs.databricks.com/aws/en/genie-code/genie-code-cli), Databricks documentation
- [Genie Code task for jobs](https://docs.databricks.com/aws/en/jobs/tasks/genie-code), Databricks documentation
- [Genie ZeroOps](https://docs.databricks.com/aws/en/zeroops/), Databricks documentation
- [Develop agents on Databricks](https://docs.databricks.com/aws/en/agents/), Databricks documentation
- [Agent Bricks CLI](https://docs.databricks.com/aws/en/agents/custom-agents/agent-bricks-cli), Databricks documentation
- [AI Functions](https://docs.databricks.com/aws/en/large-language-models/ai-functions), Databricks documentation
- [November 2026 release notes](https://docs.databricks.com/aws/en/release-notes/product/2026/november), Databricks documentation

## Medium settings

- SEO title: Databricks AI Explained: Genie, Unity Gateway, Agent Bricks
- SEO description: same as the subtitle
- Slug: databricks-ai-explained-genie-unity-gateway-agent-bricks
- Tags: Databricks, Data Engineering, Generative Ai, Unity Catalog, Ai Agents
