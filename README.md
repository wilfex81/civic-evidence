# Civic Evidence & Verification

A proof-of-concept platform that connects official civic records with
structured community observations, so people can see what was claimed,
what is being observed, and where the two agree or conflict.

Track: Transparency & Accountability · Country: Kenya

## The problem

Civic information is often fragmented across official announcements,
documents, community conversations, and individual reports. Even when
information is available, citizens may struggle to tell what was
officially stated from what is actually happening on the ground, and
where the two disagree. The gap is not access to information, it is
the gap between information and evidence.

## The solution

Civic Evidence & Verification creates a structured evidence layer
around civic projects and public services:

- **Official record** — what an institution has stated (status, date,
  source).
- **Community observations** — what people report experiencing on the
  ground, each with a date and a stated form of supporting evidence.
- **Evidence status** — a plain verdict computed from the two:
  aligned, conflicting, stale, or not yet evidenced.

The system does not decide what is true. It makes the available
evidence, and any disagreement in it, visible.

## How it works

1. **Find** — search or browse civic projects.
2. **Understand** — view the official status, location, responsible
   organization, and source.
3. **Compare** — review recent community observations and their
   evidence.
4. **See the verdict** — aligned, conflicting, stale, or no evidence
   yet.
5. **Contribute** — submit a new observation.

## Evidence status logic

The verdict is deliberately simple and fully inspectable — see
`evidence/models.py`, `Project.evidence_status()`.

| Condition | Verdict |
|---|---|
| No observations exist at all | **No evidence yet** |
| Observations exist, but none in the last 30 days | **No recent evidence** (stale) |
| Recent observations all match what the official status implies | **Aligned evidence** |
| Recent observations disagree with the official status, with each other, or both | **Conflicting evidence** |

"Matches what the official status implies" is a fixed mapping, for
example an official status of *completed* expects an *operational*
observation, *planned* expects *no activity observed*. There is no
model or scoring involved. An LLM is not used to decide, or influence,
the verdict.

## Architecture

- **Backend**: Django, server-rendered templates (no separate frontend
  build, no JavaScript framework).
- **Database**: SQLite for the PoC (swap `DATABASES` in
  `settings.py` for Postgres in a real deployment).
- **Data**: seeded from `data/projects.json` and `data/observations.json`
  via a management command. Dates in those files are stored as
  `days_ago` and resolved relative to when the command runs, so the
  seeded evidence always looks recent in a live demo regardless of
  when it's run.

```
civic-evidence/
├── civic_evidence/        # Django project settings, root URLs
├── evidence/               # The one app: models, views, templates, static
│   ├── models.py           # Project, Observation, evidence_status()
│   ├── views.py            # home, project_detail, submit_observation
│   ├── forms.py
│   ├── admin.py
│   ├── management/commands/seed_data.py
│   ├── templates/evidence/
│   └── static/evidence/css/style.css
├── data/
│   ├── projects.json
│   └── observations.json
├── requirements.txt
└── manage.py
```

## Data model

**Project** — the official record.
`name`, `slug`, `summary`, `location`, `responsible_organization`,
`official_status` (completed / ongoing / planned / stalled),
`official_status_date`, `source_name`, `source_url`, `is_demo_data`.

**Observation** — a community report, linked to a Project.
`date_observed`, `status` (operational / not_operational / in_progress
/ no_activity / other), `description`, `evidence_type` (photo / video
/ document / testimony), `evidence_note`, `submitted_by`.

The prototype does not require file uploads — evidence is recorded as
a typed claim (`evidence_type` + `evidence_note`) rather than an
attached file, which is enough to demonstrate the workflow.

## Running locally

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data      # loads the demonstration records
python manage.py runserver
```

Visit `http://127.0.0.1:8000/`. Four seeded projects demonstrate all
four evidence-status outcomes:

- **Kimumu Water Project** — conflicting evidence (observations
  disagree on whether water is flowing).
- **Eldoret Central Market Renovation** — aligned evidence.
- **Iten-Kaptagat Road Resurfacing** — no recent evidence (stale).
- **Uasin Gishu Youth Innovation Hub** — no evidence yet.

To reset and reseed: `python manage.py seed_data --flush`.

An admin interface is available at `/admin/` after creating a
superuser (`python manage.py createsuperuser`), useful for inspecting
or editing records during a demo.

## Demo screenshots / video

_Add a link to the demo video and any screenshots here before
submission._

## Limitations

- All project and observation records are seeded demonstration data,
  not verified government records. This is stated on every page.
- Observation submission is open and unauthenticated — anyone can
  submit an observation under any name, including "Anonymous". There
  is no verification of who submitted a report or whether it is
  accurate. A real deployment would need identity or trust signals
  before observations could be treated as reliable.
- Evidence is recorded as a typed claim, not an uploaded file. There
  is no image or document upload, and no way to verify that stated
  evidence actually exists.
- The 30-day recency window and the official-status-to-observation
  mapping are fixed constants, not configurable per project type.
- No real government data integration. No search across sources
  beyond name and location matching.

## Future development

- Verified government data integrations.
- Multilingual and low-bandwidth interfaces.
- Trusted-organization verification for observations.
- Geographic analysis and mapping.
- Automated document ingestion.
- Support for more civic services and public infrastructure types.

## Use of AI tools

AI-assisted development tools were used for coding support,
debugging, documentation, and iteration. The proof of concept does
not use an LLM as a source of truth or as the decision-maker for the
evidence verdict — that logic is explicit, fixed, and inspectable in
`evidence/models.py`.
