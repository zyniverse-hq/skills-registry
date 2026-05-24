# Example: a finished daily status report

A sample of what the skill produces after the interview is complete. The
section headers and ordering match `assets/report-template.txt` exactly —
empty sections are omitted.

```
Time Spent: 8

Today's Activities:

Project: Acme Portal

Done
Meeting with Client X
Done (but not tested on staging)
SendGrid Implementation
Create helper function to send emails using SendGrid
Setting up of Webhook to read delivery status for the email from SendGrid
In Progress
CI setup for Unit testing on GitHub

Need Discussion
Check with client, whether the linking between the unit and linked unit is with units or with residents.
How is linked unit setup different for College building and residential building.

Regards,
Jane Doe
```

## Notes on the format

- Items are plain lines under their section header — no `-` or `*` bullets.
- `Done (but not tested on staging)` exists because clients want to know which
  finished work still needs QA before they review it on staging.
- `Need Discussion` is the most valuable section for the client — it surfaces
  blockers and decisions they owe back. Never silently drop it.
- `Project:` is a single line — even when multiple repos are configured, the
  client sees one project, not the internal repo layout.
