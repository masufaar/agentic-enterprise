# Decision page: incident INC-001 at Halden Plant 04 (fictional)

Night: The scripted night, with the plant-floor monitoring down. Synthetic data, simulated tools. Agents run on: claude-fable-5-2, effort medium. Every euro figure is calculated by the pricing tool from the assumptions listed at the end; none is a measured loss and none was written by an agent.

## In short

An intruder moved from the office network to the plant floor between 02:10 and 02:38 UTC and controls 1 devices. 3 production lines are within reach.

**Blind spot tonight: the plant-floor-monitoring (simulated) on the plant floor sent nothing.** Assumption for this night: the plant-floor monitoring is down after a failed update and sends nothing before 08:00. Many plants have no such tool at all. Nobody can see whether the intruder is already on the plant floor. Lines there are marked "not watched" below and are never counted as safe, so the prices of the narrow responses look better than what is known.

The planner recommends: Close the link between office side and plant floor, at EUR 0 in lost output. **It leaves Line A, Line B, Line C within reach or unwatched.**

The challenger agrees. Nothing has been disconnected on the plant floor: the choice is with the Head of OT Security.

## What happened

| Time (UTC) | Seen by | From | To | What |
|---|---|---|---|---|
| 02:10 | office tool | ws-fin-117 | ws-fin-117 | Email attachment flagged after it was opened. |
| 02:14 | office tool | ws-fin-117 | ws-fin-117 | A program read stored passwords from memory. |
| 02:31 | office tool | ws-fin-117 | dc-01 | Plant maintenance account signed in from a finance workstation. |
| 02:38 | office tool | ws-fin-117 | jump-p04-01 | Remote access to the plant floor opened outside the agreed maintenance window. |
| - | plant floor | - | - | Nothing: the plant-floor-monitoring (simulated) sent no alarm tonight. |

## Already done on the office side

Taken by the first-response agent on its own. Each step can be undone and is in the Control Tower's record.

| Step | On | How it is undone | Record |
|---|---|---|---|
| Device cut off the network | ws-fin-117 | Undone by the Head of Security Operations releasing the workstation from quarantine. | 167 |
| Account suspended | svc-maint-p04 | Undone by the Head of Security Operations re-enabling the account. | 168 |
| Account suspended | employee-0733 | Undone by the Head of Security Operations re-enabling the account. | 169 |
| Remote sessions closed | jump-p04-01 | Undone by opening a new remote session through the normal request. | 170 |

What it left alone, in its own words:

> Sign-in server: left running. Cutting it stops every office sign-in; other stolen passwords are possible, not known. Remote access gateway: session closed, gateway left connected and not cleaned. Other office machines: no alarm. Plant floor: not mine. Its monitoring is down until 08:00. Nobody knows what the intruder did there after 02:38.

## The responses to choose from

| No. | Response | Lost output | Lines stopped | Lines the intruder can still reach | Still at stake if those are encrypted |
|---|---|---|---|---|---|
| 1 | Disconnect the whole plant floor | EUR 279,500 | Line A: 8 h; Line B: 8 h; Line C: 2.63 h | none | EUR 0 |
| 2 | Close the link between office side and plant floor **(recommended)** | EUR 0 | none | Line A (not watched), Line B (not watched), Line C (not watched) | EUR 2,160,000 |
| 3 | Disconnect Line B, cell 2 | EUR 120,000 | Line B: 8 h | Line A, Line B, Line C | EUR 2,160,000 |
| 4 | Disconnect Line B, cell 2 and close the link between office side and plant floor | EUR 120,000 | Line B: 8 h | Line A (not watched), Line B (not watched), Line C (not watched) | EUR 2,160,000 |
| 5 | Do nothing and keep watching | EUR 0 | none | Line A, Line B, Line C | EUR 2,160,000 |

## The planner's reasoning

> The intruder was seen on the office side and on the remote access gateway. No alarm came from any line. Closing the link between office side and plant floor shuts the only way in and costs EUR 0: the four-hour hold fits inside the six-hour order buffer. Stopping Line B, cell 2 as well costs EUR 120,000 and closes nothing more. Disconnecting the whole plant floor costs EUR 279,500; only that leaves nothing at stake. This recommendation is not a safe one. Plant-floor monitoring is down, so silence from the lines proves nothing. Earlier cases reached Line B, cell 2 by this path; they do not change my view, but check that cell first.

What remains open, in the planner's words:

> Nobody knows what the remote session did on the plant floor before it was closed. Plant-floor monitoring sends nothing before 08:00, so Lines A, B and C are unwatched. If the intruder is already inside, closing the link does not remove him and EUR 2,160,000 remains at stake. The file share between Line B, cell 2 and Line C, cell 1 stays open. Past six hours, lines run out of orders. Earlier cases carry no decision.

## The counter-argument

The challenger agrees:

> I repriced all five responses. Every figure matches. Closing the link costs EUR 0 and leaves no line reachable from the office side. Adding Line B, cell 2 costs EUR 120,000 and leaves the same EUR 2,160,000 at stake, so it buys nothing tonight. Only disconnecting the whole plant floor, at EUR 279,500, brings the stake to EUR 0. No cheaper response is as safe. No alarm names a line tonight; the earlier cases did touch Lines B and C, but carry no decision. The plan says plainly it is not safe. Two assumptions carry the EUR 0: the four-hour hold and the six-hour order buffer. If the cleaning overruns, Lines A and B run out of orders.

What nobody knows, in the challenger's words:

> Nobody knows what the remote session did on the plant floor between 02:38 and its closing. Plant-floor monitoring sends nothing before 08:00, so Lines A, B and C are unwatched. If the intruder is already inside, closing the link does not remove him, and the old file share between Line B, cell 2 and Line C, cell 1 stays open. Nobody knows whether the four-hour hold will be met. Someone should check Line B, cell 2 by hand.

## A change to the company briefing, proposed by the planner

> When plant-floor monitoring is down, a person on site checks the cells by hand before any narrow response is treated as sufficient, and every plan states that the lines are unwatched.

Recorded with the case. Not applied: a person decides whether the briefing changes.

## Case memory

This night is recorded as CASE-004. Earlier cases read by the agents: CASE-001, CASE-002, CASE-003.

## The decision

The Head of OT Security chooses one response by its number: `python -m sentinel decide NUMBER --as "Head of OT Security" --note "what the next night should know"`. No other role can choose, and no agent can. The choice is written to the Control Tower's record.

Filed with the Control Tower for the recommended response and held there:

| Step | Waiting for | Rules that hold it |
|---|---|---|
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

- Alarms read: 6; joined into this incident: 4; set aside: 2. Joining is done by fixed rules, not by an agent.
- Responses priced tonight by the agents: 5.
- Agent turns: ot-first-response 3 (handed in), ot-response 4 (handed in), ot-challenger 2 (handed in).
- Time from the last alarm handed over to this page: 49.73 seconds. Tokens: 44,530 in, 4,561 out.

## What this page is not

- Not a detection result: the alarms were written by hand for this night.
- Not a forecast: the figures follow from the assumptions above and change with them.
- Not proof that the agents are right. They can be wrong; that is why one challenges the other and a person decides.
