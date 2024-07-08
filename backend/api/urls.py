from django.urls import path, include
from rest_framework import routers
from backend.api import views as api_views

router = routers.DefaultRouter()
router.register(f'companies', api_views.CompanyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-presigned-url', api_views.GeneratePresignedUrlView.as_view()),
]
