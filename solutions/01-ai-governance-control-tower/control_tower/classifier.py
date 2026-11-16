"""Risk classification: proposes an EU AI Act tier and the ISO/IEC 42001 control
areas that apply. Rule-based and deterministic in version 0.

This is a PROPOSAL for a human to sign off. It is not legal advice. Article and
control references are the author's reading and must be checked against the
official texts before use in a real company.
"""

# flag -> (tier, basis). Checked top to bottom; the first match wins.
RULES = [
    ("social_scoring", "prohibited", "EU AI Act Art. 5 (prohibited practices)"),
    ("biometric_identification", "high", "EU AI Act Art. 6 and Annex III (biometrics)"),
    ("employment_decisions", "high", "EU AI Act Art. 6 and Annex III (employment)"),
    ("critical_infrastructure", "high", "EU AI Act Art. 6 and Annex III (critical infrastructure)"),
    ("safety_component", "high", "EU AI Act Art. 6(1) (safety component of a regulated product)"),
    ("essential_services_access", "high", "EU AI Act Art. 6 and Annex III (essential services)"),
    ("interacts_with_people", "limited", "EU AI Act Art. 50 (transparency towards people)"),
    ("generates_content", "limited", "EU AI Act Art. 50 (marking of generated content)"),
]

# ISO/IEC 42001:2023 Annex A control areas expected per tier (cumulative).
ISO_42001 = {
    "minimal": ["A.2 AI policy", "A.3 Roles and responsibilities", "A.9 Use of AI systems"],
    "limited": ["A.8 Information for interested parties"],
    "high": [
        "A.4 Resources for AI systems", "A.5 Impact assessment",
        "A.6 AI system life cycle", "A.7 Data for AI systems",
        "A.10 Third-party relationships",
    ],
}
ORDER = ["minimal", "limited", "high", "prohibited"]


def classify(card: dict) -> dict:
    flags = card.get("use_case_flags", {})
    tier, basis = "minimal", "No Annex III use and no direct contact with people"
    for flag, rule_tier, rule_basis in RULES:
        if flags.get(flag):
            tier, basis = rule_tier, rule_basis
            break
    controls: list[str] = []
    for level in ORDER[: min(ORDER.index(tier), 2) + 1]:
        controls += ISO_42001[level]
    return {"agent_id": card["id"], "tier": tier, "basis": basis,
            "iso_42001_controls": controls, "signed_off_by": None}
