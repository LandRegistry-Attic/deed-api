from enum import Enum


class DeedStatus(Enum):
    draft = "DRAFT"
    partial = "PARTIALLY-SIGNED"
    superceded = "SUPERCEDED"
    aborted = "ABORTED"
    stopped = "STOPPED"
    all_signed = "ALL-SIGNED"
    effective = "EFFECTIVE"
    submitted = "SUBMITTED"
    stored = "STORED"
    registered = "REGISTERED"
    effective_not_registrar_signed = "EFFECTIVE-NOT-REGISTRAR-SIGNED"
