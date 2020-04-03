from django.urls import path

from extra_ep import views, profile_views, raid_views

app_name = 'extra_ep'

urlpatterns = [
    path(r'combat/<int:combat_id>/', views.ItemConsumptionListView.as_view(), name='item_consumption_list'),
    path(r'report/<int:report_id>/total', views.ItemConsumptionTotalListView.as_view(), name='item_consumption_total'),
    path(r'report/<int:report_id>/export', views.ExportReportView.as_view(), name='report_export'),
    path(r'report/<int:report_id>/change_exported', views.ChangeExportedView.as_view(), name='change_exported'),
    path(r'report/<int:report_id>/', views.CombatListView.as_view(), name='combat_list'),
    path(r'report/create/', views.CreateReportView.as_view(), name='report_create'),
    path(r'report/', views.ReportListView.as_view(), name='report_list'),

    path(r'profile/', profile_views.ProfileView.as_view(), name='profile'),
    path(r'profile/deattach_character/<int:character_id>', profile_views.DeattachCharacterView.as_view(), name='deattach_character'),

    path('calendar/static/', raid_views.StaticListView.as_view(), name='static_list'),
    path('calendar/static/<int:pk>/edit/', raid_views.ChangeStaticView.as_view(), name='edit_static_properties'),
    path('calendar/static/<int:pk>/add/', raid_views.AddToStaticView.as_view(), name='add_character_to_static'),
    path('calendar/static/<int:pk>/', raid_views.EditStaticView.as_view(), name='edit_static'),
    path('calendar/static/create/', raid_views.AddStaticView.as_view(), name='add_static'),

    path('', views.MainRedirectView.as_view()),
]
