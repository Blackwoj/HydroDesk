from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("zespol/", views.staff_dashboard, name="staff_dashboard"),
    path("ujecia/<int:intake_id>/", views.intake, name="intake"),
    path("studnie/<str:code>/", views.well, name="well"),
    path("jakosc/", views.water_quality, name="water_quality"),
    path("jakosc/parametr/<str:code>/", views.parameter, name="parameter"),
    path("jakosc/dodaj/", views.analysis_add, name="analysis_add"),
    path("pomiary/dodaj/", views.measurement_add, name="measurement_add"),
    path("pobor/", views.abstraction, name="abstraction"),
    path("pobor/dodaj/", views.abstraction_add, name="abstraction_add"),
    path("pozwolenie/", views.permit, name="permit"),
    path("dokumenty/dodaj/", views.document_add, name="document_add"),
    path("alerty/", views.alerts, name="alerts"),
    path("alerty/<int:alert_id>/", views.alert_detail, name="alert_detail"),
    path("konsultacje/", views.consultations, name="consultations"),
    path("konsultacje/nowa/", views.consultation_new, name="consultation_new"),
    path("raporty/", views.reports, name="reports"),
    path("raporty/generuj/", views.report_generate, name="report_generate"),
]
