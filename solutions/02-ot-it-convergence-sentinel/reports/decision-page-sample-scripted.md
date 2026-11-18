**Sample, not a result.** This page was produced by the code in this folder on prepared replies, to show its layout and its controls. The sentences attributed to the agents were written by hand for a test. No language model was involved. Recorded runs with a real model will be published in `reports/runs/`.

# Decision page: incident INC-001 at Halden Plant 04 (fictional)

Night: Plant 04, the scripted night: last alarm at 03:02. Synthetic data, simulated tools. Agents run on: scripted stand-in (no model). Every euro figure is calculated by the pricing tool from the assumptions listed at the end; none is a measured loss and none was written by an agent.

## In short

An intruder moved from the office network to the plant floor between 02:10 and 03:02 UTC and controls 3 devices. 3 production lines are within reach.

The planner recommends: Disconnect Line B, cell 2 and close the link between office side and plant floor, at EUR 120,000 in lost output. It leaves no line within reach.

**The challenger objects.** Its argument is below, before the choice. Nothing has been disconnected on the plant floor: the choice is with the Head of OT Security.

## What happened

| Time (UTC) | Seen by | From | To | What |
|---|---|---|---|---|
| 02:10 | office tool | ws-fin-117 | ws-fin-117 | Email attachment flagged after it was opened. |
| 02:14 | office tool | ws-fin-117 | ws-fin-117 | A program read stored passwords from memory. |
| 02:31 | office tool | ws-fin-117 | dc-01 | Plant maintenance account signed in from a finance workstation. |
| 02:38 | office tool | ws-fin-117 | jump-p04-01 | Remote access to the plant floor opened outside the agreed maintenance window. |
| 02:44 | plant tool | jump-p04-01 | ews-b2-01 | Remote screen session to the engineering workstation. |
| 02:52 | plant tool | ews-b2-01 | plc-b2-01 | Full controller program copied outside a change window. |
| 02:55 | plant tool | ews-b2-01 | plc-b2-02 | Full controller program copied outside a change window. |
| 03:02 | plant tool | ews-b2-01 | hmi-c1 | Search for open file shares in Line C, cell 1. |

## Already done on the office side

Taken by the first-response agent on its own. Each step can be undone and is in the Control Tower's record.

| Step | On | How it is undone | Record |
|---|---|---|---|
| Account suspended | svc-maint-p04 | Undone by the Head of Security Operations re-enabling the account. | 9 |
| Device cut off the network | ws-fin-117 | Undone by the Head of Security Operations releasing the workstation from quarantine. | 10 |
| Remote sessions closed | jump-p04-01 | Undone by opening a new remote session through the normal request. | 11 |

What it left alone, in its own words:

> The engineering workstation: it is on the plant floor.

## The responses to choose from

| No. | Response | Lost output | Lines stopped | Lines the intruder can still reach | Still at stake if those are encrypted |
|---|---|---|---|---|---|
| 1 | Disconnect Line B, cell 2 and close the link between office side and plant floor **(recommended)** | EUR 120,000 | Line B: 8 h | none | EUR 0 |
| 2 | Disconnect the whole plant floor | EUR 285,500 | Line A: 8 h; Line B: 8 h; Line C: 3.03 h | none | EUR 0 |
| 3 | Disconnect Line B, cell 2 | EUR 120,000 | Line B: 8 h | Line A, Line B, Line C | EUR 2,160,000 |
| 4 | Do nothing and keep watching | EUR 0 | none | Line A, Line B, Line C | EUR 2,160,000 |

## The planner's reasoning

> Disconnecting Line B, cell 2 and closing the link costs EUR 120,000 and leaves no line within reach. The whole plant floor costs EUR 285,500 for the same result on the map we have.

What remains open, in the planner's words:

> Whether the map is complete. One forgotten file share was found tonight.

## The counter-argument

The challenger objects:

> Disconnecting Line B, cell 2 alone costs EUR 120,000 too, or less? I priced it: it leaves the remote access gateway open. My real objection is another one: the recommendation rests on the plant map. The file share between Line B and Line C was not on anyone's list until tonight. If there is a second forgotten connection, only the whole plant floor at EUR 285,500 is safe.

It proposes response 2 instead.

What nobody knows, in the challenger's words:

> Whether other cells are already touched.

The planner kept its recommendation and answers:

> The objection is fair and I cannot rule it out with the tools I have. I keep the recommendation because the difference is EUR 165,500 for a risk nobody has evidence of, and say so plainly: if the decider does not trust the map, response 2 is the one to choose.

## The decision

The Head of OT Security chooses one response by its number: `python -m sentinel decide NUMBER --as "Head of OT Security"`. No other role can choose, and no agent can. The choice is written to the Control Tower's record.

Filed with the Control Tower for the recommended response and held there:

| Step | Waiting for | Rules that hold it |
|---|---|---|
| Disconnect Line B, cell 2 | Head of OT Security | P-007, P-008, P-009 |
| Close the link between office side and plant floor | Head of OT Security | P-007, P-008, P-009 |

## Assumptions behind the figures

- Cost of one stopped line-hour: EUR 15,000 (company profile).
- Assumption: a line keeps running this long on orders already loaded when the link to the office side is closed. Value used: 6 hours.
- Assumption: time to restore a line whose controllers and workstations were encrypted. Value used: 48 hours.
- Assumption: a disconnected cell stops its whole line. Value used: yes.
- Disconnect Line B, cell 2: held for 8 hours. Assumption: time to check and clean the devices of one cell.
- Close the link between office side and plant floor: held for 4 hours. Assumption: time to clean the remote access gateway and replace the stolen account.
- Disconnect the whole plant floor: held for 8 hours. Assumption: time to check and clean the devices of the plant floor.
- Lost output is counted only for hours in which the schedule says the line would have run.
- The office-side steps do not change the prices: a device the intruder already controls on the plant floor is assumed to stay under its control.

## How this page was made

- Alarms read: 13; joined into this incident: 8; set aside: 5. Joining is done by fixed rules, not by an agent.
- Responses priced tonight by the agents: 5.
- Agent turns: ot-first-response 3 (handed in), ot-response 3 (handed in), ot-challenger 2 (handed in), ot-response 1 (handed in).
- Time from the last alarm handed over to this page: 0.01 seconds. Tokens: 0 in, 0 out.

## What this page is not

- Not a detection result: the alarms were written by hand for this night.
- Not a forecast: the figures follow from the assumptions above and change with them.
- Not proof that the agents are right. They can be wrong; that is why one challenges the other and a person decides.
