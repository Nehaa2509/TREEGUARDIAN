"""
apps/trees/views.py

TREEGUARDIAN TREE VIEWS
────────────────────────
TreeListCreateView  →  GET list + POST create
TreeDetailView      →  GET one tree + PUT update + DELETE

IMPORTANT PATTERN: WHY TWO SERIALIZERS IN ONE VIEW?
──────────────────────────────────────────────────
When creating a tree (POST), the client sends data.
When reading a tree (GET), we want to return MORE data (nested user, display labels).

So we use:
  - TreeDetailSerializer for reading (includes everything)
  - TreeDetailSerializer for writing too (it handles create/update)
  - TreeListSerializer for the compact list
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404

from .models import Tree
from .serializers import TreeListSerializer, TreeDetailSerializer


# ─────────────────────────────────────────────────────────────────────────────
# GET  /api/trees/    →  list all active trees
# POST /api/trees/    →  register a new tree
# ─────────────────────────────────────────────────────────────────────────────

class TreeListCreateView(APIView):
    """
    GET  → Returns a list of all active trees (compact format).
    POST → Registers a new tree. Requires authentication.

    IsAuthenticatedOrReadOnly:
        - Anyone (even unauthenticated) can GET the list
        - Only logged-in users can POST a new tree
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        Return a list of all active trees.

        queryset: We filter is_active=True to exclude removed trees.
        """
        trees = Tree.objects.filter(is_active=True)

        # Optional: filter by health status using ?health=AT_RISK
        health_filter = request.query_params.get("health")
        if health_filter:
            trees = trees.filter(health_status=health_filter.upper())

        # Optional: search by name using ?search=neem
        search = request.query_params.get("search")
        if search:
            trees = trees.filter(common_name__icontains=search)

        # Serialize the queryset.
        # `many=True` tells the serializer it's a list, not a single object.
        serializer = TreeListSerializer(trees, many=True)

        return Response(
            {
                "count": trees.count(),
                "trees": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        """
        Register a new tree.

        We pass `context={'request': request}` so the serializer's
        create() method can access the logged-in user.
        """
        serializer = TreeDetailSerializer(
            data=request.data,
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):
            tree = serializer.save()
            return Response(
                {
                    "message": f"Tree {tree.tree_id} registered successfully! 🌱",
                    "tree": TreeDetailSerializer(tree, context={"request": request}).data,
                },
                status=status.HTTP_201_CREATED,
            )


# ─────────────────────────────────────────────────────────────────────────────
# GET    /api/trees/{tree_id}/   →  view a tree's full profile
# PUT    /api/trees/{tree_id}/   →  update a tree's data
# DELETE /api/trees/{tree_id}/   →  remove a tree from the registry
# ─────────────────────────────────────────────────────────────────────────────

class TreeDetailView(APIView):
    """
    GET    → Returns the full tree profile.
    PUT    → Updates tree data. Requires authentication.
    DELETE → Soft-deletes (sets is_active=False). Requires authentication.
    """

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_tree(self, tree_id):
        """
        Helper to fetch a tree by its tree_id (e.g. TG-0000001).

        get_object_or_404:
            If the tree exists → return it
            If it doesn't → automatically return a 404 response
            This saves us writing a try/except every time.
        """
        return get_object_or_404(Tree, tree_id=tree_id, is_active=True)

    def get(self, request, tree_id):
        tree = self.get_tree(tree_id)
        serializer = TreeDetailSerializer(tree, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, tree_id):
        tree = self.get_tree(tree_id)
        serializer = TreeDetailSerializer(
            tree,
            data=request.data,
            partial=True,               # allow updating just some fields
            context={"request": request},
        )
        if serializer.is_valid(raise_exception=True):
            tree = serializer.save()
            return Response(
                {
                    "message": "Tree updated successfully. 🌿",
                    "tree": TreeDetailSerializer(tree, context={"request": request}).data,
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, tree_id):
        """
        SOFT DELETE: We don't actually delete the tree from the database.
        We set is_active=False and it disappears from the public API.

        WHY SOFT DELETE?
        ─────────────────
        A tree's history is valuable data. If we hard-deleted it,
        we'd lose all its records, photos, measurements, and reports.

        With soft delete, we can show: "This tree was recorded at this
        location but is no longer active." That's much more useful.
        """
        tree = self.get_tree(tree_id)
        tree.is_active = False
        tree.health_status = "LOST"
        tree.save()

        return Response(
            {
                "message": f"Tree {tree.tree_id} has been marked as removed from the registry. 💔",
                "tree_id": tree.tree_id,
            },
            status=status.HTTP_200_OK,
        )
