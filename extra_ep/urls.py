from django.urls import path

from extra_ep import views

app_name = 'extra_ep'

urlpatterns = [

    path(r'report/<int:report_id>/', views.ReportDetailView.as_view(), name='report'),
    path(r'report/<int:report_id>/export', views.ExportReportView.as_view(), name='report_export'),
    path(r'report/<int:report_id>/send_to_discord', views.DiscordHookView.as_view(), name='send_to_discord'),
    path(r'report/<int:report_id>/change_exported', views.ChangeExportedView.as_view(), name='change_exported'),

    path(r'report/create/', views.CreateReportView.as_view(), name='report_create'),
    path(r'reports/', views.ReportListView.as_view(), name='report_list'),

    path(
        'consumable_info/<int:class_id>/<int:role_id>/',
        views.ConsumableSetDetailView.as_view(),
        name='class_role_consumables',
    ),
    path('consumable_info/<int:class_id>/', views.ClassRoleListView.as_view(), name='class_roles'),
    path('consumable_info/', views.ClassListView.as_view(), name='classes'),

    path('', views.MainRedirectView.as_view()),
]
