"""
handler.py — Claim Segmentation / STP Classification
──────────────────────────────────────────────────────
Rule-based computation of an STP (Straight-Through-Processing) score and
classification for a claim.

Homeowners: reads intake_validation_result_output, writes to stp_classification
            and segmentation_result_output.
Motor:      reads motor_intake_validation_result_output, writes to
            motor_stp_classification and motor_segmentation_result_output.

Motor subrogation differs from HO:
  Third-Party Liability → High  (clear recovery target)
  Collision / Theft     → Medium
  All others            → Low
"""

import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from db import get_db_connection, row_to_dict  # noqa: E402

log = logging.getLogger(__name__)


# ── LOB routing helpers ───────────────────────────────────────────────────────

def _is_motor(lob: str) -> bool:
    return (lob or "").strip().lower() == "motor"

def _readiness_table(lob: str) -> str:
    return "motor_intake_validation_result_output" if _is_motor(lob) else "intake_validation_result_output"

def _stp_table(lob: str) -> str:
    return "motor_stp_classification" if _is_motor(lob) else "stp_classification"

def _seg_table(lob: str) -> str:
    return "motor_segmentation_result_output" if _is_motor(lob) else "segmentation_result_output"


# ── Shared claim lookup (claims table is shared across LOBs) ─────────────────

def get_claim_for_segmentation(claim_number: str) -> dict:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM claims WHERE claim_number = %s", (claim_number,))
        return row_to_dict(cur.fetchone())
    finally:
        conn.close()


def _get_readiness_result(claim_number: str, lob: str = "Homeowners") -> dict:
    """Fetch ClaimReadinessAgent output from the correct LOB table."""
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"SELECT * FROM {_readiness_table(lob)} WHERE claim_number = %s",
            (claim_number,),
        )
        return row_to_dict(cur.fetchone()) or {}
    finally:
        conn.close()


# ── Scoring helpers ───────────────────────────────────────────────────────────

def _compute_readiness(claim: dict, readiness_result: dict) -> int:
    """
    Use completeness_score from ClaimReadinessAgent when available.
    Fall back to a simplified field check if the readiness agent hasn't run yet.
    """
    if readiness_result.get("completeness_score") is not None:
        return int(readiness_result["completeness_score"])
    fields = ["estimated_cost", "severity", "coverage", "loss_type", "location"]
    populated = sum(1 for f in fields if claim.get(f) not in (None, "", 0))
    return int((populated / len(fields)) * 100)


def _compute_fraud_ambiguity(claim: dict, readiness_result: dict) -> str:
    """
    Use fraud_risk from ClaimReadinessAgent when available.
    Fall back to ai_confidence on the claim record.
    """
    fraud_risk = (readiness_result.get("fraud_risk") or "").strip()
    if fraud_risk in ("Low", "Medium", "High"):
        return fraud_risk

    ai_confidence = claim.get("ai_confidence")
    if ai_confidence is not None and ai_confidence < 50:
        return "High"
    if ai_confidence is not None and ai_confidence < 75:
        return "Medium"
    return "Low"


def _compute_subrogation_ho(claim: dict) -> str:
    """Homeowners subrogation: motor/auto/vehicle keywords → High."""
    loss_type = (claim.get("loss_type") or "").lower()
    if "motor" in loss_type or "auto" in loss_type or "vehicle" in loss_type:
        return "High"
    if "liability" in loss_type or "theft" in loss_type:
        return "Medium"
    return "Low"


def _compute_subrogation_motor(claim: dict) -> str:
    """
    Motor subrogation: Third-Party Liability has a clear recovery target → High.
    Collision and Theft may involve partial recovery → Medium.
    Fire, Natural Disaster, Vandalism, Windshield → Low.
    """
    loss_type = (claim.get("loss_type") or "").lower()
    if "third" in loss_type or "liability" in loss_type:
        return "High"
    if "collision" in loss_type or "theft" in loss_type:
        return "Medium"
    return "Low"


def _compute_vis(claim: dict) -> int:
    return 50 if claim.get("assigned_vendor") else 0


# ── Main scoring function ─────────────────────────────────────────────────────

def compute_stp_score(claim_number: str, lob: str = "Homeowners") -> dict:
    claim = get_claim_for_segmentation(claim_number)
    if not claim:
        raise ValueError(f"Claim {claim_number} not found")

    # ── Check for existing result — avoid recomputation ───────────────────────
    existing = get_stp_classification(claim_number, lob=lob)
    if existing and existing.get("stp_category"):
        log.info("Returning existing STP result for %s [LOB=%s]", claim_number, lob)
        return {
            "claim_number": claim_number,
            "lob": lob,
            "stp_id": existing.get("stp_id"),
            "readiness": existing.get("readiness"),
            "fraud_ambiguity": existing.get("fraud_ambiguity"),
            "subrogation": existing.get("subrogation"),
            "vis": existing.get("vis"),
            "stp_score": existing.get("stp_score"),
            "stp_category": existing.get("stp_category"),
            "reused": True,
        }

    # ── Pull readiness/fraud from the correct LOB readiness table ─────────────
    readiness_result = _get_readiness_result(claim_number, lob=lob)

    readiness       = _compute_readiness(claim, readiness_result)
    fraud_ambiguity = _compute_fraud_ambiguity(claim, readiness_result)
    subrogation     = (_compute_subrogation_motor(claim) if _is_motor(lob)
                       else _compute_subrogation_ho(claim))
    vis             = _compute_vis(claim)

    fraud_score = {"Low": 100, "Medium": 60, "High": 20}.get(fraud_ambiguity, 50)
    subro_score = {"Low": 100, "Medium": 60, "High": 20}.get(subrogation, 50)

    stp_score = int(
        readiness * 0.50 + fraud_score * 0.25 + vis * 0.15 + subro_score * 0.10
    )

    coverage        = bool(claim.get("coverage"))
    severity        = (claim.get("severity") or "").lower()
    assigned_vendor = claim.get("assigned_vendor")

    if stp_score >= 85 and coverage and severity in ("low", "medium"):
        stp_category = "Full STP"
    elif stp_score >= 70:
        stp_category = "Fast Track"
    elif assigned_vendor and stp_score >= 50:
        stp_category = "Vendor STP"
    else:
        stp_category = "Manual Review"

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    stp_id = f"STP-{claim_number}-{timestamp}"

    stp_t = _stp_table(lob)
    seg_t = _seg_table(lob)

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            INSERT INTO {stp_t}
              (stp_id, claim_number, readiness, fraud_ambiguity, subrogation, vis, stp_score, stp_category, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (claim_number) DO UPDATE SET
              stp_id          = EXCLUDED.stp_id,
              readiness       = EXCLUDED.readiness,
              fraud_ambiguity = EXCLUDED.fraud_ambiguity,
              subrogation     = EXCLUDED.subrogation,
              vis             = EXCLUDED.vis,
              stp_score       = EXCLUDED.stp_score,
              stp_category    = EXCLUDED.stp_category,
              created_at      = NOW()
            """,
            (stp_id, claim_number, readiness, fraud_ambiguity, subrogation, vis, stp_score, stp_category),
        )
        cur.execute(
            f"""
            INSERT INTO {seg_t}
              (claim_number, severity, complexity, stp_score, recommended_path, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT (claim_number) DO UPDATE SET
              severity         = EXCLUDED.severity,
              complexity       = EXCLUDED.complexity,
              stp_score        = EXCLUDED.stp_score,
              recommended_path = EXCLUDED.recommended_path,
              created_at       = NOW()
            """,
            (claim_number, claim.get("severity"), claim.get("complexity"), stp_score, stp_category),
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return {
        "claim_number": claim_number,
        "lob": lob,
        "stp_id": stp_id,
        "readiness": readiness,
        "fraud_ambiguity": fraud_ambiguity,
        "subrogation": subrogation,
        "vis": vis,
        "stp_score": stp_score,
        "stp_category": stp_category,
        "reused": False,
    }


def get_segmentation_result(claim_number: str, lob: str = "Homeowners") -> dict:
    seg_t = _seg_table(lob)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT s.* FROM {seg_t} s
            JOIN claims c ON c.claim_number = s.claim_number
            WHERE c.claim_number = %s
            ORDER BY s.id DESC LIMIT 1
            """,
            (claim_number,),
        )
        row = row_to_dict(cur.fetchone())
        if not row:
            cur.execute(
                f"SELECT * FROM {seg_t} WHERE claim_number = %s ORDER BY id DESC LIMIT 1",
                (claim_number,),
            )
            row = row_to_dict(cur.fetchone())
        return row
    finally:
        conn.close()


def get_stp_classification(claim_number: str, lob: str = "Homeowners") -> dict:
    stp_t = _stp_table(lob)
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"""
            SELECT s.* FROM {stp_t} s
            JOIN claims c ON c.claim_number = s.claim_number
            WHERE c.claim_number = %s
            ORDER BY s.id DESC LIMIT 1
            """,
            (claim_number,),
        )
        row = row_to_dict(cur.fetchone())
        if not row:
            cur.execute(
                f"SELECT * FROM {stp_t} WHERE claim_number = %s ORDER BY id DESC LIMIT 1",
                (claim_number,),
            )
            row = row_to_dict(cur.fetchone())
        return row
    finally:
        conn.close()
