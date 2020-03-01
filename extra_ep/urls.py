from django.urls import path

from extra_ep import views

app_name = 'extra_ep'

urlpatterns = [
    path(r'combat/<int:combat_id>/', views.ItemConsumptionListView.as_view(), name='item_consumption_list'),
    path(r'report/<int:report_id>/total', views.ItemConsumptionTotalListView.as_view(), name='item_consumption_total'),
    path(r'report/<int:report_id>/export', views.ExportReportView.as_view(), name='report_export'),
    path(r'report/<int:report_id>/change_exported', views.ChangeExportedView.as_view(), name='change_exported'),
    path(r'report/<int:report_id>/', views.CombatListView.as_view(), name='combat_list'),
    path(r'report/create/', views.CreateReportView.as_view(), name='report_create'),
    path(r'reports/', views.ReportListView.as_view(), name='report_list'),
    path('', views.MainRedirectView.as_view()),
]
