"""
Expiring Documents — no database models.

This app is a pure read-only aggregator: it pulls expiry dates from the
`Users` model and the `PersonalDocument` model in the `api` app and returns
a unified list. No new tables, no migrations needed.
"""
