# Databricks AI explained

An overview of the Databricks AI products and how they fit together: Unity Catalog, Unity Gateway, Genie One, Genie Agents, Genie Code, Genie ZeroOps, Agent Bricks and AI Functions. This is an explainer, so the folder holds a fact sheet, diagrams and the article. There is no code to run.

Every claim in the article is listed in the fact sheet with the official page that supports it. The statuses are as of November 2026.

## What is in this folder

| Path | What it holds |
| --- | --- |
| `article.md` | The article draft |
| `notes/facts.md` | The fact sheet: one line per claim, with its source and the page date |
| `notes/availability.md` | Which of these products could be opened in the working workspace, for screenshots |
| `diagrams/ai-architecture.mmd` and `.png` | Unity Catalog, Unity Gateway and the six tools, with the key links |
| `diagrams/ai-which-one-when.html` and `.png` | Which product to use, and when |
| `diagrams/ai-status.html` and `.png` | Release status of each product, with the source date |

The `.mmd` file is Mermaid source. The two `.html` files are the sources of the table images, because Medium has no tables.

## The new names

- Databricks One is now Genie One.
- Databricks Assistant is now Genie Code.
- Genie Spaces is now Genie Agents.
- AI Gateway is now Unity Gateway.

## Official sources

- [What is Unity Catalog](https://docs.databricks.com/aws/en/data-governance/unity-catalog/)
- [Unity Gateway](https://docs.databricks.com/aws/en/unity-gateway/) and [AI governance with Unity Gateway](https://docs.databricks.com/aws/en/ai-gateway/)
- [Unity Gateway release notes](https://docs.databricks.com/aws/en/release-notes/unity-gateway/)
- [Expanding agent governance with Unity Gateway](https://www.databricks.com/blog/ai-gateway-governance-layer-agentic-ai), Databricks blog
- [Genie One](https://docs.databricks.com/aws/en/genie-one/)
- [Genie Agents](https://docs.databricks.com/aws/en/genie-agents/) and [Set up a Genie Agent](https://docs.databricks.com/aws/en/genie-agents/set-up)
- [Genie Agents product page](https://www.databricks.com/product/genie/agents)
- [Genie Code](https://docs.databricks.com/aws/en/genie-code/), [Genie Code CLI](https://docs.databricks.com/aws/en/genie-code/genie-code-cli) and [Genie Code task for jobs](https://docs.databricks.com/aws/en/jobs/tasks/genie-code)
- [Genie ZeroOps](https://docs.databricks.com/aws/en/zeroops/)
- [Develop agents on Databricks](https://docs.databricks.com/aws/en/agents/) and [Agent Bricks CLI](https://docs.databricks.com/aws/en/agents/custom-agents/agent-bricks-cli)
- [AI Functions](https://docs.databricks.com/aws/en/large-language-models/ai-functions)
- [November 2026 release notes](https://docs.databricks.com/aws/en/release-notes/product/2026/november)

## Keeping it current

Statuses change often. Before you reuse the article or the status table, check the release notes and update the source dates in `diagrams/ai-status.html`.
