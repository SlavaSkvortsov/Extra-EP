import debug_toolbar
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('extra_ep.urls')),

    path('admin/', admin.site.urls),
    path('select2/', include('django_select2.urls')),
    path('accounts/', include('django_registration.backends.one_step.urls')),
    path('accounts/', include(('django.contrib.auth.urls', 'auth'), namespace='auth')),
    path('__debug__/', include(debug_toolbar.urls)),  # TODO remove
]


admin.site.enable_nav_sidebar = False
