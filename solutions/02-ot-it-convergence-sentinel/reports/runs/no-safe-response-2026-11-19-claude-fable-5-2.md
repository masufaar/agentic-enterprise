# Decision page: incident INC-001 at Halden Plant 04 (fictional)

Night: The same night, eleven minutes later, with the plant-wide disconnection unavailable. Synthetic data, simulated tools. Agents run on: claude-fable-5-2, effort medium. Every euro figure is calculated by the pricing tool from the assumptions listed at the end; none is a measured loss and none was written by an agent.

## In short

An intruder moved from the office network to the plant floor between 02:10 and 03:13 UTC and controls 4 devices. 3 production lines are within reach.

**No response available tonight closes every path.** The planner recommends: Disconnect Line B, cell 2 and close the link between office side and plant floor, at EUR 120,000 in lost output. It leaves Line C within the intruder's reach, with EUR 720,000 at stake if it is encrypted.

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
| 03:09 | plant tool | ews-b2-01 | hmi-c1 | Program started on the operator panel of Line C, cell 1, over the file share. |
| 03:13 | plant tool | hmi-c1 | plc-c1-01 | Full controller program copied outside a change window. |

## Already done on the office side

Taken by the first-response agent on its own. Each step can be undone and is in the Control Tower's record.

| Step | On | How it is undone | Record |
|---|---|---|---|
| Account suspended | svc-maint-p04 | Undone by the Head of Security Operations re-enabling the account. | 128 |
| Account suspended | employee-0733 | Undone by the Head of Security Operations re-enabling the account. | 129 |
| Device cut off the network | ws-fin-117 | Undone by the Head of Security Operations releasing the workstation from quarantine. | 130 |
| Remote sessions closed | jump-p04-01 | Undone by opening a new remote session through the normal request. | 131 |

What it left alone, in its own words:

> Sign-in server: used, not shown taken over; cutting it stops all sign-ins. Remote access gateway: sessions closed, not cut off; cutting it is a plant-floor decision. Other office devices: no alarm. Line B cell 2 and Line C cell 1 stay in the intruder's hands; my steps do not reach them. Unknown: whether other passwords were stolen.

## The responses to choose from

| No. | Response | Lost output | Lines stopped | Lines the intruder can still reach | Still at stake if those are encrypted |
|---|---|---|---|---|---|
| 1 | Close the link between office side and plant floor | EUR 0 | none | Line B, Line C | EUR 1,440,000 |
| 2 | Disconnect Line B, cell 2 and close the link between office side and plant floor **(recommended)** | EUR 120,000 | Line B: 8 h | Line C | EUR 720,000 |
| 3 | Disconnect Line B, cell 2 | EUR 120,000 | Line B: 8 h | Line A, Line B, Line C | EUR 2,160,000 |
| 4 | Do nothing and keep watching | EUR 0 | none | Line A, Line B, Line C | EUR 2,160,000 |

Not available tonight: Disconnect the whole plant floor. Assumption for this night: the central plant-floor switch is being replaced and the plant-wide disconnection cannot be triggered before 07:00.

## The planner's reasoning

> Disconnect Line B, cell 2 and close the link between office side and plant floor. Cost: EUR 120,000, Line B stopped 8 hours. It takes Lines A and B out of the intruder's reach. It does not close every path: Line C stays within reach, EUR 720,000 at stake. Doing nothing costs EUR 0 and leaves EUR 2,160,000 at stake. Cell cut alone costs EUR 120,000 and still leaves EUR 2,160,000 at stake. Link alone costs EUR 0 and leaves EUR 1,440,000 at stake. The link's EUR 0 holds only if it reopens within the 6-hour order buffer. No monitoring tool was silent tonight. Earlier cases are undecided and do not change my view.

What remains open, in the planner's words:

> Line C is not covered. The intruder's program is still on the Line C, cell 1 panel; no step tonight isolates that cell. Plant-wide disconnection is not possible before 07:00. Nobody knows: whether that program can act alone; whether any controller program was changed or only copied; whether a crew is at Line C now, so check in person first; whether the 4-hour, 8-hour and 6-hour assumptions hold; whether the intruder holds other accounts.

## The counter-argument

The challenger objects:

> I re-priced all four responses. The planner's figures are right, and no cheaper response is as safe. Keep the steps. I object to two gaps in the page.
> One: the link closure shows EUR 0 only on an assumption. Lines run 6 hours on loaded orders; the link is assumed closed 4 hours. If cleaning the gateway overruns by two hours, Line A starves. The plan does not say this.
> Two: Line C restarts at 08:00 with EUR 720,000 at stake and the intruder's program still on its panel. Plant-wide disconnection becomes possible at 07:00. The plan sets no decision before the restart. Ask the decider now: does Line C start?
> Earlier cases are scripted and undecided.

What nobody knows, in the challenger's words:

> Whether the program on the Line C, cell 1 panel can act on its own once Line B, cell 2 and the office link are cut. Whether any controller program was changed or only copied. Whether a crew is at Line C right now. Whether the 4-hour and 8-hour cleaning times and the 6-hour order buffer hold; all three are assumptions. Whether the intruder holds other accounts.

The planner kept its recommendation and answers:

> Checked; both points are right. I keep the steps and add both to the page. One: the link is assumed closed 4 hours, the order buffer is 6. If gateway cleaning overruns two hours, Line A runs out of orders; that cost is not priced. Two: the Head of OT Security should decide before 08:00 whether Line C starts, and at 07:00 whether to disconnect the plant floor. I recommend Line C stays down until its panel is checked.

## A change to the company briefing, proposed by the planner

> Add a response step to disconnect Line C, cell 1 alone, and close the old file share between Line B, cell 2 and Line C, cell 1, so a narrow stop is possible next time.

Recorded with the case. Not applied: a person decides whether the briefing changes.

## Case memory

This night is recorded as CASE-003. Earlier cases read by the agents: CASE-001, CASE-002.

## The decision

The Head of OT Security chooses one response by its number: `python -m sentinel decide NUMBER --as "Head of OT Security" --note "what the next night should know"`. No other role can choose, and no agent can. The choice is written to the Control Tower's record.

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
- Lost output is counted only for hours in which the schedule says the line would have run.
- The office-side steps do not change the prices: a device the intruder already controls on the plant floor is assumed to stay under its control.

## How this page was made

- Alarms read: 15; joined into this incident: 10; set aside: 5. Joining is done by fixed rules, not by an agent.
- Responses priced tonight by the agents: 4.
- Agent turns: ot-first-response 3 (handed in), ot-response 3 (handed in), ot-challenger 5 (handed in), ot-response 4 (handed in).
- Time from the last alarm handed over to this page: 77.48 seconds. Tokens: 88,316 in, 7,451 out.

## What this page is not

- Not a detection result: the alarms were written by hand for this night.
- Not a forecast: the figures follow from the assumptions above and change with them.
- Not proof that the agents are right. They can be wrong; that is why one challenges the other and a person decides.
