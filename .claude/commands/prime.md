# Prime

> Read the context files and summarize your understanding of this workspace.

## Read

./context
- `HISTORY.md` — Workspace changelog (what was built, when, by whom)
- `docs/_index.md` — Documentation routing index (agents find relevant docs here)
- `context/group/key-metrics.md` — Current business metrics (auto-generated from database)

## On-Demand Loading

These files are NOT read during /prime but should be loaded when a task requires deep detail:

- `reference/data-access.md` — Full table schemas, SQL query examples, collection scripts

## Summary

After reading, provide:

1. A brief summary of who I am, what this workspace is for and what your role is
2. Your understanding of the workspace structure and the purpose of each section/file
3. What commands are available
4. A summary of my/our current strategies and priorities
5. **Data status** — Review key-metrics.md data freshness. Flag anything stale (>2 days old). Note that you can run live SQL queries against `data/data.db` for deeper analysis.
6. Confirmation you're ready to help me with pursuing these goals through use of this workspace
