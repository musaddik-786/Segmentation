"""
init_db.py
──────────
Creates all PostgreSQL tables for the Policyholder Agents platform and seeds
reference/sample data. Safe to re-run (idempotent).

Run:
    py -3 MCP/common/init_db.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_db_connection  # noqa: E402

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS claims (
    id SERIAL PRIMARY KEY,
    claim_number TEXT UNIQUE,
    policyholder_name TEXT,
    policy_number TEXT,
    loss_type TEXT,
    short_description TEXT,
    ai_generated_summary TEXT,
    detected_cause TEXT,
    severity TEXT,
    complexity TEXT,
    estimated_cost REAL,
    coverage INTEGER DEFAULT 1,
    ai_confidence INTEGER,
    status TEXT DEFAULT 'Open',
    location TEXT,
    assigned_adjuster TEXT,
    assigned_vendor TEXT,
    date_of_loss TEXT,
    filed_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS claims_master (
    id SERIAL PRIMARY KEY,
    claim_number TEXT UNIQUE,
    policyholder_name TEXT,
    policy_number TEXT,
    loss_type TEXT,
    date_of_loss TEXT,
    coverage_limit REAL,
    deductible REAL,
    status TEXT
);

CREATE TABLE IF NOT EXISTS claim_journey_master (
    id SERIAL PRIMARY KEY,
    claim_id INTEGER,
    claim_number TEXT,
    current_stage INTEGER DEFAULT 1,
    current_stage_name TEXT DEFAULT 'Claim Initiated',
    sub_status TEXT DEFAULT 'Under Review',
    journey_start_date TIMESTAMP DEFAULT NOW(),
    last_stage_change_date TIMESTAMP DEFAULT NOW(),
    expected_completion_date TEXT,
    overall_sla_status TEXT DEFAULT 'on_track',
    total_days_in_journey INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS stage_time_sla_tracking (
    id SERIAL PRIMARY KEY,
    claim_id INTEGER,
    claim_number TEXT,
    stage_number INTEGER,
    stage_name TEXT,
    entered_at TIMESTAMP DEFAULT NOW(),
    exited_at TIMESTAMP,
    sla_days INTEGER,
    sla_status TEXT
);

CREATE TABLE IF NOT EXISTS policy_details (
    id SERIAL PRIMARY KEY,
    policy_number TEXT UNIQUE,
    gw_policy_id TEXT,
    status TEXT DEFAULT 'Active',
    coverage_type TEXT,
    deductible REAL,
    coverage_limit REAL,
    remaining_coverage_limit REAL,
    exclusions TEXT,
    effective_date TEXT,
    expiration_date TEXT,
    policyholder_name TEXT,
    account_number TEXT,
    policy_address TEXT,
    state TEXT,
    term_type TEXT,
    premium_amount REAL,
    currency TEXT,
    city TEXT,
    country TEXT,
    postal_code TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS coverage_verification_results (
    id SERIAL PRIMARY KEY,
    claim_number TEXT UNIQUE,
    policy_number TEXT,
    coverage_verdict TEXT,
    exclusion_triggered INTEGER DEFAULT 0,
    exclusion_details TEXT,
    net_payable REAL,
    coverage_notes TEXT,
    verified_at TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS claim_payments (
    id SERIAL PRIMARY KEY,
    payment_id TEXT UNIQUE,
    claim_number TEXT,
    policy_number TEXT,
    amount_paid REAL,
    payment_date TEXT,
    approved_by TEXT,
    payment_status TEXT DEFAULT 'Released',
    coverage_before REAL,
    coverage_after REAL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fnol_submissions (
    id SERIAL PRIMARY KEY,
    fnol_number TEXT UNIQUE,
    policy_number TEXT,
    policyholder_name TEXT,
    policyholder_address TEXT,
    policy_effective_date TEXT,
    policy_expiration_date TEXT,
    loss_type TEXT,
    loss_type_source TEXT,
    cause_of_loss TEXT,
    cause_of_loss_source TEXT,
    date_of_loss TEXT,
    date_of_loss_source TEXT,
    time_of_loss TEXT,
    time_of_loss_source TEXT,
    area_affected TEXT,
    area_affected_source TEXT,
    occupancy_at_loss TEXT,
    occupancy_at_loss_source TEXT,
    sudden_vs_gradual TEXT,
    sudden_vs_gradual_source TEXT,
    emotional_context TEXT,
    emotional_context_source TEXT,
    severity TEXT,
    severity_source TEXT,
    urgency_indicator TEXT,
    urgency_indicator_source TEXT,
    voice_transcript TEXT,
    text_input TEXT,
    overall_confidence INTEGER,
    confidence_notes TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    submitted_at TIMESTAMP
);
ALTER TABLE fnol_submissions ADD COLUMN IF NOT EXISTS estimated_cost REAL;

CREATE TABLE IF NOT EXISTS fnol_mandatory_fields (
    id SERIAL PRIMARY KEY,
    field_name TEXT UNIQUE,
    field_label TEXT,
    field_category TEXT,
    is_required INTEGER DEFAULT 1,
    can_be_inferred INTEGER DEFAULT 1,
    inference_question TEXT,
    input_type TEXT DEFAULT 'text',
    input_options TEXT,
    display_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS fnol_ai_inferences (
    id SERIAL PRIMARY KEY,
    fnol_id INTEGER,
    field_name TEXT,
    inferred_value TEXT,
    confidence INTEGER,
    source TEXT,
    source_details TEXT,
    customer_confirmed INTEGER DEFAULT 0,
    customer_edited_value TEXT,
    inferred_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fnol_voice_text_extraction (
    id SERIAL PRIMARY KEY,
    fnol_id INTEGER,
    input_type TEXT,
    raw_input TEXT,
    transcribed_text TEXT,
    extracted_loss_type TEXT,
    extracted_cause TEXT,
    extracted_area TEXT,
    extracted_temporal TEXT,
    sudden_gradual_signal TEXT,
    emotional_context TEXT,
    extraction_confidence INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS fnol_mandatory_question_log (
    id SERIAL PRIMARY KEY,
    fnol_id INTEGER,
    question_text TEXT,
    field_name TEXT,
    answer_text TEXT,
    answer_type TEXT,
    was_skipped INTEGER DEFAULT 0,
    question_order INTEGER DEFAULT 0,
    asked_at TIMESTAMP DEFAULT NOW(),
    answered_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS fnol_field_attribution (
    id SERIAL PRIMARY KEY,
    fnol_id INTEGER,
    field_name TEXT,
    field_label TEXT,
    field_value TEXT,
    source TEXT,
    confidence INTEGER,
    was_edited INTEGER DEFAULT 0,
    was_confirmed INTEGER DEFAULT 0,
    original_value TEXT,
    edited_value TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    document_id TEXT UNIQUE,
    claim_number TEXT,
    file_name TEXT,
    file_url TEXT,
    file_size INTEGER,
    content_type TEXT,
    document_type TEXT,
    classification_confidence INTEGER DEFAULT 0,
    uploaded_by TEXT,
    uploaded_by_role TEXT,
    status TEXT DEFAULT 'Classified',
    visibility TEXT DEFAULT 'public',
    extracted_data TEXT,
    insights TEXT,
    investigation_notes TEXT,
    flagged INTEGER DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS customer_feedback_per_stage (
    id SERIAL PRIMARY KEY,
    claim_id TEXT,
    claim_number TEXT,
    stage_number INTEGER,
    stage_name TEXT,
    sentiment TEXT,
    sentiment_score REAL,
    comment TEXT,
    submitted_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS claim_sentiment_tracker (
    id SERIAL PRIMARY KEY,
    tracker_id TEXT UNIQUE,
    claim_row_id TEXT,
    claim_number TEXT,
    policyholder_name TEXT,
    current_sentiment TEXT,
    sentiment_score REAL,
    sentiment_trend TEXT,
    last_interaction_date TEXT,
    escalation_risk TEXT,
    satisfaction_rating REAL,
    nps_score INTEGER,
    notes TEXT,
    assigned_adjuster TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS communication_history (
    id SERIAL PRIMARY KEY,
    communication_id TEXT UNIQUE,
    claim_row_id TEXT,
    claim_number TEXT,
    policyholder_name TEXT,
    communication_type TEXT,
    direction TEXT,
    subject TEXT,
    summary TEXT,
    sentiment_detected TEXT,
    handled_by TEXT,
    response_time_minutes INTEGER,
    resolution_status TEXT,
    follow_up_required INTEGER DEFAULT 0,
    follow_up_date TEXT,
    attachments TEXT,
    communication_date TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS segmentation_result_output (
    id SERIAL PRIMARY KEY,
    claim_number TEXT UNIQUE,
    severity TEXT,
    complexity TEXT,
    stp_score INTEGER,
    recommended_path TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS stp_classification (
    id SERIAL PRIMARY KEY,
    stp_id TEXT,
    claim_number TEXT UNIQUE,
    readiness INTEGER DEFAULT 0,
    fraud_ambiguity TEXT DEFAULT 'Low',
    subrogation TEXT DEFAULT 'Low',
    vis INTEGER DEFAULT 0,
    stp_score INTEGER DEFAULT 0,
    stp_category TEXT DEFAULT 'Manual Review',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS intake_validation_result_output (
    id SERIAL PRIMARY KEY,
    claim_number TEXT UNIQUE,
    completeness_score INTEGER,
    missing_fields TEXT,
    coverage_status TEXT,
    docs_status TEXT DEFAULT 'Not Checked',
    missing_docs TEXT,
    fraud_risk TEXT,
    fraud_risk_score INTEGER,
    fraud_flags TEXT,
    recommendation TEXT,
    overall_result TEXT,
    validated_at TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS policyholder_actions (
    id SERIAL PRIMARY KEY,
    claim_row_id TEXT,
    claim_number TEXT,
    action_type TEXT,
    action_label TEXT,
    details TEXT,
    stage_at_action INTEGER,
    performed_by TEXT DEFAULT 'Policyholder',
    timestamp TIMESTAMP DEFAULT NOW()
);

-- ── Motor LOB: policy details (local mock — no Guidewire for Motor) ───────────
CREATE TABLE IF NOT EXISTS motor_policy_details (
    id SERIAL PRIMARY KEY,
    policy_number TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'Active',
    coverage_type TEXT,
    deductible REAL,
    coverage_limit REAL,
    remaining_coverage_limit REAL,
    exclusions TEXT,
    effective_date TEXT,
    expiration_date TEXT,
    policyholder_name TEXT,
    vehicle_make TEXT,
    vehicle_model TEXT,
    vehicle_year TEXT,
    -- Motor-specific coverage limits (OD = Own Damage, TP = Third Party)
    od_coverage_limit NUMERIC(12,2),
    tp_coverage_limit NUMERIC(12,2),
    -- Add-on flags (1 = active, 0 = not active)
    zero_dep_enabled         INTEGER DEFAULT 0,
    engine_protection_enabled INTEGER DEFAULT 0,
    addons TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ── Motor LOB: coverage verification results ──────────────────────────────────
CREATE TABLE IF NOT EXISTS motor_coverage_verification_results (
    id SERIAL PRIMARY KEY,
    claim_number TEXT UNIQUE,
    policy_number TEXT,
    coverage_verdict TEXT,
    exclusion_triggered INTEGER DEFAULT 0,
    exclusion_details TEXT,
    net_payable REAL,
    coverage_notes TEXT,
    verified_at TEXT,
    -- Motor-specific result columns
    claim_type TEXT,                   -- 'OD' or 'TP'
    license_valid INTEGER DEFAULT 1,   -- 0 = expired at time of loss
    license_expiry_note TEXT,
    zero_dep_applied INTEGER DEFAULT 0,
    engine_protection_note TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ── Motor LOB: vehicle details pre-populated per policy ──────────────────────
CREATE TABLE IF NOT EXISTS motor_vehicle_details (
    id SERIAL PRIMARY KEY,
    policy_number TEXT UNIQUE NOT NULL,
    driver_license TEXT,
    vin TEXT,
    registration_number TEXT,
    vehicle_make TEXT,
    vehicle_model TEXT,
    vehicle_year TEXT,
    driver_license_expiry DATE,        -- for license expiry check at time of loss
    created_at TIMESTAMP DEFAULT NOW()
);

-- ── Motor LOB: separate FNOL submission table (does NOT touch fnol_submissions) ─
CREATE TABLE IF NOT EXISTS motor_fnol_submissions (
    id SERIAL PRIMARY KEY,
    fnol_number TEXT UNIQUE,
    policy_number TEXT,
    policyholder_name TEXT,
    policyholder_address TEXT,
    policy_effective_date TEXT,
    policy_expiration_date TEXT,
    -- Motor LOB loss fields
    loss_type TEXT,
    loss_type_source TEXT,
    cause_of_loss TEXT,
    cause_of_loss_source TEXT,
    date_of_loss TEXT,
    date_of_loss_source TEXT,
    time_of_loss TEXT,
    time_of_loss_source TEXT,
    accident_location TEXT,
    accident_location_source TEXT,
    emotional_context TEXT,
    emotional_context_source TEXT,
    severity TEXT,
    severity_source TEXT,
    urgency_indicator TEXT,
    urgency_indicator_source TEXT,
    -- Motor LOB vehicle fields (auto-populated from motor_vehicle_details)
    driver_license TEXT,
    vin TEXT,
    registration_number TEXT,
    vehicle_make TEXT,
    vehicle_model TEXT,
    vehicle_year TEXT,
    -- Optional user-supplied motor fields
    passenger_count TEXT,
    tow_required TEXT,
    police_fir_number TEXT,
    telematics_consent TEXT,
    -- Audit / metadata
    voice_transcript TEXT,
    text_input TEXT,
    overall_confidence INTEGER,
    confidence_notes TEXT,
    estimated_cost REAL,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    submitted_at TIMESTAMP
);

-- ── Motor LOB: segmentation / STP output tables ─────────────────────────────
CREATE TABLE IF NOT EXISTS motor_stp_classification (
    id SERIAL PRIMARY KEY,
    stp_id TEXT,
    claim_number TEXT UNIQUE,
    readiness INTEGER DEFAULT 0,
    fraud_ambiguity TEXT DEFAULT 'Low',
    subrogation TEXT DEFAULT 'Low',
    vis INTEGER DEFAULT 0,
    stp_score INTEGER DEFAULT 0,
    stp_category TEXT DEFAULT 'Manual Review',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS motor_segmentation_result_output (
    id SERIAL PRIMARY KEY,
    claim_number TEXT UNIQUE,
    severity TEXT,
    complexity TEXT,
    stp_score INTEGER,
    recommended_path TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ── Motor LOB: claim readiness results ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS motor_intake_validation_result_output (
    id SERIAL PRIMARY KEY,
    claim_number TEXT UNIQUE,
    completeness_score INTEGER,
    missing_fields TEXT,
    coverage_status TEXT,
    docs_status TEXT DEFAULT 'Not Checked',
    missing_docs TEXT,
    fraud_risk TEXT,
    fraud_risk_score INTEGER,
    fraud_flags TEXT,
    recommendation TEXT,
    overall_result TEXT,
    validated_at TEXT,
    -- Motor-specific readiness checklist
    vehicle_details_present INTEGER DEFAULT 0,
    driver_details_present  INTEGER DEFAULT 0,
    damage_photos_present   INTEGER DEFAULT 0,
    dl_doc_present          INTEGER DEFAULT 0,
    rc_book_present         INTEGER DEFAULT 0,
    police_fir_present      INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ── Motor LOB: child tables (mirror of personal-lines tables, motor-prefixed) ──
CREATE TABLE IF NOT EXISTS motor_fnol_mandatory_fields (
    id SERIAL PRIMARY KEY,
    field_name TEXT UNIQUE,
    field_label TEXT,
    field_category TEXT,
    is_required INTEGER DEFAULT 1,
    can_be_inferred INTEGER DEFAULT 1,
    inference_question TEXT,
    input_type TEXT DEFAULT 'text',
    input_options TEXT,
    display_order INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS motor_fnol_ai_inferences (
    id SERIAL PRIMARY KEY,
    fnol_id INTEGER,
    field_name TEXT,
    inferred_value TEXT,
    confidence INTEGER,
    source TEXT,
    source_details TEXT,
    customer_confirmed INTEGER DEFAULT 0,
    customer_edited_value TEXT,
    inferred_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS motor_fnol_voice_text_extraction (
    id SERIAL PRIMARY KEY,
    fnol_id INTEGER,
    input_type TEXT,
    raw_input TEXT,
    transcribed_text TEXT,
    extracted_loss_type TEXT,
    extracted_cause TEXT,
    extracted_area TEXT,
    extracted_temporal TEXT,
    sudden_gradual_signal TEXT,
    emotional_context TEXT,
    extraction_confidence INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS motor_fnol_mandatory_question_log (
    id SERIAL PRIMARY KEY,
    fnol_id INTEGER,
    question_text TEXT,
    field_name TEXT,
    answer_text TEXT,
    answer_type TEXT,
    was_skipped INTEGER DEFAULT 0,
    question_order INTEGER DEFAULT 0,
    asked_at TIMESTAMP DEFAULT NOW(),
    answered_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS motor_fnol_field_attribution (
    id SERIAL PRIMARY KEY,
    fnol_id INTEGER,
    field_name TEXT,
    field_label TEXT,
    field_value TEXT,
    source TEXT,
    confidence INTEGER,
    was_edited INTEGER DEFAULT 0,
    was_confirmed INTEGER DEFAULT 0,
    original_value TEXT,
    edited_value TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    confirmed_at TIMESTAMP
);
"""


# ── Motor LOB mandatory fields ────────────────────────────────────────────────
# driver_license / vin / registration_number / make+model+year are intentionally
# NOT in this list — they come from motor_vehicle_details (pre-populated per
# policy) and are never asked from the user.
MANDATORY_FIELDS = [
    ("loss_type", "Type of Loss", "loss_details", 1, 1,
     "What type of motor loss occurred? (e.g. Collision, Theft, Vandalism, Fire, Natural Disaster)",
     "select", '["Collision", "Theft", "Vandalism", "Fire", "Natural Disaster", "Third-Party Liability", "Windshield Damage"]', 1),
    ("cause_of_loss", "Cause of Loss", "loss_details", 1, 1,
     "What caused the accident or loss? Briefly describe what happened.", "text", None, 2),
    ("date_of_loss", "Date of Loss", "loss_details", 1, 1,
     "On what date did the loss occur?", "date", None, 3),
    ("time_of_loss", "Time of Loss", "loss_details", 1, 1,
     "Approximately what time did the loss occur?", "time", None, 4),
    ("accident_location", "Accident Location", "loss_details", 1, 1,
     "Where did the accident or loss occur? (address, city, or landmark)", "text", None, 5),
    ("severity", "Severity", "loss_details", 1, 1,
     "How severe would you say the damage is — minor, moderate, or severe?", "select",
     '["Low", "Medium", "High", "Critical"]', 6),
    ("policy_number", "Policy Number", "policy_details", 1, 1,
     "What is your motor policy number?", "text", None, 7),
]

# Fields that are pre-populated from motor_vehicle_details (NOT asked from user)
MOTOR_VEHICLE_AUTO_FIELDS = ["driver_license", "vin", "registration_number",
                              "vehicle_make", "vehicle_model", "vehicle_year"]


def init_db():
    conn = get_db_connection()
    try:
        cur = conn.cursor()

        # Execute schema (CREATE TABLE IF NOT EXISTS is idempotent)
        cur.execute(SCHEMA_SQL)

        # Column migrations — safely add columns that may be missing from
        # tables created by an earlier schema version.
        migrations = [
            "ALTER TABLE claims ADD COLUMN IF NOT EXISTS complexity TEXT",
            "ALTER TABLE claims ADD COLUMN IF NOT EXISTS ai_generated_summary TEXT",
            "ALTER TABLE claims ADD COLUMN IF NOT EXISTS detected_cause TEXT",
            "ALTER TABLE claims ADD COLUMN IF NOT EXISTS assigned_adjuster TEXT",
            "ALTER TABLE claims ADD COLUMN IF NOT EXISTS assigned_vendor TEXT",
            "ALTER TABLE claims ADD COLUMN IF NOT EXISTS police_report_number TEXT",
            "ALTER TABLE claim_journey_master ADD COLUMN IF NOT EXISTS sub_status TEXT DEFAULT 'Under Review'",
            "ALTER TABLE claim_journey_master ADD COLUMN IF NOT EXISTS overall_sla_status TEXT DEFAULT 'on_track'",
            # policy_details extended columns
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS gw_policy_id TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS remaining_coverage_limit REAL",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS exclusions TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS effective_date TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS expiration_date TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS policyholder_name TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS account_number TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS policy_address TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS state TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS term_type TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS premium_amount REAL",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS currency TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS city TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS country TEXT",
            "ALTER TABLE policy_details ADD COLUMN IF NOT EXISTS postal_code TEXT",
            # customer_feedback_per_stage — add sentiment_score column
            "ALTER TABLE customer_feedback_per_stage ADD COLUMN IF NOT EXISTS sentiment_score REAL",
            # stp_classification — add missing stp_score column and unique constraint
            "ALTER TABLE stp_classification ADD COLUMN IF NOT EXISTS stp_score INTEGER DEFAULT 0",
            # intake_validation_result_output — add missing columns for existing DBs
            "ALTER TABLE intake_validation_result_output ADD COLUMN IF NOT EXISTS missing_fields TEXT",
            "ALTER TABLE intake_validation_result_output ADD COLUMN IF NOT EXISTS docs_status TEXT DEFAULT 'Not Checked'",
            "ALTER TABLE intake_validation_result_output ADD COLUMN IF NOT EXISTS missing_docs TEXT",
            "ALTER TABLE intake_validation_result_output ADD COLUMN IF NOT EXISTS fraud_risk_score INTEGER",
            "ALTER TABLE intake_validation_result_output ADD COLUMN IF NOT EXISTS fraud_flags TEXT",
            "ALTER TABLE intake_validation_result_output ADD COLUMN IF NOT EXISTS recommendation TEXT",
            "ALTER TABLE intake_validation_result_output ADD COLUMN IF NOT EXISTS overall_result TEXT",
            "ALTER TABLE intake_validation_result_output ADD COLUMN IF NOT EXISTS validated_at TEXT",
            # Deduplicate before adding unique indexes (keep latest row per claim_number)
            "DELETE FROM intake_validation_result_output WHERE id NOT IN (SELECT MAX(id) FROM intake_validation_result_output GROUP BY claim_number)",
            "DELETE FROM stp_classification WHERE id NOT IN (SELECT MAX(id) FROM stp_classification GROUP BY claim_number)",
            "DELETE FROM segmentation_result_output WHERE id NOT IN (SELECT MAX(id) FROM segmentation_result_output GROUP BY claim_number)",
            # Unique indexes — required for ON CONFLICT (claim_number) DO UPDATE in handlers
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_intake_validation_claim_number ON intake_validation_result_output(claim_number)",
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_stp_classification_claim_number ON stp_classification(claim_number)",
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_segmentation_result_claim_number ON segmentation_result_output(claim_number)",
            # occupancy_at_loss used to be stored as INTEGER (1/0), which showed
            # inconsistently against the chat's "Yes"/"No" summary and was
            # mistaken for "missing" by falsy-value checks when 0 (No) was a
            # legitimate answer. Convert existing data in place; guarded so this
            # is a no-op once the column is already TEXT.
            """
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'fnol_submissions'
                      AND column_name = 'occupancy_at_loss'
                      AND data_type = 'integer'
                ) THEN
                    ALTER TABLE fnol_submissions
                    ALTER COLUMN occupancy_at_loss TYPE TEXT
                    USING (CASE occupancy_at_loss WHEN 1 THEN 'Yes' WHEN 0 THEN 'No' ELSE NULL END);
                END IF;
            END $$;
            """,
            # ── Motor LOB column migrations (safe to re-run on existing DBs) ────
            # motor_policy_details — OD/TP limits and add-on flags
            "ALTER TABLE motor_policy_details ADD COLUMN IF NOT EXISTS od_coverage_limit NUMERIC(12,2)",
            "ALTER TABLE motor_policy_details ADD COLUMN IF NOT EXISTS tp_coverage_limit NUMERIC(12,2)",
            "ALTER TABLE motor_policy_details ADD COLUMN IF NOT EXISTS zero_dep_enabled INTEGER DEFAULT 0",
            "ALTER TABLE motor_policy_details ADD COLUMN IF NOT EXISTS engine_protection_enabled INTEGER DEFAULT 0",
            "ALTER TABLE motor_policy_details ADD COLUMN IF NOT EXISTS addons TEXT",
            # motor_vehicle_details — license expiry for Check 2
            "ALTER TABLE motor_vehicle_details ADD COLUMN IF NOT EXISTS driver_license_expiry DATE",
            # motor_coverage_verification_results — Motor-specific check result columns
            "ALTER TABLE motor_coverage_verification_results ADD COLUMN IF NOT EXISTS claim_type TEXT",
            "ALTER TABLE motor_coverage_verification_results ADD COLUMN IF NOT EXISTS license_valid INTEGER DEFAULT 1",
            "ALTER TABLE motor_coverage_verification_results ADD COLUMN IF NOT EXISTS license_expiry_note TEXT",
            "ALTER TABLE motor_coverage_verification_results ADD COLUMN IF NOT EXISTS zero_dep_applied INTEGER DEFAULT 0",
            "ALTER TABLE motor_coverage_verification_results ADD COLUMN IF NOT EXISTS engine_protection_note TEXT",
            # motor_intake_validation_result_output — unique index for ON CONFLICT
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_motor_intake_validation_claim ON motor_intake_validation_result_output(claim_number)",
            # motor segmentation tables — unique indexes for ON CONFLICT upserts
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_motor_stp_classification_claim ON motor_stp_classification(claim_number)",
            "CREATE UNIQUE INDEX IF NOT EXISTS uq_motor_segmentation_result_claim ON motor_segmentation_result_output(claim_number)",
            # Rename the pre-rename "insured_address" mandatory field row left over
            # from an earlier schema version — ON CONFLICT DO NOTHING in the seed
            # loop below can't fix this since policyholder_address is a different
            # field_name, so the stale row would otherwise never update.
            """
            UPDATE fnol_mandatory_fields
               SET field_name = 'policyholder_address',
                   field_label = 'Policyholder Property Address'
             WHERE field_name = 'insured_address'
               AND NOT EXISTS (
                   SELECT 1 FROM fnol_mandatory_fields WHERE field_name = 'policyholder_address'
               )
            """,
            # Some DBs already had both rows (a newer init_db seeded
            # policyholder_address before this instance's insured_address row was
            # ever renamed) — the UPDATE above is then a no-op, so drop the
            # redundant leftover directly. fnol_ai_inferences /
            # fnol_mandatory_question_log store field_name as plain text with no
            # FK, so this is safe and doesn't touch audit history.
            """
            DELETE FROM fnol_mandatory_fields
             WHERE field_name = 'insured_address'
               AND EXISTS (
                   SELECT 1 FROM fnol_mandatory_fields WHERE field_name = 'policyholder_address'
               )
            """,
        ]
        for m in migrations:
            cur.execute(m)

        # Seed Motor LOB mandatory fields into motor_fnol_mandatory_fields
        # (personal-lines fnol_mandatory_fields is left completely untouched)
        for row in MANDATORY_FIELDS:
            cur.execute(
                """
                INSERT INTO motor_fnol_mandatory_fields (
                    field_name, field_label, field_category, is_required,
                    can_be_inferred, inference_question, input_type,
                    input_options, display_order
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (field_name) DO NOTHING
                """,
                row,
            )

        # Seed sample policy
        cur.execute(
            """
            INSERT INTO policy_details (policy_number, status, coverage_type, deductible, coverage_limit)
            VALUES ('POL-1001', 'Active', 'Homeowners', 1000, 250000)
            ON CONFLICT DO NOTHING
            """
        )
        cur.execute(
            """
            INSERT INTO policy_details (policy_number, status, coverage_type, deductible, coverage_limit)
            VALUES ('POL-1002', 'Active', 'Auto', 500, 50000)
            ON CONFLICT DO NOTHING
            """
        )

        # Seed Motor LOB policy details (mock — no Guidewire for Motor)
        # POL-1001: full add-ons (Zero Dep + Engine Protection), valid license
        # POL-1002: no add-ons, EXPIRED license (test rejection)
        # POL-1003: Zero Dep only, valid license
        motor_policies = [
            ("POL-1001", "Active", "Comprehensive", 5000, 150000, 135000,
             "Racing, DUI, Commercial Use", "2025-01-01", "2026-12-31", "Rajesh Kumar",
             135000, 100000, 1, 1, "Zero Depreciation, Engine Protection"),
            ("POL-1002", "Active", "Third Party", 2000, 100000, 100000,
             "Racing, DUI", "2025-06-01", "2026-12-31", "Priya Sharma",
             100000, 100000, 0, 0, "None"),
            ("POL-1003", "Active", "Comprehensive", 3000, 200000, 180000,
             "Commercial Use, DUI", "2024-09-01", "2026-12-31", "Anil Mehta",
             180000, 100000, 1, 0, "Zero Depreciation"),
        ]
        for mp in motor_policies:
            cur.execute(
                """
                INSERT INTO motor_policy_details (
                    policy_number, status, coverage_type, deductible, coverage_limit,
                    remaining_coverage_limit, exclusions, effective_date, expiration_date,
                    policyholder_name, od_coverage_limit, tp_coverage_limit,
                    zero_dep_enabled, engine_protection_enabled, addons
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (policy_number) DO NOTHING
                """,
                mp,
            )

        # Seed mock motor vehicle details (pre-populated, never asked from user)
        # driver_license_expiry: POL-1001 valid, POL-1002 EXPIRED (2025-12-31), POL-1003 valid
        mock_vehicles = [
            ("POL-1001", "DL-MH-112233", "1HGCM82633A112233", "MH-01-AB-1234",
             "Honda", "Accord", "2022", "2028-06-30"),
            ("POL-1002", "DL-MH-445566", "3VWFE21C04M445566", "MH-02-CD-5678",
             "Volkswagen", "Jetta", "2020", "2025-12-31"),
            ("POL-1003", "DL-MH-778899", "5YJSA1DN5CFP01234", "MH-03-EF-9012",
             "Toyota", "Camry", "2021", "2027-09-15"),
        ]
        for mv in mock_vehicles:
            cur.execute(
                """
                INSERT INTO motor_vehicle_details (
                    policy_number, driver_license, vin, registration_number,
                    vehicle_make, vehicle_model, vehicle_year, driver_license_expiry
                ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT (policy_number) DO NOTHING
                """,
                mv,
            )

        # Seed sample claim
        cur.execute("SELECT COUNT(*) FROM claims WHERE claim_number = 'CLM-2026-1001'")
        count = cur.fetchone()["count"]
        if count == 0:
            cur.execute(
                """
                INSERT INTO claims (
                    claim_number, policyholder_name, policy_number, loss_type,
                    short_description, severity, complexity, estimated_cost,
                    coverage, ai_confidence, status, location, date_of_loss
                ) VALUES (
                    'CLM-2026-1001', 'John Doe', 'POL-1001', 'Water Damage',
                    'Burst pipe in kitchen caused flooding', 'Medium', 'Low', 8500,
                    TRUE, 85, 'Open', '123 Main St, Springfield', '2026-05-20'
                ) RETURNING id
                """
            )
            claim_id = cur.fetchone()["id"]

            cur.execute(
                """
                INSERT INTO claims_master (
                    claim_number, policyholder_name, policy_number, loss_type,
                    date_of_loss, coverage_limit, deductible, status
                ) VALUES (
                    'CLM-2026-1001', 'John Doe', 'POL-1001', 'Homeowners',
                    '2026-05-20', 250000, 1000, 'Open'
                ) ON CONFLICT (claim_number) DO NOTHING
                """
            )

            cur.execute("SELECT COUNT(*) FROM claim_journey_master WHERE claim_number = 'CLM-2026-1001'")
            if cur.fetchone()["count"] == 0:
                cur.execute(
                    """
                    INSERT INTO claim_journey_master (
                        claim_id, claim_number, current_stage, current_stage_name,
                        sub_status, overall_sla_status
                    ) VALUES (%s, 'CLM-2026-1001', 1, 'Claim Initiated', 'Under Review', 'on_track')
                    """,
                    (claim_id,),
                )

        # ── Motor LOB: seed claims in the shared claims table ─────────────────
        # CLM-MOTOR-001: complete Collision claim (POL-1001, all fields present)
        # CLM-MOTOR-002: Theft claim (POL-1002, missing accident_location)
        # CLM-MOTOR-003: Third-Party Liability (POL-1003, late-reported — fraud risk)
        motor_claims = [
            ("CLM-MOTOR-001", "Rajesh Kumar", "POL-1001", "Collision",
             "Vehicle rear-ended at traffic signal, front bumper and hood damage",
             "Medium", "Low", 45000, True, 82, "Open",
             "MG Road, Bangalore", "2026-09-10"),
            ("CLM-MOTOR-002", "Priya Sharma",  "POL-1002", "Theft",
             "Vehicle stolen from parking lot overnight",
             "High", "High", 100000, True, 75, "Open",
             None, "2026-08-20"),
            ("CLM-MOTOR-003", "Anil Mehta",    "POL-1003", "Third Party Liability",
             "Vehicle collided with another car; third-party injury reported",
             "High", "Complex", 80000, True, 60, "Open",
             "NH48 Pune Highway", "2026-07-15"),
        ]
        for mc in motor_claims:
            cur.execute("SELECT COUNT(*) FROM claims WHERE claim_number = %s", (mc[0],))
            if cur.fetchone()["count"] == 0:
                cur.execute(
                    """
                    INSERT INTO claims (
                        claim_number, policyholder_name, policy_number, loss_type,
                        short_description, severity, complexity, estimated_cost,
                        coverage, ai_confidence, status, location, date_of_loss
                    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """,
                    mc,
                )

        # ── Motor LOB: seed motor_fnol_submissions ────────────────────────────
        motor_fnols = [
            # CLM-MOTOR-001: complete FNOL (all fields present)
            {
                "fnol_number": "MFNOL-2026-001",
                "policy_number": "POL-1001",
                "policyholder_name": "Rajesh Kumar",
                "policyholder_address": "42 Koramangala, Bangalore 560034",
                "loss_type": "Collision",
                "cause_of_loss": "Rear-end collision at traffic signal",
                "date_of_loss": "2026-09-10",
                "time_of_loss": "08:30",
                "accident_location": "MG Road & Brigade Road junction, Bangalore",
                "severity": "Medium",
                "driver_license": "DL-MH-112233",
                "vin": "1HGCM82633A112233",
                "registration_number": "MH-01-AB-1234",
                "vehicle_make": "Honda",
                "vehicle_model": "Accord",
                "vehicle_year": "2022",
                "passenger_count": "2",
                "tow_required": "Yes",
                "police_fir_number": None,
                "telematics_consent": "Yes",
                "overall_confidence": 88,
                "status": "submitted",
            },
            # CLM-MOTOR-002: incomplete FNOL (no accident_location)
            {
                "fnol_number": "MFNOL-2026-002",
                "policy_number": "POL-1002",
                "policyholder_name": "Priya Sharma",
                "policyholder_address": "15 Andheri West, Mumbai 400053",
                "loss_type": "Theft",
                "cause_of_loss": "Vehicle stolen from parking lot",
                "date_of_loss": "2026-08-20",
                "time_of_loss": "02:00",
                "accident_location": None,  # MISSING — triggers incompleteness
                "severity": "High",
                "driver_license": "DL-MH-445566",
                "vin": "3VWFE21C04M445566",
                "registration_number": "MH-02-CD-5678",
                "vehicle_make": "Volkswagen",
                "vehicle_model": "Jetta",
                "vehicle_year": "2020",
                "passenger_count": None,
                "tow_required": "No",
                "police_fir_number": "FIR/2026/0892",
                "telematics_consent": "No",
                "overall_confidence": 70,
                "status": "submitted",
            },
            # CLM-MOTOR-003: third-party claim, delayed 64 days — fraud signal
            {
                "fnol_number": "MFNOL-2026-003",
                "policy_number": "POL-1003",
                "policyholder_name": "Anil Mehta",
                "policyholder_address": "88 Baner Road, Pune 411045",
                "loss_type": "Third Party Liability",
                "cause_of_loss": "Collision with third-party vehicle on highway; injury reported",
                "date_of_loss": "2026-07-15",
                "time_of_loss": "14:15",
                "accident_location": "NH48 Pune-Mumbai Highway, Km 72",
                "severity": "High",
                "driver_license": "DL-MH-778899",
                "vin": "5YJSA1DN5CFP01234",
                "registration_number": "MH-03-EF-9012",
                "vehicle_make": "Toyota",
                "vehicle_model": "Camry",
                "vehicle_year": "2021",
                "passenger_count": "3",
                "tow_required": "Yes",
                "police_fir_number": "FIR/2026/1456",
                "telematics_consent": "No",
                "overall_confidence": 55,
                "status": "submitted",
            },
        ]
        for mf in motor_fnols:
            cur.execute(
                "SELECT COUNT(*) FROM motor_fnol_submissions WHERE fnol_number = %s",
                (mf["fnol_number"],),
            )
            if cur.fetchone()["count"] == 0:
                cur.execute(
                    """
                    INSERT INTO motor_fnol_submissions (
                        fnol_number, policy_number, policyholder_name, policyholder_address,
                        loss_type, cause_of_loss, date_of_loss, time_of_loss,
                        accident_location, severity,
                        driver_license, vin, registration_number,
                        vehicle_make, vehicle_model, vehicle_year,
                        passenger_count, tow_required, police_fir_number, telematics_consent,
                        overall_confidence, status, submitted_at
                    ) VALUES (
                        %(fnol_number)s, %(policy_number)s, %(policyholder_name)s, %(policyholder_address)s,
                        %(loss_type)s, %(cause_of_loss)s, %(date_of_loss)s, %(time_of_loss)s,
                        %(accident_location)s, %(severity)s,
                        %(driver_license)s, %(vin)s, %(registration_number)s,
                        %(vehicle_make)s, %(vehicle_model)s, %(vehicle_year)s,
                        %(passenger_count)s, %(tow_required)s, %(police_fir_number)s,
                        %(telematics_consent)s, %(overall_confidence)s, %(status)s, NOW()
                    )
                    """,
                    mf,
                )

        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    init_db()
    print("Database initialized on Azure PostgreSQL.")
