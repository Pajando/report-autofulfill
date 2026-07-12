# Report Auto-Fulfillment

Robot for the [AI Visibility Audit](https://pajando.github.io/ai-visibility-audit/).
Every 20 minutes a GitHub Action reads new lead emails (FormSubmit → Gmail),
builds the personalized AI Visibility Report PDF, and emails it to the lead
automatically.

## One-time setup (2 minutes)

1. Enable 2-Step Verification on the Gmail account (if not already on).
2. Create an **App Password**: https://myaccount.google.com/apppasswords
   → app: "Mail", name: "report robot" → copy the 16-character password.
3. In this repo: **Settings → Secrets and variables → Actions → New repository secret**
   - `GMAIL_USER` = the Gmail address
   - `GMAIL_APP_PASSWORD` = the 16-character app password

Until the secrets exist, the schedule runs and exits harmlessly.

## How it works

- `fulfill.py` — polls IMAP for unseen FormSubmit emails with subject
  "AI Visibility Audit lead", parses the embedded `report_json`, builds the
  CLIENT dict, renders the PDF via `report_template.py`, sends it via SMTP,
  marks the email seen. Failures leave the email unseen for automatic retry.
- Leads with test addresses (example.com etc.) are skipped.
- Old-format leads without `report_json` are left for manual handling.
- Every sent report appears in the Gmail **Sent** folder for auditing.

## Local test (no email)

    pip install reportlab
    python3 fulfill.py --test sample_lead.json
