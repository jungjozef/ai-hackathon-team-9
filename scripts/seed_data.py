"""Seed the database with sample meeting notes for demo purposes."""

import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import init_db, SessionLocal
from backend.document_processor import store_document

SAMPLE_DOCS = [
    {
        "title": "Engineering Standup – 2025-01-15",
        "content": (
            "Attendees: Alice, Bob, Carlos\n\n"
            "Alice: Finished the auth microservice migration to Go. Latency dropped 40%. "
            "Will start on the caching layer today using Redis.\n\n"
            "Bob: Still debugging the flaky integration tests in CI. Root cause seems to be "
            "race conditions in the database seeder. Should be fixed by EOD.\n\n"
            "Carlos: Deployed the new API gateway (Kong) to staging. Load tests show 12k req/s, "
            "which exceeds our target of 10k. Planning production rollout for Thursday.\n\n"
            "Blockers: Need DevOps to provision a new Redis cluster before caching work can proceed."
        ),
        "tags": ["engineering", "standup", "backend"],
    },
    {
        "title": "Client Meeting – Acme Corp Q1 Review",
        "content": (
            "Client: Acme Corp (Jane Smith, VP Product)\n"
            "Internal: Sarah (Sales), Mike (Delivery)\n\n"
            "Summary:\n"
            "- Acme is happy with the dashboard delivered in December. Usage is up 60% among their teams.\n"
            "- They want to expand the integration to include their Salesforce instance (Q2 priority).\n"
            "- Budget discussion: Acme approved a $150k expansion for Phase 2.\n"
            "- Timeline: SOW to be signed by Feb 1, kickoff Feb 15.\n\n"
            "Action items:\n"
            "1. Sarah to send revised SOW by Jan 20.\n"
            "2. Mike to draft a Phase 2 project plan.\n"
            "3. Engineering to estimate Salesforce integration effort."
        ),
        "tags": ["sales", "client", "acme"],
    },
    {
        "title": "Sprint 14 Retrospective",
        "content": (
            "Sprint 14 (Jan 6 – Jan 17)\n\n"
            "What went well:\n"
            "- Shipped the new notification system on time.\n"
            "- Cross-team collaboration with Design improved significantly.\n"
            "- Zero production incidents this sprint.\n\n"
            "What could be improved:\n"
            "- Story pointing was inconsistent – several 3-pointers turned into 8s.\n"
            "- QA was bottlenecked because test environments were down for 2 days.\n"
            "- Documentation for the notification API is still incomplete.\n\n"
            "Action items:\n"
            "1. Introduce calibration sessions for story pointing.\n"
            "2. Add monitoring alerts for test environment health.\n"
            "3. Assign documentation tickets as part of the Definition of Done."
        ),
        "tags": ["delivery", "retro", "sprint"],
    },
    {
        "title": "Sales Pipeline Update – January 2025",
        "content": (
            "Pipeline summary:\n"
            "- Total qualified leads: 23 (up from 18 last month)\n"
            "- Deals in negotiation: 5 (combined value $420k)\n"
            "- Closed this month: 2 deals ($95k total)\n"
            "- Lost: 1 deal (GlobalTech – went with competitor due to pricing)\n\n"
            "Key opportunities:\n"
            "1. BetaCorp ($200k) – Final presentation scheduled Jan 25. High confidence.\n"
            "2. MegaIndustries ($120k) – Awaiting legal review of contract terms.\n"
            "3. StartupXYZ ($50k) – Pilot completed successfully, expansion likely.\n\n"
            "Marketing attribution: 40% of new leads came from the webinar series, "
            "35% from organic search, 25% from referrals."
        ),
        "tags": ["sales", "pipeline", "monthly"],
    },
]


def seed():
    init_db()
    db = SessionLocal()
    try:
        for doc in SAMPLE_DOCS:
            store_document(db, title=doc["title"], content=doc["content"], tags=doc["tags"])
        print(f"Seeded {len(SAMPLE_DOCS)} documents.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
