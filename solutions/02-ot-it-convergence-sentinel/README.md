# OT/IT Convergence Sentinel

**Status: In build. A first slice is working: one scripted incident at one plant, on fixed rules, with simulated tools and no language model.**

The decision layer above the security tools you already own.

## What it is

A team of four agents that takes the alerts of the office and plant-floor security tools a company already runs, joins them into one incident, prices every possible response in lost output, and asks a named person to release the chosen one. It does not replace those tools and does not try to detect better than they do.

## The management issue it solves

Ransomware that stops production is the top cyber risk for a manufacturer, and the IT and plant security teams rarely share one picture. When an incident reaches the plant floor at night, the safe reflex is to disconnect everything. Nobody in the room can say what that costs, or whether a smaller step would do.

## "We already have AI network management tools"

Yes, and they stay. Security and network vendors now ship their own agents that collect, correlate, diagnose and remediate. This solution sits above them and adds three things they are not built for:

- **The price of each response in lost output.** That needs the production schedule and the cost of a stopped line, which live in business systems outside a security product.
- **One set of rules for every agent, whichever vendor it comes from.** Every action passes the [AI Governance Control Tower](../01-ai-governance-control-tower/README.md): it is checked, held for the accountable owner where the rules say so, and recorded.
- **A page for the crisis team, not for the analyst.**

We did not find a product that prices containment options in lost output during an incident. That is a statement about what we found on 16 November 2026, not a claim that none exists.

## What the first slice shows

Measured on 17 November 2026 by running `python -m sentinel run` in this folder. All data is synthetic. Every euro figure is calculated from stated assumptions; none is a measured loss.

The scenario: at 02:10 a finance employee at Halden Plant 04 opens a malicious attachment. Within an hour the intruder uses a stolen maintenance account to reach an engineering workstation on Line B, copies two controller programs and starts looking for a way into Line C.

| Response | Lost output | Lines still within the intruder's reach |
|---|---|---|
| Do nothing and keep watching | EUR 0 | Line A, Line B, Line C |
| Disconnect Line B, cell 2 | EUR 120,000 | Line A, Line B, Line C |
| Close the link between office side and plant floor | EUR 0 | Line B, Line C |
| Disconnect the whole plant floor | EUR 285,500 | none |
| **Disconnect Line B, cell 2 and close the link (recommended)** | **EUR 120,000** | **none** |

The recommended response closes every known path for EUR 165,500 less than disconnecting everything. The difference is the output of Line A and Line C, which the recommended response leaves running. Line C is in planned maintenance until 08:00, so the hour of the decision changes the price.

The full page as the crisis team would see it: [reports/incident-latest.md](reports/incident-latest.md).

| Measure | Result |
|---|---|
| Alerts collected from two tools with different formats | 13 |
| Joined into one incident | 8 |
| Set aside as unrelated, and listed | 5 |
| Responses priced | 5 |
| Decisions by the Control Tower in one run | 13: 11 allowed, 2 held for the Head of OT Security |
| Isolation carried out without a human release | 0 |
| Tests | 25 of 25 pass |

## The four agents

| Agent | What it does | Status | Limits of the first slice |
|---|---|---|---|
| Collection | Reads the plant layout and the alerts of the office and plant-floor tools, and puts them in one format. | Working | Reads two prepared files. Connection to real tools is designed. |
| Correlation | Joins alerts that share a device or an account within one hour into one incident, with the intruder's path and the lines within reach. | Working | One fixed rule. It has seen one scenario; two more are designed. |
| Impact and response | Prices each response in lost output from the production schedule, states what each leaves within reach, recommends the cheapest one that closes every known path, and asks for it. | Working | Prices follow from assumptions. No probability of spread is estimated. |
| Briefing | Writes one page for the crisis team. | Working | One generated page. The notification to the regulator (NIS2) is designed, not built. |

All four are registered in the Control Tower with an accountable owner and a named approver. The impact and response agent is classified high-risk there, so it may read on its own and nothing else: its isolation requests wait for the Head of OT Security, and a release attempt by any other role is refused.

No language model runs in this slice. Each agent is a fixed rule, which makes every result repeatable and its running cost zero. "State of the art" describes the design, not this slice.

## Run it

Python 3.10 or later, nothing to install. From this folder:

```
python -m sentinel run
python -m sentinel waiting
python -m sentinel release --as "Head of OT Security"
python -m pytest -q
```

`release` acts on a simulated network: it records that the isolation ran and touches nothing.

## What is in this folder

- `sentinel/` the four agents, the workflow and the command line (about 500 lines)
- `data/plant.json` zones, devices, connections and isolation points of the plant (synthetic)
- `data/production.json` lines, schedule and every assumption behind the prices (synthetic)
- `data/events_office.json`, `data/events_plant.json` the alerts of the two simulated tools
- `reports/incident-latest.md` the page for the crisis team, generated
- `tests/` 25 tests
- `BUILD_LOG.md` decisions, alternatives set aside, corrections and estimated tokens per step

## Not built yet

- Two further attack scenarios, including one that the single correlation rule should miss.
- Connection to real security tools and to a real production schedule.
- A language model for the investigation and for wording the briefing.
- The notification to the regulator. Its legal deadlines must be checked against the official text first.
- Mapping of agent permissions to IEC 62443 zones, a tabletop exercise generator and supplier remote-access monitoring.

## Next steps

1. Add the two further scenarios and publish where the correlation fails.
2. Read the assumptions from a production schedule that changes by shift, and show how the recommendation moves.
3. Report the cost and benefit of each run to the AI Value Ledger once it exists.

See the one-page [business case](BUSINESS_CASE.md).
