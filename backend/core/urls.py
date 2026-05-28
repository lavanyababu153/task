from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from emissions.views import EmissionLedgerViewSet

router = DefaultRouter()

router.register(r'ledger', EmissionLedgerViewSet, basename='ledger')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]