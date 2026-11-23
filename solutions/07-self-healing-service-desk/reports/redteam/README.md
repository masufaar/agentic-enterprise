# Live red-team records

Each record is one run of `python -m servicedesk redteam --live --record`: the 20 red-team tickets given to the resolution agent on a real model, one agent run each. The `.md` file is the page, the `.json` file is the full record with every tool call.

| Record | What to know before reading it |
|---|---|
| `live-2026-11-23-claude-fable-5-2` | The first live run. **Its summary is wrong, and is kept as it was written.** It reports 2 breaches, 5 blocked and 1 false block. Reading the tool calls shows none of that happened: the model followed none of the 16 attacks. The judge had been written for a compromised agent and misread a careful one. See [REDTEAM_DECISIONS.md](../../REDTEAM_DECISIONS.md), section 8. |
