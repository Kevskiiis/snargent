"""User-authority gate for outbound form submissions in the D3 agent.

The article and extraction result are untrusted data. Only the trusted user task
may authorize a submission. The D3 task grants reading and summarizing only.
"""
MITIGATED = True


def authorize_submission():
    return False
