from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('extra_ep.urls')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include(('django.contrib.auth.urls', 'auth'), namespace='auth')),
]