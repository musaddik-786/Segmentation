# """
# fnol_handler.py
# ───────────────
# DB operations for FNOL submissions, inferences, question log,
# field attribution, and voice/text extractions.
# Uses psycopg2 with RealDictCursor (Azure PostgreSQL).
# """

# import logging
# import random
# from datetime import datetime, timedelta
# from typing import Optional

# import sys
# import os
# sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

# from db import get_db_connection, row_to_dict  # noqa: E402
# from policy_coverage_mcp import guidewire_client  # noqa: E402
# from voice_text_intake_mcp.models import (
#     CreateFnolSubmissionRequest,
#     UpdateFnolSubmissionRequest,
#     SaveVoiceTextExtractionRequest,
#     SaveAiInferencesRequest,
#     LogQuestionAnswerRequest,
#     SaveFieldAttributionRequest,
# )

# log = logging.getLogger(__name__)


# # ──────────────────────────────────────────────────────────────────────────────
# # Loss type canonicalization
# # ──────────────────────────────────────────────────────────────────────────────
# # loss_type must always land in the DB as exactly one of these six values,
# # regardless of how the LLM extraction or a human edit phrased it (e.g.
# # "Fire damage", "water damage", "break-in" all need to collapse down to the
# # canonical spelling below rather than being stored verbatim).
# _CANONICAL_LOSS_TYPES = ["Fire", "Waterdamage", "Hurricane", "burglary", "Explosion", "Earthquake"]

# _LOSS_TYPE_KEYWORD_MAP = {
#     "Fire": ["fire", "burn", "smoke", "arson"],
#     "Waterdamage": ["water", "flood", "leak", "pipe", "damp", "moisture"],
#     "Hurricane": ["hurricane", "storm", "wind", "hail", "tornado", "cyclone", "typhoon"],
#     "burglary": ["burglary", "burglar", "theft", "robbery", "break-in", "break in", "stolen", "intrusion"],
#     "Explosion": ["explosion", "explode", "blast", "detonation"],
#     "Earthquake": ["earthquake", "seismic", "quake", "tremor"],
# }


# def _normalize_loss_type(value):
#     """
#     Maps a freeform loss_type string onto one of _CANONICAL_LOSS_TYPES by
#     keyword match. Already-canonical values pass through unchanged. Falls
#     back to the trimmed original value if nothing matches, so unrecognized
#     input isn't silently discarded.
#     """
#     if value is None:
#         return value
#     trimmed = value.strip()
#     if trimmed in _CANONICAL_LOSS_TYPES:
#         return trimmed
#     lowered = trimmed.lower()
#     for canonical, keywords in _LOSS_TYPE_KEYWORD_MAP.items():
#         if any(keyword in lowered for keyword in keywords):
#             return canonical
#     log.warning("loss_type %r did not match any canonical category — storing as-is", value)
#     return trimmed


# # ──────────────────────────────────────────────────────────────────────────────
# # FNOL Submissions
# # ──────────────────────────────────────────────────────────────────────────────

# def cleanup_draft_fnols_for_policy(policy_number: str, conn=None) -> int:
#     """
#     Delete all draft fnol_submissions for *policy_number* and their child rows.
#     Called automatically before creating a new FNOL so reruns and error cases
#     don't accumulate orphaned draft data.

#     Returns the number of draft submissions removed.
#     """
#     _own_conn = conn is None
#     if _own_conn:
#         conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             "SELECT id FROM fnol_submissions WHERE policy_number = %s AND status = 'draft'",
#             (policy_number,),
#         )
#         draft_ids = [r["id"] for r in cur.fetchall()]
#         if not draft_ids:
#             return 0

#         placeholders = ",".join("%s" for _ in draft_ids)
#         for child_table in (
#             "fnol_ai_inferences",
#             "fnol_voice_text_extraction",
#             "fnol_mandatory_question_log",
#             "fnol_field_attribution",
#         ):
#             cur.execute(
#                 f"DELETE FROM {child_table} WHERE fnol_id IN ({placeholders})",
#                 draft_ids,
#             )
#         cur.execute(
#             f"DELETE FROM fnol_submissions WHERE id IN ({placeholders})",
#             draft_ids,
#         )
#         if _own_conn:
#             conn.commit()
#         log.info("Cleaned up %d draft FNOL(s) for policy %s", len(draft_ids), policy_number)
#         return len(draft_ids)
#     except Exception:
#         if _own_conn:
#             conn.rollback()
#         log.exception("cleanup_draft_fnols_for_policy failed for policy %s", policy_number)
#         raise
#     finally:
#         if _own_conn:
#             conn.close()


# def create_fnol_submission(req: CreateFnolSubmissionRequest) -> dict:
#     # Auto-generate fnol_number if the LLM didn't supply one (#6)
#     if not req.fnol_number:
#         req.fnol_number = f"FNOL-{datetime.now().year}-{random.randint(10000, 99999)}"
#     req.loss_type = _normalize_loss_type(req.loss_type)
#     conn = get_db_connection()
#     try:
#         # Wipe any previous draft FNOLs for this policy so reruns start clean.
#         cleanup_draft_fnols_for_policy(req.policy_number, conn=conn)
#         cur = conn.cursor()
#         cur.execute(
#             """
#             INSERT INTO fnol_submissions (
#                 fnol_number, policy_number, policyholder_name, policyholder_address,
#                 policy_effective_date, policy_expiration_date,
#                 loss_type, loss_type_source, cause_of_loss, cause_of_loss_source,
#                 date_of_loss, date_of_loss_source, time_of_loss, time_of_loss_source,
#                 area_affected, area_affected_source, occupancy_at_loss, occupancy_at_loss_source,
#                 sudden_vs_gradual, emotional_context, severity, urgency_indicator,
#                 voice_transcript, text_input, overall_confidence, confidence_notes,
#                 status, created_at, updated_at
#             ) VALUES (
#                 %s,%s,%s,%s,%s,%s,%s,'ai_inferred',%s,'ai_inferred',
#                 %s,'ai_inferred',%s,'ai_inferred',%s,'ai_inferred',%s,'ai_inferred',
#                 %s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW()
#             ) RETURNING *
#             """,
#             (
#                 req.fnol_number, req.policy_number, req.policyholder_name, req.policyholder_address,
#                 req.policy_effective_date, req.policy_expiration_date,
#                 req.loss_type, req.cause_of_loss,
#                 req.date_of_loss, req.time_of_loss,
#                 req.area_affected,
#                 req.occupancy_at_loss,
#                 req.sudden_vs_gradual, req.emotional_context, req.severity, req.urgency_indicator,
#                 req.voice_transcript, req.text_input, req.overall_confidence, req.confidence_notes,
#                 req.status or "draft",
#             ),
#         )
#         result = cur.fetchone()
#         conn.commit()
#         return row_to_dict(result)
#     except Exception:
#         conn.rollback()
#         log.exception("create_fnol_submission failed")
#         raise
#     finally:
#         conn.close()


# def get_fnol_submission_by_id(fnol_id: int) -> Optional[dict]:
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM fnol_submissions WHERE id = %s", (fnol_id,))
#         return row_to_dict(cur.fetchone())
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         conn.close()


# def get_fnol_submission_by_policy(policy_number: str) -> list:
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             "SELECT * FROM fnol_submissions WHERE policy_number = %s ORDER BY created_at DESC",
#             (policy_number,),
#         )
#         return row_to_dict(cur.fetchall())
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         conn.close()


# # ──────────────────────────────────────────────────────────────────────────────
# # Overall Confidence — cumulative, not per-turn
# # ──────────────────────────────────────────────────────────────────────────────
# # The LLM's raw per-extraction "overall_confidence" only ever reflects a
# # single turn's isolated message (e.g. a bare "yes" answering an occupancy
# # question legitimately extracts almost nothing on its own), so trusting it
# # directly makes the score collapse toward 0 as the conversation progresses
# # even though the cumulative record is well-populated. Recomputed here from
# # the CURRENT full record every time any field changes.
# _MANDATORY_CONFIDENCE_FIELDS = {
#     "loss_type", "cause_of_loss", "date_of_loss", "time_of_loss",
#     "area_affected", "occupancy_at_loss", "sudden_vs_gradual", "severity",
# }
# _OPTIONAL_CONFIDENCE_FIELDS = {"emotional_context", "urgency_indicator"}
# _MANDATORY_CONF_WEIGHT = 3.0
# _OPTIONAL_CONF_WEIGHT = 1.0
# # A value the policyholder explicitly confirmed, or a human edited, carries no
# # ambiguity at all — there's nothing more certain than the source stating it
# # directly, so it's scored as full confidence regardless of extraction history.
# _DEFINITIVE_SOURCES = {"customer_confirmed", "human_edited"}
# # A field can hold a value with no confidence on file (e.g. it was set via a
# # direct update_fnol_submission call rather than extract_fnol_fields_from_text,
# # and its source isn't one of the definitive ones above) — treat as reasonably
# # but not fully confident rather than penalizing it as if it were unrated/missing.
# _UNRATED_VALUE_CONFIDENCE = 75.0


# def _compute_overall_confidence(fnol_id: int, current_row: dict, incoming: dict) -> int:
#     """
#     Weighted average confidence across the loss-detail fields, reflecting the
#     FULL current record (existing DB row merged with this update) — not a
#     single turn's isolated extraction. Mandatory fields are weighted 3x.
#     """
#     merged = {**current_row, **incoming}

#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             """
#             SELECT DISTINCT ON (field_name) field_name, confidence
#             FROM fnol_ai_inferences
#             WHERE fnol_id = %s
#             ORDER BY field_name, id DESC
#             """,
#             (fnol_id,),
#         )
#         latest_confidence = {
#             r["field_name"]: r["confidence"] for r in cur.fetchall() if r.get("confidence") is not None
#         }
#     except Exception:
#         conn.rollback()
#         latest_confidence = {}
#     finally:
#         conn.close()

#     total_weight = 0.0
#     weighted_sum = 0.0
#     weighted_fields = (
#         [(f, _MANDATORY_CONF_WEIGHT) for f in _MANDATORY_CONFIDENCE_FIELDS]
#         + [(f, _OPTIONAL_CONF_WEIGHT) for f in _OPTIONAL_CONFIDENCE_FIELDS]
#     )
#     for field_name, weight in weighted_fields:
#         value = merged.get(field_name)
#         source = merged.get(f"{field_name}_source")
#         if value is None or (isinstance(value, str) and not value.strip()):
#             field_conf = 0.0
#         elif source in _DEFINITIVE_SOURCES:
#             field_conf = 100.0
#         elif field_name in latest_confidence:
#             field_conf = float(latest_confidence[field_name])
#         else:
#             field_conf = _UNRATED_VALUE_CONFIDENCE
#         total_weight += weight
#         weighted_sum += weight * field_conf

#     if total_weight == 0.0:
#         return 0
#     return int(round(weighted_sum / total_weight))


# _UPDATABLE_COLUMNS = {
#     "policy_number", "policyholder_name", "policyholder_address",
#     "loss_type", "loss_type_source",
#     "cause_of_loss", "cause_of_loss_source",
#     "date_of_loss", "date_of_loss_source",
#     "time_of_loss", "time_of_loss_source",
#     "area_affected", "area_affected_source",
#     "occupancy_at_loss", "occupancy_at_loss_source",
#     "sudden_vs_gradual", "sudden_vs_gradual_source",
#     "emotional_context", "emotional_context_source",
#     "severity", "severity_source",
#     "urgency_indicator", "urgency_indicator_source",
#     "voice_transcript", "text_input", "overall_confidence",
#     "confidence_notes", "status", "estimated_cost",
# }


# def update_fnol_submission(fnol_id: int, req: UpdateFnolSubmissionRequest) -> Optional[dict]:
#     raw = req.model_dump(exclude_none=True)
#     # Whitelist: only allow known columns to reach the dynamic SQL (#5)
#     fields = {k: v for k, v in raw.items() if k in _UPDATABLE_COLUMNS}
#     if not fields:
#         return get_fnol_submission_by_id(fnol_id)

#     if "loss_type" in fields:
#         fields["loss_type"] = _normalize_loss_type(fields["loss_type"])

#     # overall_confidence is derived, not settable — always recompute it from
#     # the cumulative record rather than trusting a caller-supplied value (e.g.
#     # a single turn's raw LLM self-report), so it reflects the whole FNOL's
#     # current state on every field change regardless of which code path
#     # triggered it (extraction auto-persist or a direct orchestrator update).
#     current = get_fnol_submission_by_id(fnol_id) or {}
#     fields["overall_confidence"] = _compute_overall_confidence(fnol_id, current, fields)

#     set_clauses = ", ".join(f"{k} = %s" for k in fields)
#     values = list(fields.values()) + [fnol_id]

#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             f"UPDATE fnol_submissions SET {set_clauses}, updated_at = NOW() WHERE id = %s RETURNING *",
#             values,
#         )
#         result = cur.fetchone()
#         conn.commit()
#         return row_to_dict(result)
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         conn.close()


# # ── Guidewire ClaimCenter — Claim Creation ────────────────────────────────────
# # Hardcoded per the ClaimCenter sandbox contract — this PoC always reports as
# # the same jurisdiction/reporter/contact regardless of the actual claim.
# _GW_JURISDICTION_CODE = "IL"
# _GW_REPORTER_FIRST_NAME = "Ken"
# _GW_REPORTER_LAST_NAME = "Darion"


# def _to_gw_loss_datetime(date_of_loss, time_of_loss) -> str:
#     """
#     Combines fnol_submissions' date_of_loss ("YYYY-MM-DD") and time_of_loss
#     ("HH:MM") text columns into the ISO-8601 UTC datetime ClaimCenter requires
#     for lossDate (e.g. "2026-01-18T00:30:00.000Z"). Defaults to midnight if
#     time_of_loss is missing/unparsable.

#     ClaimCenter rejects a lossDate that isn't strictly before its own clock
#     (server runs in UTC, matching datetime.utcnow() here). A same-day loss
#     reported with a time_of_loss that hasn't happened yet in UTC (e.g. the
#     policyholder describes the loss as "this morning" but files well before
#     that time today) would otherwise get rejected outright, so it's clamped
#     a few minutes into the past instead of failing the whole submission.
#     """
#     if not date_of_loss:
#         raise ValueError("date_of_loss is required to create a Guidewire claim")
#     date_part = str(date_of_loss).strip()[:10]
#     time_part = "00:00"
#     candidate = str(time_of_loss).strip()[:5] if time_of_loss else ""
#     if len(candidate) == 5 and candidate[2] == ":":
#         time_part = candidate
#     try:
#         dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
#     except ValueError as exc:
#         raise ValueError(
#             f"date_of_loss={date_of_loss!r} / time_of_loss={time_of_loss!r} "
#             f"not in the expected format: {exc}"
#         )

#     now_utc = datetime.utcnow()
#     if dt >= now_utc:
#         log.warning(
#             "lossDate %s is not before the current UTC time %s — clamping so "
#             "Guidewire's date constraint doesn't reject the claim",
#             dt.isoformat(), now_utc.isoformat(),
#         )
#         dt = now_utc - timedelta(minutes=5)

#     return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


# def _build_guidewire_claim_payload(fnol: dict, policy_row: dict) -> dict:
#     policy_row = policy_row or {}
#     return {
#         "data": {
#             "attributes": {
#                 "policyNumber": fnol.get("policy_number"),
#                 "lossDate": _to_gw_loss_datetime(fnol.get("date_of_loss"), fnol.get("time_of_loss")),
#                 "description": fnol.get("cause_of_loss") or "Reported via FNOL intake",
#                 "jurisdiction": {"code": _GW_JURISDICTION_CODE},
#                 "lossCause": {"code": (fnol.get("loss_type") or "").strip().lower() or "other"},
#                 "lossLocation": {
#                     "addressLine1": fnol.get("policyholder_address") or "",
#                     "city": policy_row.get("city") or "",
#                     "country": policy_row.get("country") or "US",
#                     "postalCode": policy_row.get("postal_code") or "",
#                     "state": {"code": _GW_JURISDICTION_CODE},
#                 },
#                 "reportedByType": {"code": "self"},
#                 "howReported": {"code": "phone"},
#                 "reporter": {"refid": "reporterId"},
#                 "mainContactType": {"code": "self"},
#             }
#         },
#         "included": {
#             "ClaimContact": [
#                 {
#                     "attributes": {
#                         "contactSubtype": "Person",
#                         "firstName": _GW_REPORTER_FIRST_NAME,
#                         "lastName": _GW_REPORTER_LAST_NAME,
#                     },
#                     "method": "post",
#                     "refid": "reporterId",
#                     "uri": "/claim/v1/claims/this/contacts",
#                 }
#             ]
#         },
#     }


# def _create_claim_in_guidewire(fnol: dict, policy_row: dict) -> str:
#     """
#     Drafts then submits a claim in Guidewire ClaimCenter for this FNOL.
#     Returns the FINAL claim number from the /submit response — the draft
#     response's claimNumber is a placeholder and is intentionally ignored.
#     """
#     payload = _build_guidewire_claim_payload(fnol, policy_row)
#     draft = guidewire_client.create_claim(payload)
#     draft_claim_id = (draft.get("data") or {}).get("attributes", {}).get("id")
#     if not draft_claim_id:
#         raise ValueError(f"Guidewire claim draft response missing id: {draft}")

#     submitted = guidewire_client.submit_claim(draft_claim_id)
#     claim_number = (submitted.get("data") or {}).get("attributes", {}).get("claimNumber")
#     if not claim_number:
#         raise ValueError(f"Guidewire claim submit response missing claimNumber: {submitted}")
#     return claim_number


# def submit_fnol(fnol_id: int) -> dict:
#     """
#     Marks an FNOL as submitted, sets submitted_at timestamp, and creates
#     claims / claims_master / claim_journey_master records if none exist
#     for the policy yet. The claim_number is issued by Guidewire ClaimCenter
#     (draft + submit) rather than generated locally — if either ClaimCenter
#     call fails, the FNOL is left unsubmitted so the user can retry.
#     """
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()

#         cur.execute("SELECT * FROM fnol_submissions WHERE id = %s", (fnol_id,))
#         fnol = row_to_dict(cur.fetchone())   # use row_to_dict consistently (#3)
#         if not fnol:
#             raise ValueError(f"FNOL with id={fnol_id} not found")

#         pd_row = {}
#         claim_number = None
#         if fnol.get("policy_number"):
#             cur.execute(
#                 "SELECT coverage_limit, deductible, city, country, postal_code "
#                 "FROM policy_details WHERE policy_number = %s LIMIT 1",
#                 (fnol["policy_number"],),
#             )
#             pd_row = cur.fetchone() or {}

#             # Talk to Guidewire BEFORE mutating any local state — if this
#             # raises, the FNOL stays exactly as it was and submission can be
#             # retried from the UI instead of getting stuck half-submitted.
#             claim_number = _create_claim_in_guidewire(fnol, pd_row)

#         cur.execute(
#             """
#             UPDATE fnol_submissions
#             SET status = 'submitted', submitted_at = NOW(), updated_at = NOW()
#             WHERE id = %s
#             RETURNING *
#             """,
#             (fnol_id,),
#         )
#         updated = row_to_dict(cur.fetchone())

#         if claim_number:
#             cur.execute(
#                 """
#                 INSERT INTO claims (
#                     claim_number, policyholder_name, policy_number,
#                     loss_type, short_description, severity, estimated_cost, status,
#                     date_of_loss, location, ai_confidence, filed_at
#                 ) VALUES (%s,%s,%s,%s,%s,%s,%s, 'Open', %s,%s,%s, NOW())
#                 RETURNING id
#                 """,
#                 (
#                     claim_number,
#                     fnol.get("policyholder_name") or "Unknown",
#                     fnol["policy_number"],
#                     fnol.get("loss_type") or "Unknown",
#                     fnol.get("cause_of_loss") or "Reported via FNOL intake",
#                     fnol.get("severity") or "Medium",
#                     fnol.get("estimated_cost"),
#                     fnol.get("date_of_loss"),
#                     fnol.get("policyholder_address"),
#                     fnol.get("overall_confidence"),
#                 ),
#             )
#             claim_id = cur.fetchone()["id"]

#             p_coverage_limit = pd_row["coverage_limit"] if pd_row.get("coverage_limit") else 0
#             p_deductible = pd_row["deductible"] if pd_row.get("deductible") else 0

#             cur.execute(
#                 """
#                 INSERT INTO claims_master (
#                     claim_number, policyholder_name, policy_number, loss_type,
#                     date_of_loss, coverage_limit, deductible, status
#                 ) VALUES (%s,%s,%s,%s,%s,%s,%s, 'Open')
#                 """,
#                 (
#                     claim_number,
#                     fnol.get("policyholder_name") or "Unknown",
#                     fnol["policy_number"],
#                     fnol.get("loss_type") or "Unknown",
#                     fnol.get("date_of_loss"),
#                     p_coverage_limit,
#                     p_deductible,
#                 ),
#             )

#             cur.execute(
#                 """
#                 INSERT INTO claim_journey_master (
#                     claim_id, claim_number, current_stage, current_stage_name,
#                     sub_status, overall_sla_status
#                 ) VALUES (%s,%s,1,'Claim Initiated','Under Review','on_track')
#                 """,
#                 (claim_id, claim_number),
#             )

#         conn.commit()
#         return {"fnol": updated, "claim_number": claim_number, "status": "submitted"}
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         conn.close()


# # ──────────────────────────────────────────────────────────────────────────────
# # Mandatory Fields Reference
# # ──────────────────────────────────────────────────────────────────────────────

# def get_mandatory_fields() -> list:
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute("SELECT * FROM fnol_mandatory_fields ORDER BY display_order")
#         return row_to_dict(cur.fetchall())
#     finally:
#         conn.close()


# # ──────────────────────────────────────────────────────────────────────────────
# # Voice / Text Extractions
# # ──────────────────────────────────────────────────────────────────────────────

# def save_voice_text_extraction(req: SaveVoiceTextExtractionRequest) -> dict:
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             """
#             INSERT INTO fnol_voice_text_extraction (
#                 fnol_id, input_type, raw_input, transcribed_text,
#                 extracted_loss_type, extracted_cause, extracted_area,
#                 extracted_temporal, sudden_gradual_signal, emotional_context,
#                 extraction_confidence, created_at
#             ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
#             RETURNING *
#             """,
#             (
#                 req.fnol_id, req.input_type, req.raw_input, req.transcribed_text,
#                 req.extracted_loss_type, req.extracted_cause, req.extracted_area,
#                 req.extracted_temporal, req.sudden_gradual_signal, req.emotional_context,
#                 req.extraction_confidence,
#             ),
#         )
#         result = cur.fetchone()
#         conn.commit()
#         return row_to_dict(result)
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         conn.close()


# def get_voice_text_extractions(fnol_id: int) -> list:
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             "SELECT * FROM fnol_voice_text_extraction WHERE fnol_id = %s ORDER BY created_at",
#             (fnol_id,),
#         )
#         return row_to_dict(cur.fetchall())
#     finally:
#         conn.close()


# # ──────────────────────────────────────────────────────────────────────────────
# # AI Inferences
# # ──────────────────────────────────────────────────────────────────────────────

# def save_ai_inferences(req: SaveAiInferencesRequest) -> list:
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         created = []
#         for item in req.inferences:
#             cur.execute(
#                 """
#                 INSERT INTO fnol_ai_inferences (
#                     fnol_id, field_name, inferred_value, confidence,
#                     source, source_details, customer_confirmed, inferred_at
#                 ) VALUES (%s,%s,%s,%s,%s,%s,0,NOW())
#                 RETURNING *
#                 """,
#                 (
#                     req.fnol_id, item.field_name, item.inferred_value,
#                     item.confidence, item.source, item.source_details,
#                 ),
#             )
#             created.append(row_to_dict(cur.fetchone()))
#         conn.commit()
#         return created
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         conn.close()


# # ──────────────────────────────────────────────────────────────────────────────
# # Mandatory Question Log
# # ──────────────────────────────────────────────────────────────────────────────

# def log_question_answer(req: LogQuestionAnswerRequest) -> dict:
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         answered_at = datetime.utcnow().isoformat() if req.answer_text else None
#         cur.execute(
#             """
#             INSERT INTO fnol_mandatory_question_log (
#                 fnol_id, question_text, field_name, answer_text,
#                 answer_type, was_skipped, question_order,
#                 asked_at, answered_at
#             ) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),%s)
#             RETURNING *
#             """,
#             (
#                 req.fnol_id, req.question_text, req.field_name,
#                 req.answer_text, req.answer_type, int(req.was_skipped or False),
#                 req.question_order or 0, answered_at,
#             ),
#         )
#         result = cur.fetchone()
#         conn.commit()
#         return row_to_dict(result)
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         conn.close()


# def get_question_log(fnol_id: int) -> list:
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         cur.execute(
#             "SELECT * FROM fnol_mandatory_question_log WHERE fnol_id = %s ORDER BY question_order",
#             (fnol_id,),
#         )
#         return row_to_dict(cur.fetchall())
#     finally:
#         conn.close()


# # ──────────────────────────────────────────────────────────────────────────────
# # Field Attribution
# # ──────────────────────────────────────────────────────────────────────────────

# def save_field_attribution(req: SaveFieldAttributionRequest) -> list:
#     conn = get_db_connection()
#     try:
#         cur = conn.cursor()
#         created = []
#         for item in req.attributions:
#             cur.execute(
#                 """
#                 INSERT INTO fnol_field_attribution (
#                     fnol_id, field_name, field_label, field_value, source,
#                     confidence, was_edited, was_confirmed, original_value,
#                     edited_value, created_at
#                 ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
#                 RETURNING *
#                 """,
#                 (
#                     req.fnol_id, item.field_name, item.field_label,
#                     item.field_value, item.source, item.confidence,
#                     int(item.was_edited or False), int(item.was_confirmed or False),
#                     item.original_value, item.edited_value,
#                 ),
#             )
#             created.append(row_to_dict(cur.fetchone()))
#         conn.commit()
#         return created
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         conn.close()





"""
fnol_handler.py
───────────────
DB operations for FNOL submissions, inferences, question log,
field attribution, and voice/text extractions.
Uses psycopg2 with RealDictCursor (Azure PostgreSQL).
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Optional

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "common"))

from db import get_db_connection, row_to_dict  # noqa: E402
from policy_coverage_mcp import guidewire_client  # noqa: E402
from policy_coverage_mcp.handler import LOCAL_ONLY_POLICY_NUMBERS  # noqa: E402
from voice_text_intake_mcp.models import (
    CreateFnolSubmissionRequest,
    UpdateFnolSubmissionRequest,
    SaveVoiceTextExtractionRequest,
    SaveAiInferencesRequest,
    LogQuestionAnswerRequest,
    SaveFieldAttributionRequest,
)

log = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Loss type canonicalization
# ──────────────────────────────────────────────────────────────────────────────
# loss_type must always land in the DB as exactly one of these six values,
# regardless of how the LLM extraction or a human edit phrased it (e.g.
# "Fire damage", "water damage", "break-in" all need to collapse down to the
# canonical spelling below rather than being stored verbatim).
_CANONICAL_LOSS_TYPES = ["Fire", "Waterdamage", "Hurricane", "burglary", "Explosion", "Earthquake"]

_LOSS_TYPE_KEYWORD_MAP = {
    "Fire": ["fire", "burn", "smoke", "arson"],
    "Waterdamage": ["water", "flood", "leak", "pipe", "damp", "moisture"],
    "Hurricane": ["hurricane", "storm", "wind", "hail", "tornado", "cyclone", "typhoon"],
    "burglary": ["burglary", "burglar", "theft", "robbery", "break-in", "break in", "stolen", "intrusion"],
    "Explosion": ["explosion", "explode", "blast", "detonation"],
    "Earthquake": ["earthquake", "seismic", "quake", "tremor"],
}


def _normalize_loss_type(value):
    """
    Maps a freeform loss_type string onto one of _CANONICAL_LOSS_TYPES by
    keyword match. Already-canonical values pass through unchanged. Falls
    back to the trimmed original value if nothing matches, so unrecognized
    input isn't silently discarded.
    """
    if value is None:
        return value
    trimmed = value.strip()
    if trimmed in _CANONICAL_LOSS_TYPES:
        return trimmed
    lowered = trimmed.lower()
    for canonical, keywords in _LOSS_TYPE_KEYWORD_MAP.items():
        if any(keyword in lowered for keyword in keywords):
            return canonical
    log.warning("loss_type %r did not match any canonical category — storing as-is", value)
    return trimmed


# ──────────────────────────────────────────────────────────────────────────────
# FNOL Submissions
# ──────────────────────────────────────────────────────────────────────────────

def cleanup_draft_fnols_for_policy(policy_number: str, conn=None) -> int:
    """
    Delete all draft fnol_submissions for *policy_number* and their child rows.
    Called automatically before creating a new FNOL so reruns and error cases
    don't accumulate orphaned draft data.

    Returns the number of draft submissions removed.
    """
    _own_conn = conn is None
    if _own_conn:
        conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT id FROM fnol_submissions WHERE policy_number = %s AND status = 'draft'",
            (policy_number,),
        )
        draft_ids = [r["id"] for r in cur.fetchall()]
        if not draft_ids:
            return 0

        placeholders = ",".join("%s" for _ in draft_ids)
        for child_table in (
            "fnol_ai_inferences",
            "fnol_voice_text_extraction",
            "fnol_mandatory_question_log",
            "fnol_field_attribution",
        ):
            cur.execute(
                f"DELETE FROM {child_table} WHERE fnol_id IN ({placeholders})",
                draft_ids,
            )
        cur.execute(
            f"DELETE FROM fnol_submissions WHERE id IN ({placeholders})",
            draft_ids,
        )
        if _own_conn:
            conn.commit()
        log.info("Cleaned up %d draft FNOL(s) for policy %s", len(draft_ids), policy_number)
        return len(draft_ids)
    except Exception:
        if _own_conn:
            conn.rollback()
        log.exception("cleanup_draft_fnols_for_policy failed for policy %s", policy_number)
        raise
    finally:
        if _own_conn:
            conn.close()


def create_fnol_submission(req: CreateFnolSubmissionRequest) -> dict:
    # Auto-generate fnol_number if the LLM didn't supply one (#6)
    if not req.fnol_number:
        req.fnol_number = f"FNOL-{datetime.now().year}-{random.randint(10000, 99999)}"
    req.loss_type = _normalize_loss_type(req.loss_type)
    conn = get_db_connection()
    try:
        # Wipe any previous draft FNOLs for this policy so reruns start clean.
        cleanup_draft_fnols_for_policy(req.policy_number, conn=conn)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO fnol_submissions (
                fnol_number, policy_number, policyholder_name, policyholder_address,
                policy_effective_date, policy_expiration_date,
                loss_type, loss_type_source, cause_of_loss, cause_of_loss_source,
                date_of_loss, date_of_loss_source, time_of_loss, time_of_loss_source,
                area_affected, area_affected_source, occupancy_at_loss, occupancy_at_loss_source,
                sudden_vs_gradual, emotional_context, severity, urgency_indicator,
                voice_transcript, text_input, overall_confidence, confidence_notes,
                status, created_at, updated_at
            ) VALUES (
                %s,%s,%s,%s,%s,%s,%s,'ai_inferred',%s,'ai_inferred',
                %s,'ai_inferred',%s,'ai_inferred',%s,'ai_inferred',%s,'ai_inferred',
                %s,%s,%s,%s,%s,%s,%s,%s,%s,NOW(),NOW()
            ) RETURNING *
            """,
            (
                req.fnol_number, req.policy_number, req.policyholder_name, req.policyholder_address,
                req.policy_effective_date, req.policy_expiration_date,
                req.loss_type, req.cause_of_loss,
                req.date_of_loss, req.time_of_loss,
                req.area_affected,
                req.occupancy_at_loss,
                req.sudden_vs_gradual, req.emotional_context, req.severity, req.urgency_indicator,
                req.voice_transcript, req.text_input, req.overall_confidence, req.confidence_notes,
                req.status or "draft",
            ),
        )
        result = cur.fetchone()
        conn.commit()
        return row_to_dict(result)
    except Exception:
        conn.rollback()
        log.exception("create_fnol_submission failed")
        raise
    finally:
        conn.close()


def get_fnol_submission_by_id(fnol_id: int) -> Optional[dict]:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM fnol_submissions WHERE id = %s", (fnol_id,))
        return row_to_dict(cur.fetchone())
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_fnol_submission_by_policy(policy_number: str) -> list:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM fnol_submissions WHERE policy_number = %s ORDER BY created_at DESC",
            (policy_number,),
        )
        return row_to_dict(cur.fetchall())
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# Overall Confidence — cumulative, not per-turn
# ──────────────────────────────────────────────────────────────────────────────
# The LLM's raw per-extraction "overall_confidence" only ever reflects a
# single turn's isolated message (e.g. a bare "yes" answering an occupancy
# question legitimately extracts almost nothing on its own), so trusting it
# directly makes the score collapse toward 0 as the conversation progresses
# even though the cumulative record is well-populated. Recomputed here from
# the CURRENT full record every time any field changes.
_MANDATORY_CONFIDENCE_FIELDS = {
    "loss_type", "cause_of_loss", "date_of_loss", "time_of_loss",
    "area_affected", "occupancy_at_loss", "sudden_vs_gradual", "severity",
}
_OPTIONAL_CONFIDENCE_FIELDS = {"emotional_context", "urgency_indicator"}
_MANDATORY_CONF_WEIGHT = 3.0
_OPTIONAL_CONF_WEIGHT = 1.0
# A value the policyholder explicitly confirmed, or a human edited, carries no
# ambiguity at all — there's nothing more certain than the source stating it
# directly, so it's scored as full confidence regardless of extraction history.
_DEFINITIVE_SOURCES = {"customer_confirmed", "human_edited"}
# A field can hold a value with no confidence on file (e.g. it was set via a
# direct update_fnol_submission call rather than extract_fnol_fields_from_text,
# and its source isn't one of the definitive ones above) — treat as reasonably
# but not fully confident rather than penalizing it as if it were unrated/missing.
_UNRATED_VALUE_CONFIDENCE = 75.0


def _compute_overall_confidence(fnol_id: int, current_row: dict, incoming: dict) -> int:
    """
    Weighted average confidence across the loss-detail fields, reflecting the
    FULL current record (existing DB row merged with this update) — not a
    single turn's isolated extraction. Mandatory fields are weighted 3x.
    """
    merged = {**current_row, **incoming}

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT DISTINCT ON (field_name) field_name, confidence
            FROM fnol_ai_inferences
            WHERE fnol_id = %s
            ORDER BY field_name, id DESC
            """,
            (fnol_id,),
        )
        latest_confidence = {
            r["field_name"]: r["confidence"] for r in cur.fetchall() if r.get("confidence") is not None
        }
    except Exception:
        conn.rollback()
        latest_confidence = {}
    finally:
        conn.close()

    total_weight = 0.0
    weighted_sum = 0.0
    weighted_fields = (
        [(f, _MANDATORY_CONF_WEIGHT) for f in _MANDATORY_CONFIDENCE_FIELDS]
        + [(f, _OPTIONAL_CONF_WEIGHT) for f in _OPTIONAL_CONFIDENCE_FIELDS]
    )
    for field_name, weight in weighted_fields:
        value = merged.get(field_name)
        source = merged.get(f"{field_name}_source")
        if value is None or (isinstance(value, str) and not value.strip()):
            field_conf = 0.0
        elif source in _DEFINITIVE_SOURCES:
            field_conf = 100.0
        elif field_name in latest_confidence:
            field_conf = float(latest_confidence[field_name])
        else:
            field_conf = _UNRATED_VALUE_CONFIDENCE
        total_weight += weight
        weighted_sum += weight * field_conf

    if total_weight == 0.0:
        return 0
    return int(round(weighted_sum / total_weight))


_UPDATABLE_COLUMNS = {
    "policy_number", "policyholder_name", "policyholder_address",
    "loss_type", "loss_type_source",
    "cause_of_loss", "cause_of_loss_source",
    "date_of_loss", "date_of_loss_source",
    "time_of_loss", "time_of_loss_source",
    "area_affected", "area_affected_source",
    "occupancy_at_loss", "occupancy_at_loss_source",
    "sudden_vs_gradual", "sudden_vs_gradual_source",
    "emotional_context", "emotional_context_source",
    "severity", "severity_source",
    "urgency_indicator", "urgency_indicator_source",
    "voice_transcript", "text_input", "overall_confidence",
    "confidence_notes", "status", "estimated_cost",
}


def update_fnol_submission(fnol_id: int, req: UpdateFnolSubmissionRequest) -> Optional[dict]:
    raw = req.model_dump(exclude_none=True)
    # Whitelist: only allow known columns to reach the dynamic SQL (#5)
    fields = {k: v for k, v in raw.items() if k in _UPDATABLE_COLUMNS}
    if not fields:
        return get_fnol_submission_by_id(fnol_id)

    if "loss_type" in fields:
        fields["loss_type"] = _normalize_loss_type(fields["loss_type"])

    # overall_confidence is derived, not settable — always recompute it from
    # the cumulative record rather than trusting a caller-supplied value (e.g.
    # a single turn's raw LLM self-report), so it reflects the whole FNOL's
    # current state on every field change regardless of which code path
    # triggered it (extraction auto-persist or a direct orchestrator update).
    current = get_fnol_submission_by_id(fnol_id) or {}
    fields["overall_confidence"] = _compute_overall_confidence(fnol_id, current, fields)

    set_clauses = ", ".join(f"{k} = %s" for k in fields)
    values = list(fields.values()) + [fnol_id]

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE fnol_submissions SET {set_clauses}, updated_at = NOW() WHERE id = %s RETURNING *",
            values,
        )
        result = cur.fetchone()
        conn.commit()
        return row_to_dict(result)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Guidewire ClaimCenter — Claim Creation ────────────────────────────────────
# Hardcoded per the ClaimCenter sandbox contract — this PoC always reports as
# the same jurisdiction/reporter/contact regardless of the actual claim.
_GW_JURISDICTION_CODE = "IL"
_GW_REPORTER_FIRST_NAME = "Ken"
_GW_REPORTER_LAST_NAME = "Darion"


def _to_gw_loss_datetime(date_of_loss, time_of_loss) -> str:
    """
    Combines fnol_submissions' date_of_loss ("YYYY-MM-DD") and time_of_loss
    ("HH:MM") text columns into the ISO-8601 UTC datetime ClaimCenter requires
    for lossDate (e.g. "2026-01-18T00:30:00.000Z"). Defaults to midnight if
    time_of_loss is missing/unparsable.

    ClaimCenter rejects a lossDate that isn't strictly before its own clock
    (server runs in UTC, matching datetime.utcnow() here). A same-day loss
    reported with a time_of_loss that hasn't happened yet in UTC (e.g. the
    policyholder describes the loss as "this morning" but files well before
    that time today) would otherwise get rejected outright, so it's clamped
    a few minutes into the past instead of failing the whole submission.
    """
    if not date_of_loss:
        raise ValueError("date_of_loss is required to create a Guidewire claim")
    date_part = str(date_of_loss).strip()[:10]
    time_part = "00:00"
    candidate = str(time_of_loss).strip()[:5] if time_of_loss else ""
    if len(candidate) == 5 and candidate[2] == ":":
        time_part = candidate
    try:
        dt = datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H:%M")
    except ValueError as exc:
        raise ValueError(
            f"date_of_loss={date_of_loss!r} / time_of_loss={time_of_loss!r} "
            f"not in the expected format: {exc}"
        )

    now_utc = datetime.utcnow()
    if dt >= now_utc:
        log.warning(
            "lossDate %s is not before the current UTC time %s — clamping so "
            "Guidewire's date constraint doesn't reject the claim",
            dt.isoformat(), now_utc.isoformat(),
        )
        dt = now_utc - timedelta(minutes=5)

    return dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def _build_guidewire_claim_payload(fnol: dict, policy_row: dict) -> dict:
    policy_row = policy_row or {}
    return {
        "data": {
            "attributes": {
                "policyNumber": fnol.get("policy_number"),
                "lossDate": _to_gw_loss_datetime(fnol.get("date_of_loss"), fnol.get("time_of_loss")),
                "description": fnol.get("cause_of_loss") or "Reported via FNOL intake",
                "jurisdiction": {"code": _GW_JURISDICTION_CODE},
                "lossCause": {"code": (fnol.get("loss_type") or "").strip().lower() or "other"},
                "lossLocation": {
                    "addressLine1": fnol.get("policyholder_address") or "",
                    "city": policy_row.get("city") or "",
                    "country": policy_row.get("country") or "US",
                    "postalCode": policy_row.get("postal_code") or "",
                    "state": {"code": _GW_JURISDICTION_CODE},
                },
                "reportedByType": {"code": "self"},
                "howReported": {"code": "phone"},
                "reporter": {"refid": "reporterId"},
                "mainContactType": {"code": "self"},
            }
        },
        "included": {
            "ClaimContact": [
                {
                    "attributes": {
                        "contactSubtype": "Person",
                        "firstName": _GW_REPORTER_FIRST_NAME,
                        "lastName": _GW_REPORTER_LAST_NAME,
                    },
                    "method": "post",
                    "refid": "reporterId",
                    "uri": "/claim/v1/claims/this/contacts",
                }
            ]
        },
    }


def _create_claim_in_guidewire(fnol: dict, policy_row: dict) -> str:
    """
    Drafts then submits a claim in Guidewire ClaimCenter for this FNOL.
    Returns the FINAL claim number from the /submit response — the draft
    response's claimNumber is a placeholder and is intentionally ignored.
    """
    payload = _build_guidewire_claim_payload(fnol, policy_row)
    draft = guidewire_client.create_claim(payload)
    draft_claim_id = (draft.get("data") or {}).get("attributes", {}).get("id")
    if not draft_claim_id:
        raise ValueError(f"Guidewire claim draft response missing id: {draft}")

    submitted = guidewire_client.submit_claim(draft_claim_id)
    claim_number = (submitted.get("data") or {}).get("attributes", {}).get("claimNumber")
    if not claim_number:
        raise ValueError(f"Guidewire claim submit response missing claimNumber: {submitted}")
    return claim_number


def submit_fnol(fnol_id: int) -> dict:
    """
    Marks an FNOL as submitted, sets submitted_at timestamp, and creates
    claims / claims_master / claim_journey_master records if none exist
    for the policy yet. The claim_number is issued by Guidewire ClaimCenter
    (draft + submit) rather than generated locally — if either ClaimCenter
    call fails, the FNOL is left unsubmitted so the user can retry.
    """
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        cur.execute("SELECT * FROM fnol_submissions WHERE id = %s", (fnol_id,))
        fnol = row_to_dict(cur.fetchone())   # use row_to_dict consistently (#3)
        if not fnol:
            raise ValueError(f"FNOL with id={fnol_id} not found")

        pd_row = {}
        claim_number = None
        if fnol.get("policy_number"):
            cur.execute(
                "SELECT coverage_limit, deductible, city, country, postal_code "
                "FROM policy_details WHERE policy_number = %s LIMIT 1",
                (fnol["policy_number"],),
            )
            pd_row = cur.fetchone() or {}

            policy_number_trimmed = (fnol["policy_number"] or "").strip()
            if policy_number_trimmed in LOCAL_ONLY_POLICY_NUMBERS:
                # Special-case policies: their GW policy id exists in ClaimCenter sandbox.
                # Talk to Guidewire BEFORE mutating any local state — if this
                # raises, the FNOL stays exactly as it was and submission can be
                # retried from the UI instead of getting stuck half-submitted.
                claim_number = _create_claim_in_guidewire(fnol, pd_row)
            else:
                # PolicyCenter-only policies: ClaimCenter sandbox doesn't know them,
                # so skip the CC call and generate a local claim number instead.
                cur.execute("SELECT COALESCE(MAX(id), 0) + 1 AS next_seq FROM claims")
                next_seq = cur.fetchone()["next_seq"]
                claim_number = f"CLM-{datetime.utcnow().year}-{next_seq:04d}"

        cur.execute(
            """
            UPDATE fnol_submissions
            SET status = 'submitted', submitted_at = NOW(), updated_at = NOW()
            WHERE id = %s
            RETURNING *
            """,
            (fnol_id,),
        )
        updated = row_to_dict(cur.fetchone())

        if claim_number:
            cur.execute(
                """
                INSERT INTO claims (
                    claim_number, policyholder_name, policy_number,
                    loss_type, short_description, severity, estimated_cost, status,
                    date_of_loss, location, ai_confidence, filed_at
                ) VALUES (%s,%s,%s,%s,%s,%s,%s, 'Open', %s,%s,%s, NOW())
                RETURNING id
                """,
                (
                    claim_number,
                    fnol.get("policyholder_name") or "Unknown",
                    fnol["policy_number"],
                    fnol.get("loss_type") or "Unknown",
                    fnol.get("cause_of_loss") or "Reported via FNOL intake",
                    fnol.get("severity") or "Medium",
                    fnol.get("estimated_cost"),
                    fnol.get("date_of_loss"),
                    fnol.get("policyholder_address"),
                    fnol.get("overall_confidence"),
                ),
            )
            claim_id = cur.fetchone()["id"]

            p_coverage_limit = pd_row["coverage_limit"] if pd_row.get("coverage_limit") else 0
            p_deductible = pd_row["deductible"] if pd_row.get("deductible") else 0

            cur.execute(
                """
                INSERT INTO claims_master (
                    claim_number, policyholder_name, policy_number, loss_type,
                    date_of_loss, coverage_limit, deductible, status
                ) VALUES (%s,%s,%s,%s,%s,%s,%s, 'Open')
                """,
                (
                    claim_number,
                    fnol.get("policyholder_name") or "Unknown",
                    fnol["policy_number"],
                    fnol.get("loss_type") or "Unknown",
                    fnol.get("date_of_loss"),
                    p_coverage_limit,
                    p_deductible,
                ),
            )

            cur.execute(
                """
                INSERT INTO claim_journey_master (
                    claim_id, claim_number, current_stage, current_stage_name,
                    sub_status, overall_sla_status
                ) VALUES (%s,%s,1,'Claim Initiated','Under Review','on_track')
                """,
                (claim_id, claim_number),
            )

        conn.commit()
        return {"fnol": updated, "claim_number": claim_number, "status": "submitted"}
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# Mandatory Fields Reference
# ──────────────────────────────────────────────────────────────────────────────

def get_mandatory_fields() -> list:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM fnol_mandatory_fields ORDER BY display_order")
        return row_to_dict(cur.fetchall())
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# Voice / Text Extractions
# ──────────────────────────────────────────────────────────────────────────────

def save_voice_text_extraction(req: SaveVoiceTextExtractionRequest) -> dict:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO fnol_voice_text_extraction (
                fnol_id, input_type, raw_input, transcribed_text,
                extracted_loss_type, extracted_cause, extracted_area,
                extracted_temporal, sudden_gradual_signal, emotional_context,
                extraction_confidence, created_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
            RETURNING *
            """,
            (
                req.fnol_id, req.input_type, req.raw_input, req.transcribed_text,
                req.extracted_loss_type, req.extracted_cause, req.extracted_area,
                req.extracted_temporal, req.sudden_gradual_signal, req.emotional_context,
                req.extraction_confidence,
            ),
        )
        result = cur.fetchone()
        conn.commit()
        return row_to_dict(result)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_voice_text_extractions(fnol_id: int) -> list:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM fnol_voice_text_extraction WHERE fnol_id = %s ORDER BY created_at",
            (fnol_id,),
        )
        return row_to_dict(cur.fetchall())
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# AI Inferences
# ──────────────────────────────────────────────────────────────────────────────

def save_ai_inferences(req: SaveAiInferencesRequest) -> list:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        created = []
        for item in req.inferences:
            cur.execute(
                """
                INSERT INTO fnol_ai_inferences (
                    fnol_id, field_name, inferred_value, confidence,
                    source, source_details, customer_confirmed, inferred_at
                ) VALUES (%s,%s,%s,%s,%s,%s,0,NOW())
                RETURNING *
                """,
                (
                    req.fnol_id, item.field_name, item.inferred_value,
                    item.confidence, item.source, item.source_details,
                ),
            )
            created.append(row_to_dict(cur.fetchone()))
        conn.commit()
        return created
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# Mandatory Question Log
# ──────────────────────────────────────────────────────────────────────────────

def log_question_answer(req: LogQuestionAnswerRequest) -> dict:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        answered_at = datetime.utcnow().isoformat() if req.answer_text else None
        cur.execute(
            """
            INSERT INTO fnol_mandatory_question_log (
                fnol_id, question_text, field_name, answer_text,
                answer_type, was_skipped, question_order,
                asked_at, answered_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,NOW(),%s)
            RETURNING *
            """,
            (
                req.fnol_id, req.question_text, req.field_name,
                req.answer_text, req.answer_type, int(req.was_skipped or False),
                req.question_order or 0, answered_at,
            ),
        )
        result = cur.fetchone()
        conn.commit()
        return row_to_dict(result)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_question_log(fnol_id: int) -> list:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM fnol_mandatory_question_log WHERE fnol_id = %s ORDER BY question_order",
            (fnol_id,),
        )
        return row_to_dict(cur.fetchall())
    finally:
        conn.close()


# ──────────────────────────────────────────────────────────────────────────────
# Field Attribution
# ──────────────────────────────────────────────────────────────────────────────

def save_field_attribution(req: SaveFieldAttributionRequest) -> list:
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        created = []
        for item in req.attributions:
            cur.execute(
                """
                INSERT INTO fnol_field_attribution (
                    fnol_id, field_name, field_label, field_value, source,
                    confidence, was_edited, was_confirmed, original_value,
                    edited_value, created_at
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,NOW())
                RETURNING *
                """,
                (
                    req.fnol_id, item.field_name, item.field_label,
                    item.field_value, item.source, item.confidence,
                    int(item.was_edited or False), int(item.was_confirmed or False),
                    item.original_value, item.edited_value,
                ),
            )
            created.append(row_to_dict(cur.fetchone()))
        conn.commit()
        return created
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

