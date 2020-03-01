"""extra_ep URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from extra_ep import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'combat/<int:combat_id>/', views.ItemConsumptionListView.as_view(), name='item_consumption_list'),
    path(r'report/<int:report_id>/', views.CombatListView.as_view(), name='combat_list'),
    path(r'reports/', views.ReportListView.as_view(), name='report_list'),
    path(r'report/<int:report_id>/total', views.ItemConsumptionTotalListView.as_view(), name='item_consumption_total'),

    path(r'^accounts/', include('registration.backends.default.urls')),
]
