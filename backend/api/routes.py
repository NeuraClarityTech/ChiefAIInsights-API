import os
from fastapi import APIRouter, Form, HTTPException
from datetime import datetime
from utils.google_sheet import get_worksheet
from utils.mailer import send_thank_you, notify_admin

router = APIRouter()

# Persona classifier (fallback if role_level is empty)
TIER_BUCKETS = [
    ("Tier 1 (CXO)", ["chief", "cxo", "officer", "ceo", "cmo", "cfo", "cio"]),
    ("Tier 2 (EVP/SVP/VP)", ["evp", "svp", "vp", "vice"]),
    ("Tier 3 (Director/Head)", ["director", "head"]),
    ("Tier 4 (Manager/Sr Manager)", ["manager"]),
    ("Tier 5 (Specialist/Practitioner)", ["specialist", "analyst", "consultant", "lead"]),
]
def classify_persona_level(title: str, fallback: str | None) -> str:
    if fallback: return fallback
    t = (title or "").lower()
    for label, keys in TIER_BUCKETS:
        if any(k in t for k in keys): return label
    return "Unclassified"

@router.get("/health")
def health():
    return {"status":"healthy"}

@router.post("/contact")
def contact_form(name: str = Form(...), email: str = Form(...), message: str = Form(...)):
    try:
        ws = get_worksheet("Contacts")
        ws.append_row([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, email, message])
        # thank you to user is optional for contact; admin alert can be sent if desired
        return {"status":"success","message":"Contact saved"}
    except Exception as e:
        raise HTTPException(500, f"Contact error: {e}")

@router.post("/join-beta")
def join_beta(
    name: str = Form(...),
    email: str = Form(...),
    company: str = Form(...),
    role_title: str = Form(...),
    role_level: str | None = Form(None),
    linkedin: str | None = Form(None),
    industry: str | None = Form(None),
    company_size: str | None = Form(None),
    region: str | None = Form(None),
    website: str | None = Form(None),
    competitors: str | None = Form(None),
    tools: str | None = Form(None),
    platforms: str | None = Form(None),
    channels: str | None = Form(None),
    budget_focus: str | None = Form(None),
    pain_point: str | None = Form(None),
    expected_outcome: str | None = Form(None),
    metrics: str | None = Form(None),
    data_interest: str | None = Form(None),
    source: str | None = Form(None),
    consent: str | None = Form(None),
    api_key: str | None = Form(None),
):
    # (optional) simple public API key check
    PUBLIC_KEY = os.getenv("PUBLIC_FORM_KEY")
    if PUBLIC_KEY and api_key != PUBLIC_KEY:
        raise HTTPException(403, "Invalid form key")

    try:
        ws = get_worksheet("JoinBeta")
        persona_level = classify_persona_level(role_title, role_level)
        ws.append_row([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            name, email, company, role_title, persona_level, linkedin, industry,
            company_size, region, website, competitors, tools, platforms, channels,
            budget_focus, pain_point, expected_outcome, metrics, data_interest, source, str(consent or "")
        ])

        # Send emails (best-effort)
        try:
            send_thank_you(email, name)
            notify_admin(name, email, company, role_title)
        except Exception as mail_err:
            print("Mail error:", mail_err)

        return {"status":"success","message":"Join Beta saved"}
    except Exception as e:
        raise HTTPException(500, f"JoinBeta error: {e}")

@router.get("/admin/view")
def admin_view(limit: int = 25, key: str | None = None):
    ADMIN_KEY = os.getenv("ADMIN_KEY", "neura123")
    if key != ADMIN_KEY:
        raise HTTPException(403, "Unauthorized")
    ws = get_worksheet("JoinBeta")
    rows = ws.get_all_values()
    headers = rows[0] if rows else []
    data = rows[1:limit+1]
    return [dict(zip(headers, r)) for r in data]
