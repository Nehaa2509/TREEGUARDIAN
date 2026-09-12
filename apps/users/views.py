"""
apps/users/views.py

WHAT IS AN APIView?
───────────────────
APIView is the most fundamental class-based view in DRF.
You define methods named after HTTP verbs:
    def get(self, request):    →  handles GET requests
    def post(self, request):   →  handles POST requests
    def put(self, request):    →  handles PUT requests
    etc.

WHAT IS request.data?
─────────────────────
DRF's `request.data` is like Django's `request.POST` but:
  - Works for JSON, form data, multipart — anything
  - You use it to read the incoming data the client sent

WHAT IS Response()?
───────────────────
DRF's Response automatically converts Python dicts to JSON
(or HTML if the client wants the browsable API).
You pass it a dict and an optional status code.

WHAT ARE STATUS CODES?
──────────────────────
HTTP status codes tell the client what happened:
    200 OK          → success (GET, PUT)
    201 Created     → new resource created (POST)
    204 No Content  → success but nothing to return (DELETE)
    400 Bad Request → client sent bad data (validation error)
    401 Unauthorized→ not logged in
    403 Forbidden   → logged in but not allowed
    404 Not Found   → resource doesn't exist
    500 Server Error→ our code broke
"""

from django.contrib.auth import login, logout
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/auth/register/
# ─────────────────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    """
    Register a new TreeGuardian user.

    permission_classes = [AllowAny]
    → Anyone can access this endpoint, even without being logged in.
      (Of course — you need to register before you can log in!)
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # Step 1: Pass the incoming data to the serializer
        serializer = RegisterSerializer(data=request.data)

        # Step 2: Validate.
        # If data is invalid, serializer.errors will have helpful messages.
        # raise_exception=True automatically returns a 400 response — no extra code needed.
        if serializer.is_valid(raise_exception=True):

            # Step 3: Save — this calls our custom create() method in the serializer
            user = serializer.save()

            # Step 4: Return the new user's profile (minus password)
            return Response(
                {
                    "message": "Welcome to TreeGuardian! 🌳",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,  # 201 = something was created
            )


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/auth/login/
# ─────────────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    """
    Log in with username + password.

    For Level 1 we use Django's built-in session-based login.
    In Level 3 we'll replace this with JWT tokens.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data["user"]

            # log in — creates a session cookie
            login(request, user)

            return Response(
                {
                    "message": f"Welcome back, {user.full_name}! 🌿",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )


# ─────────────────────────────────────────────────────────────────────────────
# POST /api/auth/logout/
# ─────────────────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    """
    Log out — destroy the session.
    """

    def post(self, request):
        logout(request)
        return Response(
            {"message": "You have been logged out."},
            status=status.HTTP_200_OK,
        )


# ─────────────────────────────────────────────────────────────────────────────
# GET /api/auth/profile/      — view your profile
# PUT /api/auth/profile/      — update your profile
# ─────────────────────────────────────────────────────────────────────────────

class ProfileView(APIView):
    """
    Get or update the logged-in user's profile.

    IsAuthenticated means: only logged-in users can access this.
    If an unauthenticated user tries, DRF returns 401 automatically.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # `request.user` — DRF automatically attaches the logged-in user here
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        # partial=True lets the user update only some fields (PATCH behaviour)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {
                    "message": "Profile updated successfully.",
                    "user": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
