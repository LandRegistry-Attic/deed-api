from enum import Enum


class DeedStatus(Enum):
    draft = "DRAFT"
    partial = "PARTIALLY-SIGNED"
    superceded = "SUPERCEDED"
    aborted = "ABORTED"
    stopped = "STOPPED"
    all_signed = "ALL-SIGNED"
    effective = "EFFECTIVE"
    effective_not_signed = "EFFECTIVE-NOT-SIGNED"
    submitted = "SUBMITTED"
    stored = "STORED"
    registered = "REGISTERED"
