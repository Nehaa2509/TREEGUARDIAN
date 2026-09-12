# TREEGUARDIAN

TREEGUARDIAN now includes a minimal Django REST Framework API for a geospatial tree-conservation platform.

## Features

- Digital identities for individual trees (`Tree.digital_identity` UUID)
- Lifecycle stage tracking and growth history records
- Species and care information per tree
- Evidence-based damage reporting
- Community guardian assignment for trees
- Location-based conservation alerts (`/api/trees/<id>/alerts/`)

## Run tests

```bash
pip install -r requirements.txt
python manage.py test conservation
```
