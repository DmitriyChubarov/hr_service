from django.urls import path, include

from rest_framework.authtoken.views import obtain_auth_token

from .views import WorkerRetrieveUpdateDestroyAPIView, WorkerListCreateAPIView, WorkerImportAPIView

urlpatterns = [
    path('auth/token/', obtain_auth_token, name='api-token'),
    path('auth/', include('rest_framework.urls')),

    path('workers/', WorkerListCreateAPIView.as_view(), name='workers'),
    path('workers/import/', WorkerImportAPIView.as_view(), name='worker_import'),
    path('workers/<pk>/', WorkerRetrieveUpdateDestroyAPIView.as_view(), name='worker_id'),
]