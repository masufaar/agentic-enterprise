# Build log: OT/IT Convergence Sentinel

A running record of what was done, why, how, and what it cost. Newest session at the bottom.

## How to read the token figures

- **Measured** figures come from the tool that ran the step.
- **Estimated** figures are file size divided by four (a common rule of thumb for English text and code). They cover the text that was written or read, not the reasoning behind it.
- The main model cannot read its own token meter from inside the session. The session total has to be taken from the usage screen, not from this file.

## Session 1, 16 November 2026

Goal given by M: start the next solution after the Control Tower was paused as version 0. M chose solution 02 and asked that it be state of the art, with at least four agents, and that it must not draw the board reply "we already have AI network management tools".

### Decisions

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D1 | Solution 02 before solution 10 (AI Value Ledger). | M's choice. The ledger would have had almost nothing to account for: no language model runs in the repository, so measured cost is zero. The published roadmap also puts a business solution first. | A thin ledger slice first, so that solution 02 reports into it from its first run. Still possible later. |
| D2 | Position the solution as a decision layer above the security and network tools a company already owns, not as another monitoring tool. | Checked on 16 November 2026: plant-floor security vendors and network vendors already ship agents that collect, correlate, diagnose and remediate. A synthetic-data repository cannot beat them at that job, and copying it invites the objection M wants to avoid. | Four agents that mirror the observability steps (collect, correlate, visualise, remediate). |
| D3 | The three things the solution adds: it prices every response in lost output; every action passes rules set by the board, whichever vendor's tool is underneath; it writes for the crisis team, not the analyst. | These need the production schedule and the governance layer, which sit outside a security vendor's product. | Competing on detection quality. |
| D4 | Four agents: collection, correlation, impact and response, briefing. | M asked for at least four. The roles follow M's four steps, re-cut so that the third prices responses and the fourth serves the crisis team. | Two agents on the two existing registry cards (my first proposal, withdrawn). |
| D5 | Two new cards in the Control Tower registry (correlation, briefing). The existing discovery card serves the collection agent. | No agent runs unregistered. Consequence: the Control Tower figures move from 16 to 18 registered agents, and its reports, tests and the board deck must follow. | Running correlation inside the response agent to leave the published figures untouched. |
| D6 | First slice: one scripted incident at one plant, fixed rules, no language model, simulated tools. Plain Python, standard library only. | Same reasons as solution 01: repeatable, measurable, readable in one sitting, zero running cost. "State of the art" is claimed for the design, never for this slice. | A model-driven investigation. Later step. |
| D7 | The two alert feeds use different field names on purpose. | The collection agent has a real job only if the sources disagree in format, as tools from different vendors do. | One tidy common feed. |
| D8 | Noise is included: 5 of the 13 alerts have nothing to do with the incident. | A correlation that is handed only relevant alerts proves nothing. | Only the eight incident alerts. |
| D9 | Line C is in planned maintenance when the incident happens. | It makes the production schedule matter: the same isolation costs a different amount depending on the hour. This is the point of the solution. | All lines running. |
| D10 | Every euro figure is calculated from stated assumptions and labelled so. The EUR 15,000 per stopped line-hour comes from the company profile. | Repository rule: measured or labelled as an assumption. | Different values per line, which would add assumptions without adding insight. |
| D11 | People appear by role or by a numbered account only. | Synthetic data rule, as in solution 01. | Invented names. |

| D12 | **Withdrawn by M on 17 November 2026, see D22.** Line A is a casting line: any unplanned stop costs 12 further hours before good output returns (assumption). | M's plant experience: some machines, casting for example, cannot be stopped without large cost and long waiting. It makes the "disconnect everything" reflex visibly expensive. | Treating all lines alike. |
| D13 | Each isolation point has its own hold time (cell 8 h, office link 4 h, whole plant floor 8 h; assumptions). | Closing the office link is only needed until the gateway is cleaned, which is shorter than the 6 hours of orders already loaded. So that step costs no output, which is what a plant would expect. | One hold time for all, which made closing the link cost output for no reason. |
| D14 | The existing discovery card was renamed "Plant Asset and Alert Collector", its purpose extended and one tool added (`security.alerts.read`). Its id is unchanged. | A registry card must describe what the agent does. Keeping the id keeps the Control Tower's attack list valid. | A card whose purpose no longer matched the agent, or a fifth card. |
| D15 | The response agent got two read tools (`incident.read`, `production.read`). It writes no report itself. | It is classified high-risk, so the Control Tower lets it read on its own and nothing else. The briefing agent, classified limited, writes the page. Found while building: my first design had the response agent write the report, which the gateway would have held. | Loosening the rule for this agent. |
| D16 | The recommendation rule: the cheapest response that leaves no production line within the intruder's reach. | One sentence a board member can repeat and challenge. | A weighted score of cost and risk, which would hide a probability nobody has measured. |
| D17 | Unrelated alerts are listed on the page. | Nothing is dropped silently; the crisis team can see what was set aside. | Showing only the incident. |

### Not verified, stated openly

- I did not find a vendor product that prices containment options in lost output during an incident. That is not proof that none exists. Public texts must say "we did not find", never "nobody does".
- The regulator notification (NIS2) is out of this slice. Its legal deadlines must be checked against the legal text before anything is written.

### Steps and cost

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Read the latest handover | Project document | Main (Fable 5.2) | Input, about 1,300 estimated |
| 2 | Cloned the repository at 22db85c; read the designs of solutions 02 and 10, the architecture, company profile, roadmap, registry cards and gateway interface | git, read-only | Main | Input, about 9,000 estimated |
| 3 | Checked what commercial tools already do | Three web searches | Main | Input, about 12,000 estimated |
| 4 | Wrote the synthetic data: plant, production, two alert feeds (`data/`) | Written directly, validated by loading | Main | About 1,900 estimated output |
| 5 | Wrote this log | Written directly | Main | About 1,300 estimated output |

| 6 | Read the gateway, registry, classifier, approvals and tests of the Control Tower | Read-only | Main | Input, about 9,500 estimated |
| 7 | Casting assumption, hold times; two new registry cards, two cards extended; four count checks in the Control Tower tests moved from 16 to 18 | Script, then test run | Main | About 900 estimated output |
| 8 | Four agents, workflow and command line (`sentinel/`, 510 lines) | Written directly | Main | About 5,600 estimated output |
| 9 | Tests (`tests/test_sentinel.py`, 25 tests) | Written directly | Main | About 2,700 estimated output |
| 10 | Ran the incident and both test suites | Shell | Main | Small |
| 11 | Regenerated the Control Tower reports from a clean state (inventory, campaign, board page) so they show 18 agents | Its own commands | Main | Small |
| 12 | Rewrote this solution's README and business case; updated the main README, the roadmap and one line of the Control Tower README | Written directly | Main | About 2,900 estimated output |
| 13 | Push to GitHub and browser check of two pages | git, built-in browser | Main | Small |
| 14 | Board deck: generator edited (slides 5, 6, 9, 16, 18, 19, 29, 31 and their notes), two overflows fixed, PowerPoint rebuilt and rendered for a visual check | Deck build scripts | Main | About 2,300 estimated output; input about 20,000 for reading the generator |

### Measured results, session 1

- 25 of 25 tests pass in this solution; 77 of 77 still pass in the Control Tower.
- 13 alerts collected from two tools; 8 joined into one incident; 5 set aside.
- 5 responses priced. Recommended: disconnect Line B cell 2 and close the office link, EUR 120,000. Whole plant floor: EUR 465,500. Both figures are calculated from assumptions, not measured losses.
- 13 gateway decisions for one run: 11 allowed, 2 held for the Head of OT Security. Audit record intact.
- Registry: 18 agents (was 16).

### Corrections to what I told M earlier

- My hand estimate before coding was about EUR 150,000 against EUR 285,000. The code gives EUR 120,000 against EUR 465,500. The difference comes from D12 and D13, both added after the estimate.
- I had said rule P-002 would refuse a write to a controller. The gateway refuses it one step earlier (PERM-1: the tool is not on the agent's permission list). P-002 stays as the second barrier.

### Decisions on the public texts

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D18 | Status word for this solution: "In build", with "a first slice is working". | Same wording as the Control Tower. "Working" alone would overstate one scripted incident. | "Working". |
| D19 | The README answers the objection "we already have AI network management tools" under its own heading. | It is the first thing a board member will say. | Leaving the positioning implicit. |
| D20 | The business case keeps its two original levers as assumptions and adds the slice result as an illustration, explicitly not as evidence. | The EUR 345,500 difference comes from assumptions about one invented incident. | Replacing the lever with the slice figure. |
| D21 | The roadmap now lists the Sentinel first under "In build" and the Control Tower as paused at version 0. | M's decision of 16 November. | Leaving the Control Tower's list as the only one. |

### Open after this session

- Pushed on M's go as commit 9f60412 (main). The solution page and the front page were checked in a browser after the push; the roadmap, the business case and the regenerated Control Tower reports were not looked at rendered.
- Board deck (local only, not in the repository) updated after the push: 8 of 31 slides changed, PowerPoint rebuilt with 31 notes, no slide over its limit. Not opened in Microsoft PowerPoint itself.
- This entry was corrected after the push, so the published copy of this log still says "Nothing is pushed" until the next push.
- Campaign figures of the Control Tower are unchanged (29 attacks, 28 contained, 1 open breach); only the agent counts moved.

### Lighter model

The synthetic data and this log could have been written by a lighter model with an exact brief. They were small enough that briefing and checking would have cost more than writing them.

## Session 2, 17 November 2026: the casting assumption is withdrawn

M's instruction: there is no casting at Halden Industrial, only direct manufacturing. Forget the 12 hours for restarting a casting line.

### Decision

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D22 | D12 is withdrawn. Line A is a normal line: no further hours after a stop. The name "Line A (casting)" becomes "Line A". The pricing code keeps its optional "further hours after a stop" per line, unused by the data and covered by one test. | The company profile is M's to set, and the 12 hours was my figure, never confirmed by him. Keeping the mechanism costs nothing and a later scenario may need it. | Replacing casting with another slow-to-restart process to keep the larger difference: that would be choosing an assumption for the size of the result. |

### What changed

- `data/production.json`: the name, the 12 hours and their basis removed from Line A.
- `tests/test_sentinel.py`: six expected figures changed; one check added inside an existing test so the unused mechanism stays tested. Still 25 tests.
- `README.md`, `BUSINESS_CASE.md`: figures and the sentence that named casting as a driver.
- `reports/incident-latest.md`: regenerated by `python -m sentinel run`.
- Session 1 above is left as written. Where it says EUR 465,500, EUR 345,500 or EUR 2,340,000, the figures below replace them.

### Measured results, session 2

- 25 of 25 tests pass in this solution; 77 of 77 in the Control Tower.
- Recommended response: EUR 120,000 (unchanged). Whole plant floor: EUR 285,500 (was 465,500). Difference: EUR 165,500 (was 345,500). At stake if all three lines are encrypted: EUR 2,160,000 (was 2,340,000). All calculated from assumptions, not measured losses.
- The recommendation itself did not change. Alerts, incident and gateway decisions are unchanged: 13 alerts, 8 joined, 5 set aside; 11 allowed, 2 held.
- The difference is now close to my hand estimate of session 1 (about EUR 285,000 for the whole plant floor), which was made before D12.

### Steps

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Read the latest handover | Project document | Main (Fable 5.2) | Input, about 2,300 estimated |
| 2 | Cloned the repository at 9f60412; searched every file for the casting assumption; dry run in a scratch copy | git, search, test run | Main | Input, about 5,000 estimated |
| 3 | Changed data, tests, README and business case in the Desktop folder; regenerated the incident page in a scratch copy so the Control Tower state folder stays clean | Script on M's computer | Main | About 1,500 estimated output |
| 4 | Ran both test suites on the changed files | Workspace copy | Main | Small |
| 5 | Push to GitHub and browser check of the solution page | git, built-in browser | Main | Small |
| 6 | Board deck: slide 19 and its note changed in the generator, the slide file, the speaker notes, the browser file and the PowerPoint | Script on M's computer | Main | About 600 estimated output; input about 6,000 for reading the notes |
| 7 | Ran the incident again in a scratch copy to answer M's questions on data, rule, pricing and escalation, including both release attempts | Command line | Main | Input, about 9,000 estimated for reading code and data |
| 8 | Board deck: new Backup section, first two slides, then on M's request four slides in plain language for non-technical board members; PowerPoint rebuilt from the generator (35 slides) | Deck build scripts | Main | About 9,000 estimated output |

### Open after session 2

- Pushed to main on M's go on 17 November 2026, as the commit that follows 9f60412. This push also publishes the correction to session 1 noted above.
- Published as commit 1053dc9; the solution page was checked in a browser after the push. The business case, the incident page and this log were not looked at rendered.
- Board deck (local only) updated after the push: slide 19 and its note now carry EUR 285,500 and no longer mention casting. The PowerPoint was patched in place, not rebuilt, and rendered once for a visual check of slide 19. Not opened in Microsoft PowerPoint itself.
- Board deck (local only): a Backup section of four slides explains one incident run in plain language (the steps, the intruder's path, the price of each response, who decides and what is not built). M's instruction: backup slides must be detailed and simple enough for non-technical board members. 35 slides, 35 notes. Rendered once for a visual check; not opened in Microsoft PowerPoint itself.
- Stated to M and on the slides as not built: a deputy or time limit when the approver does not answer; recognition of an intruder slower than one hour per step or changing accounts; any probability of spread.
- This entry was written after the push, so the published copy still says the deck is not updated until the next push.

### Lighter model

All of session 2 is small data and wording work that a lighter model could have done with an exact brief.

## Session 3, 18 November 2026: the solution is redefined as agentic; public pages rewritten

Nothing in the code changed in this session. The pages changed.

### Why

On 17 November M stated the principle the whole project rests on: an agent is a language model working in a loop inside a harness, which evaluates, corrects and adapts; anything else is traditional software. Measured against it, sessions 1 and 2 built no agent. The four "agents" of this solution are fixed code. I had kept the word, which was wrong; the cause is recorded in the project's review of 17 November (a limit of my workspace was turned into a product decision without asking M).

### Decisions

| # | Decision | Why | Alternative set aside |
|---|---|---|---|
| D23 | The word agent is used only for a model in a loop with tools. The four steps of the first version are called fixed code or tools. | M's principle. | Keeping "agent" with a footnote. |
| D24 | Position: "It runs the decision, not the detection, in addition to your existing tools." | Research on 18 November found that joining office and plant alarms with AI agents is a shipped commercial capability, so it is not where this solution adds anything. | Competing on detection or investigation. |
| D25 | The offer has three stages: prepare, rehearse, decide. | Agreed with M while drafting the LinkedIn article, which is written before the build and serves as its specification. | A live incident tool only. |
| D26 | Reversible office-side steps are taken by the agents at once; everything touching the plant floor is decided by a named person. | It makes "act at once" true without an agent disconnecting production. | Recommend-only agents. |
| D27 | The business case loses the lever "analyst time saved" (EUR 180,000). | It is a benefit of detection tools, which the solution no longer claims. The yearly value falls from EUR 980,000 to EUR 800,000, both assumptions. | Keeping a figure that contradicts the position. |
| D28 | The collection and joining steps of the first version stay as a basic module for companies without such tools. | Not every company has them. | Deleting them. |
| D29 | The solution page lists ten things that must exist before the status becomes "Working". | The article commits the build; the list makes the commitment checkable. | An open-ended roadmap. |

### Steps

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Review of all work against M's principle; two external toolkits read | Project documents, web | Main (Fable 5.2) | Input about 30,000, output about 6,000, estimated |
| 2 | Project charter written with M (three versions) | Project documents | Main | Output about 5,000 estimated |
| 3 | Research brief for this solution: five searches, three pages read | Web | Main | Input about 25,000, output about 2,500, estimated |
| 4 | LinkedIn article, four drafts, kept as documents outside the repository | Written directly | Main | Output about 9,000 estimated |
| 5 | Solution page, business case, front page row and roadmap rewritten to match draft 4 of the article | Written directly | Main | Output about 4,500 estimated |

### State after session 3

- 25 of 25 tests still pass; the code is unchanged.
- Model involved: no. Agents: designed.
- The board deck (local only) still describes the first version as four agents and gives EUR 980,000 for this solution. It is to be rewritten after the build.

### Lighter model

The page rewrite could go to a lighter model once the article text is fixed. The review and the article drafts could not.


## Session 4, 18 November 2026: the build of the agents starts; the model connector

Documents read at the start: project charter (version 3), project handover of 18 November, handover for this solution of 18 November.

### Why

The handover sets the order of the build. Its first step: check the current Claude API documentation before writing the model connector, and do not build it from memory.

### Decisions

| No. | Decision | Why | Alternative set aside |
|---|---|---|---|
| D30 | One neutral format between the agents and any model: `ask(system, turns, tools)` returns text, tool requests, a stop reason and the tokens used. | The repository is model-agnostic (charter, section 3). An agent written against one provider's format would have to be rewritten for another. | Letting the agents speak Anthropic's format directly. |
| D31 | The connector uses plain HTTPS from the standard library. | Nothing to install, as agreed; package installs are also off in the workspace. | The vendor's Python package. |
| D32 | The key is sent as `Authorization: Bearer` with `anthropic-version: 2026-10-21`, because that is what the example on the API reference page shows today. The older way (`x-api-key`) is kept as a setting. | Written from the page, not from memory. From memory the assistant would have written `x-api-key` and version `2023-06-01`. **Not verified**: which of the two a key created by M needs is known only after the first real call. | Hard-coding either one. |
| D33 | The reply of the service is handed back unchanged on the next call ("opaque"). | The API reference requires reasoning blocks to be returned exactly as received when tools are used. | Rebuilding the reply from text and tool requests only. |
| D34 | Effort is sent as `output_config.effort`, default `medium`. No `thinking` and no `temperature` setting is sent. | Effort is documented that way. The page says the accepted thinking settings depend on the model and the part read does not say what Fable 5.2 accepts; sending nothing leaves the service's default. | Guessing a thinking setting. |
| D35 | The key is read from a file named by the variable `SENTINEL_MODEL_KEY_FILE`, at the moment of the call. It is never logged or stored; a test checks it does not appear in a reply. | M creates the key; the assistant never opens it (handover). | A key in the settings or in the environment. |
| D36 | The OpenAI-style connector is not written in this step. | Its documentation has not been checked yet, and the rule of this build is: no connector from memory. | Writing it now from memory. |

### What was found in the documentation (read on 18 November 2026)

- Source: https://platform.claude.com/docs/en/api/messages/create.md, read in two parts.
- Model name `claude-fable-5-2` is listed. Effort values: low, medium, high, xhigh, max.
- Stop reasons: end_turn, max_tokens, stop_sequence, tool_use, pause_turn, refusal, model_context_window_exceeded. All seven are handled.
- Tokens used: the input is the sum of three counters (plain, cache written, cache read). The connector adds them.

### What changed

- New: `sentinel/model.py` (139 lines): the neutral format, the scripted stand-in for tests, the Claude connector.
- New: `tests/test_model.py`: 14 tests, without network and without key.
- Nothing else changed. No agent exists yet. No model has run.

### Measured results, session 4

- 39 of 39 tests pass in the workspace (25 existing, 14 new).
- What the new tests prove: what would be sent, and how an answer is read. What they do not prove: that the service accepts it. Only a recorded real run shows that.

### Steps

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 1 | Charter and both handovers read; existing code of solution 02 and the Control Tower gateway read | Project documents, Desktop folder | Main (Fable 5.2) | Input about 45,000, output about 1,000, estimated |
| 2 | Claude API reference read (one search, one page in two parts) | Web | Main, the page summary by a small model | Input about 40,000, output about 500, estimated |
| 3 | Model connector and its tests written; all tests run | Written directly, pytest in the workspace | Main | Output about 5,000, estimated |

### State after session 4

- Model involved: no. Agents: in build (connector only).
- Not pushed. The files are in the Desktop folder only.

### Lighter model

The connector and its tests could have been written by a lighter model once the format was decided. The agent loop and the agents' briefing, next, should not.

## Session 4, second part, 18 November 2026: the loop, the three agents, the decision page

M confirmed: reversible office-side steps are taken by the agents on their own through the Control Tower; everything touching the plant floor is held for the Head of OT Security.

### Decisions

| No. | Decision | Why | Alternative set aside |
|---|---|---|---|
| D37 | Three agents, not two: a first-response agent beside the planner and the challenger. | The planner's registry card is high-risk (it prepares plant-floor steps), so the Control Tower lets it read and nothing else. Letting that same identity act alone on the office side would need an exception to rule P-008. A separate identity with office-side permissions only is the cleaner answer: the agent that can ask for a line to be disconnected can do nothing alone, and the agent that can act alone cannot touch the plant floor. | One planner with two sets of rights; weakening P-008. |
| D38 | The two new registry cards (first response, challenger) are kept in this solution's `data/agents.json` and given to the gateway together with the Control Tower's registry. | Entering them in the Control Tower changes its published count of 18 in tests, generated pages, two README pages and the deck. That is a change to a paused solution and to public text. **Open: for M to decide.** | Changing solution 01 without asking. |
| D39 | An agent is finished only when it hands in through one tool, and the harness accepts the result. A result that fails a check is handed back with the reasons. | This is the "evaluates and corrects" of the charter's definition, made checkable: the record shows each refusal and the corrected attempt. | Taking the model's last message as the result. |
| D40 | Every euro figure in an agent's text must be one the pricing tool produced tonight (or the difference of two such prices). Any other figure makes the harness hand the result back. | "Every figure is measured or labelled" must hold for agent text too. A model that invents a figure at 03:00 is the failure a board fears most. | Trusting the prompt. |
| D41 | The decision page is put together by fixed code. Its figures come from the pricing tool's results; the agents' words are shown as quotations, marked as theirs. | The reader can tell what was calculated from what was argued. | A page written by a model. |
| D42 | The planner has no tool that disconnects anything. After the debate the harness files the plant-floor steps of the final recommendation with the Control Tower, which holds them. | Filing during the debate would leave stale requests when the planner changes its mind. | A disconnect tool that is always held. |
| D43 | The named person chooses a response by its number. The choice is written to the Control Tower record with the price, whether it was the recommended one, and the challenger's verdict. Held steps are released if chosen and refused if not; steps of another choice are carried out with the person's approval. Another role is refused and the attempt is recorded. | Item 5 of the "Working" list. It reuses the approval workflow of solution 01 as it is. | A separate approval mechanism. |
| D44 | If the planner does not hand in, the page says so and shows each single step priced by the tool alone; nothing is filed. If the challenger does not hand in, the page says the recommendation was not challenged. | A failed agent must not look like a quiet night. | Stopping without a page. |
| D45 | A harder night is a small file of changes to the scripted night (`data/nights/no-safe-response.json`): the intruder reaches Line C and the plant-wide disconnection is unavailable (assumption). On it, no response closes every path. | Item 2 of the "Working" list. The same mechanism will carry the invented rehearsal nights. | A second full data set. |
| D46 | The briefing (`data/briefing.json`) holds what the agents are told about the company and four settings the harness enforces: which office-side steps are allowed, accounts never suspended, how many responses fit on the page, how often the challenger speaks. The night stops if the briefing names another decider than the registry. | Item 1 of the "Working" list. Part of the briefing changes what a model is told, part changes what the harness allows; tests can prove only the second. | Role instructions and limits in code. |

### Limits found, each with the fix designed for it

- **No model has run.** All 36 new tests use prepared replies. They prove the harness, not the reasoning. The instructions to the three agents have never been read by a model and will probably need changes after the first real runs. Fix: the recorded real runs (next but one step).
- The office-side steps do not change the prices: the model of the plant assumes a device already controlled on the plant floor stays controlled. Stated on the page. Fix: none planned; it is the cautious assumption.
- Disconnecting cell 2 alone and disconnecting it together with closing the link cost the same (EUR 120,000) in the scripted night, because the link is closed for 4 hours and the lines run 6 hours on loaded orders. Correct by the assumptions, but it makes the scripted night an easy one for the planner. Fix: the invented rehearsal nights.
- `decide` looks for held steps by incident number. Two nights in the same Control Tower record both carry INC-001. Fix: a night identifier in the request (with the case memory).
- The page is written under the registry identity `ot-briefing`, which is fixed code on a card the registry calls an agent. Part of the open point on the Control Tower's wording.

### What changed

- New: `sentinel/loop.py` (80 lines), `sentinel/agents.py`, `sentinel/night.py`, `sentinel/decision.py`, `data/briefing.json`, `data/agents.json`, `data/nights/no-safe-response.json`, `tests/test_agents.py` (36 tests).
- Changed: `sentinel/collection.py` accepts the data of another night; `sentinel/__main__.py` has `night` and `decide`; `.gitignore` leaves out `state/`.
- The first version (`python -m sentinel run`) is unchanged and its page is still what the code produces.

### Measured results

- 75 of 75 tests pass in the workspace (25 first version, 14 connector, 36 agents).
- Against the list of ten on the solution page: items 1, 2, 5 and 6 are built and tested on the scripted stand-in only. Items 3, 4, 7, 8 are not built. Item 9 is measured by the code but has no real figure yet. Item 10 needs real runs.

### Steps

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 4 | Remaining code of the first version, registry, rules and approval workflow of the Control Tower read | Desktop folder | Main (Fable 5.2) | Input about 30,000, estimated |
| 5 | Loop, three agents, night, decision page, briefing, harder night, command line | Written directly | Main | Output about 14,000, estimated |
| 6 | 36 tests written; two failures found and fixed (order of responses on the page; a wrong call in a test) | pytest in the workspace | Main | Output about 7,000, estimated |

### State

- Model involved: no. Agents: in build. Status on the public pages unchanged and still true.
- Not pushed. Desktop folder only.

### Lighter model

Not for this step: the design of the controls and the wording of the agents' instructions are the substance of the solution.

## Session 4, third part, 18 November 2026: the two new cards enter the Control Tower registry

| No. | Decision | Why | Alternative set aside |
|---|---|---|---|
| D47 | M decided the open point of D38: the cards of the first-response agent and the challenger are entered in the Control Tower's registry (`solutions/01-ai-governance-control-tower/data/agents.json`). The separate list in this solution is removed; the gateway is the Control Tower's own again. | One registry is the single place agents are listed. A second list beside it is the pattern the Control Tower exists to prevent. | Keeping the cards in this solution until solution 01 is reopened. |

### What changed

- Solution 01: registry 18 to 20 cards; four counts in its tests; `reports/agent-inventory.md` and `reports/board-latest.md` regenerated by their commands (the red-team campaign pages are unchanged, byte for byte); one figure in its README (18 to 20 agents).
- Solution 02: `data/agents.json` removed; `sentinel/night.py` uses the Control Tower gateway as it is; one test rewritten.

### Measured results

- Solution 01: 77 of 77 tests pass. Solution 02: 75 of 75.
- Board page of the Control Tower, generated: 20 registered, 19 approved to act, 1 not yet approved; limited tier 11 to 12, minimal 6 to 7; advise only 9 to 10; acting within permissions 6 to 7.

### Limits found

- The classifier proposes the tier **minimal** for the first-response agent, although it suspends accounts on its own. The classifier follows the use-case flags of the EU AI Act reading (no safety component, no contact with people); it does not weigh what an agent can do inside the company. The tier is a proposal awaiting human sign-off, and the board page says so. Fix designed: a second, internal risk rating by reach of action, next to the legal tier. Not built.
- The board deck (local only) still says 18 agents on slides 9 and 16. To be corrected when the slides are redone.

### Steps

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 7 | Cards moved, counts and pages of solution 01 updated, both test suites run | Script and the Control Tower's own commands | Main (Fable 5.2) | Output about 2,500, estimated. A lighter model would have done. |

## Session 4, fourth part, 18 November 2026: interim publication, status unchanged

Agreed with M: five steps in order. 1 solution 01 (pushed, commit b2864b6: reach of action, what stands behind each card, the two cards). 2 this interim push of solution 02. 3 slides for solution 01. 4 remaining items and recorded real runs of solution 02. 5 slides for solution 02.

- Published with M's go: the code of session 4, 75 tests, and the solution page, front page and roadmap rewritten to say what is built, what is tested on prepared replies only, and what is not built. Status stays "In build".
- A sample decision page is published in `reports/`, labelled in its first paragraph as produced on prepared replies with hand-written agent sentences.
- Not changed: the published article. Its status line ("the agents are in build") is still true.
- Tokens for the page rewrites, estimated: output about 3,500, main model. A lighter model would have done.

## Session 4, fifth part, 18 November 2026: the first run with a real model

M chose route (a): his own model key, in a file outside the project folder, which the assistant cannot reach. Spending is capped by a prepaid balance with automatic top-up off. Runs with a real model are therefore started by M in PowerShell on his computer; the assistant reads the recorded result.

| No. | Decision | Why | Alternative set aside |
|---|---|---|---|
| D48 | The key file is read as `utf-8-sig`. | Notepad on Windows may put an invisible marker at the start of a file; the key would have been sent with it. | Asking M to save in a particular encoding. |
| D49 | Room per model reply raised from 4,000 to 16,000 tokens. | The model's reasoning counts against the same allowance and could cut an answer off. | Finding out by a failed run. |

### Measured: one run, scripted night, 18 November 2026, claude-fable-5-2 at medium effort

Recorded in `reports/runs/plant-04-0302-2026-11-18-claude-fable-5-2.md` and `.json`. One run is one run: no rate can be stated from it.

- The connector worked at the first call. The key is accepted as `Authorization: Bearer` with `anthropic-version: 2026-10-21` (D32 is now verified for M's key).
- All three agents handed in. Turns: first response 3, planner 3, challenger 2. No hand-in was refused; no tool failed.
- Time from the last alarm handed over to the decision page: 71.62 seconds. Tokens: 35,342 in, 6,905 out.
- First response: suspended two accounts (the stolen maintenance account and the employee account of the infected workstation), quarantined the finance workstation, closed the remote sessions on the gateway. All four within the briefing; nothing attempted on the plant floor.
- Planner: priced 8 responses, including combinations nobody asked for; recommended Line B cell 2 plus the link at EUR 120,000, the same as the rule-based first version; pointed out that cell 2 alone "is paying for a stop and gaining nothing"; added two safety calls (Line B shift lead, Line C maintenance crew) that no rule contains.
- Challenger: re-priced all five options itself, agreed, and added unknowns the planner had not named, among them that two alarms set aside as unrelated could concern the Line C panel.

### Limits found in this run, each with the fix designed for it

- **The debate was not exercised.** The challenger agreed, so the planner never had to answer an objection with a real model. As foreseen: the scripted night is an easy one. Fix: run the harder night and the invented nights.
- **The page is too long for three in the morning.** The first-response agent wrote about 450 words under "what it left alone", repeated the steps it took and listed the plant-floor options, which is not its job. Planner and challenger are also long. Fix: a word limit per field, enforced by the harness at hand-in, and tighter role texts.
- **Figures without separators.** The agents wrote "EUR 2160000". The figure control accepted them, correctly, because they are priced figures; they are hard to read. Fix: the role texts ask for the format of the page, or the page reformats priced figures in agent text.
- The correction path (a refused hand-in, then a corrected one) did not occur, so it is still shown on prepared replies only.

### Steps

| Step | What | How | Model | Tokens |
|---|---|---|---|---|
| 8 | Key set up with M, step by step; two small changes to the connector | Chat; documentation of the vendor's command-line tool read to rule it out | Main (Fable 5.2) | Input about 12,000, output about 3,000, estimated |
| 9 | First real run | Started by M in PowerShell | claude-fable-5-2, medium effort | 35,342 in, 6,905 out, measured |
