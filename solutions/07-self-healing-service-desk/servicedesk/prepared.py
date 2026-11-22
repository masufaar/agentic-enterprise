"""Prepared replies: what a scripted stand-in says in place of a model.

These are not a model and prove nothing about one. They exist so that the tests
and the sample page run every time, without a key and without cost, and so that
the fixed code around the model can be shown working: the tools, the refusals
handed back, the hand-in checks, the ladder, the page. Each scenario's replies
include at least one hand-in that the harness does not accept, and its correction.
"""
RESET = "reset password and send a one-time sign-in link to the owner's registered contact"
ARCHIVE = "enable the online archive"
REINSTALL, TEMPORARY = "reinstall the VPN profile", "install a temporary VPN certificate"


def ask(name: str, **given) -> dict:
    return {"tool_calls": [{"id": f"call-{name}", "name": name, "input": given}]}


def looks() -> list[dict]:
    """The verifier reads its four sources."""
    return [ask("read_ticket"), ask("look_up_owner"), ask("read_action_log"), ask("read_later_tickets")]


def finding(fix: str, entitled: str, record: str, words: str, lesson: str, evidence: list[str] | None = None) -> dict:
    return ask("file_finding", fix_held=fix, requester_entitled=entitled, record_matches=record,
               evidence=evidence or [], finding=words, lesson=lesson)


SOUND = "The log shows the action the note names, by the same actor. The requester owns the laptop. No later ticket about it."

REPLIES = {
    "sound-batch": [
        *looks(), finding("yes", "yes", "yes", SOUND, "A mailbox closure with the archive in the log and no return is sound."),
        *looks(), finding("yes", "yes", "yes", SOUND, "Nothing new: archive enabled, no return within seven days."),
        *looks(), finding("yes", "yes", "yes", SOUND, "A catalogue installation that is in the log and did not come back is sound."),
        ask("read_ticket"), ask("look_up_owner"),
        ask("resolve", action=ARCHIVE, note="Online archive enabled. Older mail moves there automatically."),
        ask("finish", what_i_did="resolved", reason="The requester owns the laptop and the mailbox is full. The suite "
            "offers the online archive for this; I enabled it and said so on the ticket.",
            lesson="A full mailbox with a signed-in requester is solved by the archive; check in seven days that it held."),
        *looks(),
        finding("yes", "yes", "yes", "Archive enabled by sd-resolution, as the note says. The requester owns the laptop.",
                "Our own closures are checked like any other."),
        finding("cannot tell", "yes", "yes", "Archive enabled by sd-resolution, as the note says. The requester owns "
                "the laptop. The ticket was closed today, so nobody can say yet whether the fix held.",
                "A closure is not a held fix until the follow-up days are over."),
    ],
    "wrong-requester": [
        ask("read_ticket"), ask("look_up_owner"),
        ask("resolve", action=RESET, note="Password reset. One-time sign-in link sent to the owner's registered contact."),
        ask("finish", what_i_did="resolved", reason="The requester is the owner of the account and came in through a "
            "signed-in session. I reset the password; the link goes to the registered contact only.",
            lesson="A reset for the signed-in owner is routine; the link never goes to an address given in the ticket."),
        ask("read_ticket"), ask("look_up_owner"), ask("read_action_log"),
        finding("yes", "yes", "yes", "Reset logged as noted; requester is the owner, second factor confirmed.",
                "Nothing new."),
        ask("read_later_tickets"),
        finding("no", "yes", "yes", "The reset is in the log and the requester is the owner, confirmed by second factor. "
                "The next day the same person wrote SD-26-0138: still locked out of the same account.",
                "A reset that is followed by 'locked out' the next day did not hold; look at why the link did not work.",
                evidence=["SD-26-0138"]),
        *looks(),
        finding("cannot tell", "no", "yes", "The requester HI-EMP-42057 is not the owner of acct-11581, and no "
                "confirmation is recorded. The link went to the address given in the chat. The log then shows a sign-in "
                "from a device not seen before. The owner reports in SD-26-0147 a change that was not theirs.",
                "A reset asked 'for a colleague' with the link sent to the asker is the pattern of an account takeover.",
                evidence=["SD-26-0147"]),
        *looks(), ask("read_cases"),
        finding("cannot tell", "no", "yes", "The request came from an address outside the company, for acct-54267, with "
                "no confirmation recorded. The link went to that outside address. A sign-in from an unknown device "
                "followed, and the owner reports it in SD-26-0155.",
                "The second case in two days: the reset was allowed, the check on who was asking was missing.",
                evidence=["SD-26-0155"]),
        ask("read_ticket"),
        ask("propose_fix", action=RESET, note="Requester is the signed-in owner. Password expired; a reset to the "
            "registered contact solves it."),
        ask("finish", what_i_did="proposed a fix", reason="Password resets now stand on Propose, so I do not act. The "
            "requester is the signed-in owner; I put the reset in front of the person working the ticket.",
            lesson="The same ticket I closed this morning is now a proposal: the type lost its rung on the verifier's findings."),
        ask("read_ticket"), ask("look_up_owner"), ask("find_similar_tickets", by="about"),
        ask("read_other_ticket", ticket="SD-26-0145"), ask("read_cases"), ask("confirm_requester"),
        ask("hand_over", to="OT security team", why="The owner, confirmed by second factor, reports a password change "
            "that was not theirs. SD-26-0145 reset this account for another employee without confirmation. Suspected "
            "account takeover: block the sessions first, then reset."),
        ask("finish", what_i_did="handed over", reason="This is not a forgotten password. The account was reset in "
            "SD-26-0145 for someone who is not its owner, and the owner now reports it. That is a suspected attack, "
            "and not mine to resolve.",
            lesson="'Not by me' on an account with a recent reset for another requester is a security incident, not a reset."),
    ],
    "incident-returns": [
        *looks(),
        finding("no", "yes", "yes", "Profile reinstalled as noted. Two days later the same person wrote SD-26-0065 from "
                "the same laptop: the VPN still fails. The first ticket names a certificate error at the gateway.",
                "At plant 07 reinstalling the VPN profile did not hold; the error points at the gateway, not the laptop.",
                evidence=["SD-26-0065"]),
        *looks(), ask("read_cases"),
        finding("no", "yes", "yes", "The same pattern as SD-26-0054: profile reinstalled, and the next day SD-26-0108 "
                "from the same person and laptop. Another requester, the same plant, the same certificate error.",
                "Second requester, same plant, same failed fix: this is one incident, not two tickets.",
                evidence=["SD-26-0108"]),
        ask("read_ticket"), ask("find_similar_tickets", by="group"), ask("read_cases"),
        ask("read_other_ticket", ticket="SD-26-0065"),
        ask("resolve", action=TEMPORARY, note="Temporary VPN certificate installed. The cause is the certificate of the "
            "plant 07 gateway; a permanent fix is proposed."),
        ask("propose_permanent_fix", incident="VPN fails at plant 07 with a certificate error, for several people.",
            tickets=["SD-26-0054"],
            permanent_fix="Renew the certificate of the VPN gateway at plant 07 and put its expiry date under monitoring.",
            instruction="For a VPN certificate error at plant 07, do not reinstall the profile. Install a temporary "
                        "certificate and link the ticket to the problem record until the gateway certificate is renewed.",
            do_not_apply=REINSTALL),
        ask("propose_permanent_fix", incident="VPN fails at plant 07 with a certificate error, for several people.",
            tickets=["SD-26-0054", "SD-26-0104", "SD-26-0065"],
            permanent_fix="Renew the certificate of the VPN gateway at plant 07 and put its expiry date under monitoring.",
            instruction="For a VPN certificate error at plant 07, do not reinstall the profile. Install a temporary "
                        "certificate and link the ticket to the problem record until the gateway certificate is renewed.",
            do_not_apply=REINSTALL),
        ask("finish", what_i_did="resolved", reason="The verifier found that reinstalling the profile did not hold in "
            "SD-26-0054 and SD-26-0104. In SD-26-0065 a temporary certificate did. I applied that, and proposed the "
            "permanent fix for approval.",
            lesson="When a check says the standard fix came back twice, the third ticket gets a different fix and a proposal."),
        ask("read_ticket"), ask("read_cases"),
        ask("resolve", action=REINSTALL, note="VPN profile reinstalled."),
        ask("resolve", action=TEMPORARY, note="Temporary VPN certificate installed, as the standing instruction says. "
            "Linked to the problem record for the plant 07 gateway certificate."),
        ask("finish", what_i_did="resolved", reason="The standing instruction for this incident rules out the reinstall, "
            "and the connector refused it. I installed the temporary certificate.",
            lesson="An approved instruction is enforced, not only read: the old fix is refused for this incident."),
    ],
}
