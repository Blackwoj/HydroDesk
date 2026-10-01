"""Widoki makiety — wyłącznie odczyt zmockowanych danych, formularze niczego nie zapisują."""
import json

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from . import mock_data as m


def is_htmx(request) -> bool:
    return request.headers.get("HX-Request") == "true"


def login_view(request):
    if request.method == "POST":
        role = request.POST.get("role", "client")
        if role not in m.ROLES:
            role = "client"
        request.session["role"] = role
        return redirect("staff_dashboard" if role in ("hydrogeologist", "operator", "admin") else "dashboard")
    return render(request, "ui/login.html", {"roles": m.ROLES, "users": m.USERS})


@require_POST
def logout_view(request):
    request.session.flush()
    return redirect("login")


def dashboard(request):
    ab = m.abstraction()
    upcoming = sorted(m.OBLIGATIONS, key=lambda o: o["days"])[:3]
    action_count = sum(a["severity"] == "action" for a in m.ALERTS)
    watch_count = sum(a["severity"] == "watch" for a in m.ALERTS)
    return render(request, "ui/dashboard.html", {
        "quality": m.quality_summary(),
        "abstraction": ab,
        "wells": [m.WELLS[c] for c in m.INTAKES[0]["wells"]],
        "permit": m.PERMIT,
        "obligations": upcoming,
        "alerts": m.ALERTS[:3],
        "action_count": action_count,
        "watch_count": watch_count,
        "nav": "dashboard",
    })


def staff_dashboard(request):
    return render(request, "ui/staff_dashboard.html", {
        "q": m.STAFF_QUEUE, "consultations": m.CONSULTATIONS, "nav": "staff",
    })


def intake(request, intake_id: int):
    item = next((i for i in m.INTAKES if i["id"] == intake_id), None)
    if item is None:
        raise Http404
    wells = [m.WELLS[c] for c in item["wells"] if c in m.WELLS]
    return render(request, "ui/intake.html", {"intake": item, "wells": wells, "permit": m.PERMIT, "nav": "intake"})


def well(request, code: str):
    w = m.WELLS.get(code)
    if w is None:
        raise Http404
    series = m.well_series(code)
    return render(request, "ui/well.html", {
        "well": w,
        "history": m.well_history(code),
        "series_json": json.dumps(series),
        "obligations": [o for o in m.OBLIGATIONS if o["well"] == code],
        "alerts": [a for a in m.ALERTS if a.get("well") == code],
        "nav": "intake",
    })


def water_quality(request):
    rows = m.parameters()
    group = request.GET.get("group")
    if group:
        rows = [r for r in rows if r["group"] == group]
    status = request.GET.get("status")
    if status:
        rows = [r for r in rows if r["status"] == status]
    ctx = {"rows": rows, "summary": m.quality_summary(), "group": group, "status": status, "nav": "quality"}
    if is_htmx(request):
        return render(request, "ui/partials/quality_table.html", ctx)
    return render(request, "ui/water_quality.html", ctx)


def parameter(request, code: str):
    try:
        series = m.parameter_series(code)
    except StopIteration:
        raise Http404
    row = next(r for r in m.parameters() if r["code"] == code)
    return render(request, "ui/parameter.html", {
        "row": row, "series_json": json.dumps(series), "series": series,
        "is_mn": code == "Mn", "nav": "quality",
    })


def abstraction(request):
    ab = m.abstraction()
    return render(request, "ui/abstraction.html", {"ab": ab, "ab_json": json.dumps(ab), "nav": "abstraction"})


def permit(request):
    return render(request, "ui/permit.html", {
        "permit": m.PERMIT, "obligations": m.OBLIGATIONS, "limits": m.abstraction()["limits"], "nav": "permit",
    })


def alerts(request):
    items = m.ALERTS
    cat = request.GET.get("category")
    if cat:
        items = [a for a in items if a["category"] == cat]
    categories = sorted({a["category"] for a in m.ALERTS})
    return render(request, "ui/alerts.html", {"alerts": items, "categories": categories, "category": cat, "nav": "alerts"})


def alert_detail(request, alert_id: int):
    a = next((a for a in m.ALERTS if a["id"] == alert_id), None)
    if a is None:
        raise Http404
    return render(request, "ui/alert_detail.html", {"alert": a, "nav": "alerts"})


def form_page(request, template: str, success_title: str, success_next: str, extra=None):
    """Wspólna obsługa formularzy makiety: POST → komunikat sukcesu z „co dalej”."""
    ctx = {"wells": list(m.WELLS.values()), "parameters": m.parameters(), "nav": "add", **(extra or {})}
    if request.method == "POST":
        ctx.update({"success_title": success_title, "success_next": success_next})
        if is_htmx(request):
            return render(request, "ui/partials/form_success.html", ctx)
        messages.success(request, success_title)
        return redirect("dashboard")
    return render(request, template, ctx)


def measurement_add(request):
    return form_page(
        request, "ui/measurement_add.html",
        "Pomiar zapisany",
        "Depresja i wydajność jednostkowa zostały wyliczone. Obowiązek „Pomiar zwierciadła” został oznaczony jako wykonany — następny termin: 13.01.2027.",
        {"selected_well": request.GET.get("well", "S-2")},
    )


def analysis_add(request):
    return form_page(
        request, "ui/analysis_add.html",
        "Analiza przekazana do weryfikacji",
        "Hydrogeolog sprawdzi wyniki. Statusy parametrów zostały już przeliczone — zobacz zakładkę Jakość wody.",
    )


def abstraction_add(request):
    return form_page(
        request, "ui/abstraction_add.html",
        "Pobór zapisany",
        "Wykorzystanie limitu rocznego: 68%. Prognoza na koniec roku: 91% — mieścisz się w limicie.",
    )


def document_add(request):
    return form_page(
        request, "ui/document_add.html",
        "Dokument dodany",
        "Oryginał został zachowany. Jeśli to wyniki z laboratorium, możesz od razu zaimportować z niego dane.",
    )


def consultation_new(request):
    alert_id = request.GET.get("alert")
    a = next((a for a in m.ALERTS if str(a["id"]) == alert_id), None)
    return form_page(
        request, "ui/consultation_new.html",
        "Zgłoszenie wysłane do hydrogeologa",
        "dr Piotr Nowak odpowie zwykle w ciągu 2 dni roboczych. Odpowiedź zobaczysz tutaj i dostaniesz e-mail.",
        {"alert": a},
    )


def consultations(request):
    return render(request, "ui/consultations.html", {"consultations": m.CONSULTATIONS, "nav": "consultations"})


def reports(request):
    return render(request, "ui/reports.html", {"reports": m.REPORTS, "nav": "reports"})


@require_POST
def report_generate(request):
    return render(request, "ui/partials/report_row_new.html", {"today": m.TODAY})
