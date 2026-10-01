from django.shortcuts import redirect

PUBLIC_PATHS = ("/login", "/static/")


class MockRoleMiddleware:
    """Makieta: „zalogowany” = wybrana rola w sesji."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.role = request.session.get("role")
        if request.role is None and not request.path.startswith(PUBLIC_PATHS):
            return redirect("login")
        return self.get_response(request)
