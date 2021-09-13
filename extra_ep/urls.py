from django.urls import path

from extra_ep import views, views_new

app_name = 'extra_ep'

urlpatterns = [
    path(r'combat/<int:combat_id>/', views.ItemConsumptionListView.as_view(), name='item_consumption_list'),
    path(r'report/<int:report_id>/total', views.ItemConsumptionTotalListView.as_view(), name='item_consumption_total'),
    path(r'report/<int:report_id>/export', views.ExportReportView.as_view(), name='report_export'),
    path(r'report/<int:report_id>/change_exported', views.ChangeExportedView.as_view(), name='change_exported'),
    path(r'report/<int:report_id>/', views.CombatListView.as_view(), name='combat_list'),

    path(r'report_new/<int:report_id>/', views_new.ReportDetailView.as_view(), name='report_new'),
    path(r'report_new/<int:report_id>/export', views_new.ExportReportView.as_view(), name='report_export_new'),
    path(r'report_new/<int:report_id>/send_to_discord', views_new.DiscordHookView.as_view(), name='send_to_discord'),

    path(r'report/create/', views.CreateReportView.as_view(), name='report_create'),
    path(r'reports/', views.ReportListView.as_view(), name='report_list'),

    path(
        'consumable_info/<int:class_id>/<int:role_id>/',
        views_new.ConsumableSetDetailView.as_view(),
        name='class_role_consumables',
    ),
    path('consumable_info/<int:class_id>/', views_new.ClassRoleListView.as_view(), name='class_roles'),
    path('consumable_info/', views_new.ClassListView.as_view(), name='classes'),

    path('', views.MainRedirectView.as_view()),
]
