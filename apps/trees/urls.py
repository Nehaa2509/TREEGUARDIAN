"""
apps/trees/urls.py

URL patterns for the trees app.
Included under /api/trees/ in config/urls.py.

Full paths:
    GET  /api/trees/                →  list all trees
    POST /api/trees/                →  register a new tree
    GET  /api/trees/<tree_id>/      →  view a tree's full profile
    PUT  /api/trees/<tree_id>/      →  update a tree
    DELETE /api/trees/<tree_id>/    →  remove a tree from registry

<str:tree_id>:
    The angle brackets define a URL parameter that DRF passes
    to the view method as a keyword argument.
    `str` means it will match any string (e.g. TG-0000001).
"""

from django.urls import path
from .views import TreeListCreateView, TreeDetailView

urlpatterns = [
    path("",           TreeListCreateView.as_view(), name="tree-list"),
    path("<str:tree_id>/", TreeDetailView.as_view(),     name="tree-detail"),
]
