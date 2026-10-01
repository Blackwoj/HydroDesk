from . import mock_data as m


def mock_context(request):
    role = getattr(request, "role", None)
    return {
        "role": role,
        "role_label": m.ROLES.get(role, ""),
        "user": m.USERS.get(role, {}),
        "is_staff_role": role in ("hydrogeologist", "operator", "admin"),
        "intakes": m.INTAKES,
        "current_intake": m.INTAKES[0],
        "today": m.TODAY,
        "open_alerts_count": len(m.ALERTS),
    }
