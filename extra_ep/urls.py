from django.urls import path

from extra_ep import views_new

app_name = 'extra_ep'

urlpatterns = [

    path(r'report_new/<int:report_id>/', views_new.ReportDetailView.as_view(), name='report_new'),
    path(r'report_new/<int:report_id>/export', views_new.ExportReportView.as_view(), name='report_export_new'),
    path(r'report_new/<int:report_id>/send_to_discord', views_new.DiscordHookView.as_view(), name='send_to_discord'),
    path(r'report/<int:report_id>/change_exported', views_new.ChangeExportedView.as_view(), name='change_exported'),

    path(r'report/create/', views_new.CreateReportView.as_view(), name='report_create'),
    path(r'reports/', views_new.ReportListView.as_view(), name='report_list'),

    path(
        'consumable_info/<int:class_id>/<int:role_id>/',
        views_new.ConsumableSetDetailView.as_view(),
        name='class_role_consumables',
    ),
    path('consumable_info/<int:class_id>/', views_new.ClassRoleListView.as_view(), name='class_roles'),
    path('consumable_info/', views_new.ClassListView.as_view(), name='classes'),

    path('', views_new.MainRedirectView.as_view()),
]
