# Decision page: incident INC-001 at Halden Plant 04 (fictional)

Night: The scripted night, with a new alarm after the first plan. Synthetic data, simulated tools. Agents run on: claude-fable-5-2, effort medium. Every euro figure is calculated by the pricing tool from the assumptions listed at the end; none is a measured loss and none was written by an agent.

## In short

An intruder moved from the office network to the plant floor between 02:10 and 03:09 UTC and controls 4 devices. 3 production lines are within reach.

**The night changed after the first plan.** A new alarm arrived at 03:09 UTC. Before it, the planner recommended Disconnect Line B, cell 2 and close the link between office side and plant floor, at EUR 120,000; it now recommends Disconnect the whole plant floor, at EUR 287,250.

The planner recommends: Disconnect the whole plant floor, at EUR 287,250 in lost output. It leaves no line within reach.

The challenger agrees. Nothing has been disconnected on the plant floor: the choice is with the Head of OT Security.

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
| 03:09 | plant tool | hmi-c1 | plc-c1-01 | Full controller program of Line C, cell 1, copied from the operator panel outside a change window. (new alarm, after the first plan) |

## Already done on the office side

Taken by the first-response agent on its own. Each step can be undone and is in the Control Tower's record.

| Step | On | How it is undone | Record |
|---|---|---|---|
| Account suspended | svc-maint-p04 | Undone by the Head of Security Operations re-enabling the account. | 79 |
| Account suspended | employee-0733 | Undone by the Head of Security Operations re-enabling the account. | 80 |
| Device cut off the network | ws-fin-117 | Undone by the Head of Security Operations releasing the workstation from quarantine. | 81 |
| Remote sessions closed | jump-p04-01 | Undone by opening a new remote session through the normal request. | 82 |

What it left alone, in its own words:

> Sign-in server: touched, not shown as taken over; unknown if other passwords were stolen there. Remote access gateway: stays on the network, still under intruder control. Other office devices: no alarm. Plant floor: not mine. The intruder may still sit on the engineering workstation in Line B, cell 2, with the open share to Line C.

## The responses to choose from

| No. | Response | Lost output | Lines stopped | Lines the intruder can still reach | Still at stake if those are encrypted |
|---|---|---|---|---|---|
| 1 | Disconnect the whole plant floor **(recommended)** | EUR 287,250 | Line A: 8 h; Line B: 8 h; Line C: 3.15 h | none | EUR 0 |
| 2 | Close the link between office side and plant floor | EUR 0 | none | Line B, Line C | EUR 1,440,000 |
| 3 | Disconnect Line B, cell 2 | EUR 120,000 | Line B: 8 h | Line A, Line B, Line C | EUR 2,160,000 |
| 4 | Disconnect Line B, cell 2 and close the link between office side and plant floor | EUR 120,000 | Line B: 8 h | Line C | EUR 720,000 |
| 5 | Do nothing and keep watching | EUR 0 | none | Line A, Line B, Line C | EUR 2,160,000 |

## The plan before the new alarm

Recommended then: Disconnect Line B, cell 2 and close the link between office side and plant floor, at EUR 120,000 (priced before the new alarm; out of date). The planner's reasoning then:

> Disconnect Line B, cell 2 and close the link between office side and plant floor. Cost: EUR 120,000, Line B stopped 8 hours. Priced, it leaves no line within reach. The intruder sits on the engineering workstation in cell 2 and has searched Line C through an old file share. Cutting the cell alone costs the same EUR 120,000 and leaves all three lines reachable. Closing the link alone costs EUR 0 but leaves Lines B and C reachable, EUR 1,440,000 at stake. The whole plant floor costs EUR 285,500 and closes nothing more. Doing nothing leaves EUR 2,160,000 at stake. The earlier case recommended the same; it has no decision or note, so my view stands.

## The planner's reasoning

> I change my recommendation. The new alarm shows the intruder now sits on the operator panel of Line C, cell 1, and copied its controller program. My earlier plan, Line B cell 2 plus the office link, costs EUR 120,000 but leaves Line C within reach, with EUR 720,000 at stake. Tonight there is no step that disconnects Line C, cell 1 alone. Only disconnecting the whole plant floor closes every path. It costs EUR 287,250 and leaves nothing within reach. Line C is in maintenance until 08:00, so people may be at the machine while the intruder holds its panel. Safety comes first. The price is stopping Line A, where we have seen nothing.

What remains open, in the planner's words:

> The recommendation stops Line A for eight hours without any sign of the intruder there. Nobody knows whether the controller programs on Line B and Line C were only copied or also changed. Nobody knows whether maintenance staff are at Line C now; ask the shift lead. Nobody knows whether the intruder holds other devices unseen. All monitoring reported tonight. Prices rest on assumptions. The earlier case ended before the Line C alarm and does not change my view.

## The counter-argument

The challenger agrees:

> I re-priced all five responses. The planner's figures hold. Disconnecting the whole plant floor costs EUR 287,250 and leaves no line within reach. The cheaper plan, Line B cell 2 plus the office link, costs EUR 120,000 but leaves Line C within reach, with EUR 720,000 at stake. No step tonight disconnects Line C, cell 1 alone, so nothing cheaper closes Line C. The earlier case ended before the Line C alarm and records no decision. One caution: Line A's stop, EUR 120,000 of the total, is the price of having no narrow cut for Line C. Disconnecting does not by itself make the Line C machine safe to work on.

What nobody knows, in the challenger's words:

> Whether the controller programs on Line B and Line C were changed or only copied. Whether the intruder left anything on the Line C operator panel that can still act on its controller after the disconnect. Whether maintenance staff are at Line C now. Whether the intruder holds devices no alarm has shown. Whether the eight-hour check time holds; it is an assumption, as is every price.

## A change to the company briefing, proposed by the planner

> Add a response step to disconnect Line C, cell 1 alone, and close the old file share between Line B, cell 2 and Line C, cell 1, so a narrow stop is possible next time.

Recorded with the case. Not applied: a person decides whether the briefing changes.

## Case memory

This night is recorded as CASE-002. Earlier cases read by the agents: CASE-001.

## The decision

The Head of OT Security chooses one response by its number: `python -m sentinel decide NUMBER --as "Head of OT Security" --note "what the next night should know"`. No other role can choose, and no agent can. The choice is written to the Control Tower's record.

Filed with the Control Tower for the recommended response and held there:

| Step | Waiting for | Rules that hold it |
|---|---|---|
| Disconnect the whole plant floor | Head of OT Security | P-007, P-008, P-009 |

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

- Alarms read: 14; joined into this incident: 9; set aside: 5. Joining is done by fixed rules, not by an agent.
- Responses priced tonight by the agents: 7.
- Agent turns: ot-first-response 4 (handed in), ot-response 4 (handed in), ot-response 4 (handed in), ot-challenger 3 (handed in).
- Time from the new alarm to this page: 43.01 seconds.
- Time from the last alarm handed over to this page: 77.79 seconds. Tokens: 85,851 in, 7,460 out.

## What this page is not

- Not a detection result: the alarms were written by hand for this night.
- Not a forecast: the figures follow from the assumptions above and change with them.
- Not proof that the agents are right. They can be wrong; that is why one challenges the other and a person decides.
