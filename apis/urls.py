from django.urls import path
from .views import TableAPIView, TableRowAPIView

urlpatterns = [
    path('api/table', TableAPIView.as_view(), name='table-create'),
    path('api/table/<int:id>', TableAPIView.as_view(), name='table-update'),
    path('api/table/<int:id>/row',
         TableRowAPIView.as_view(), name='table-row-create'),
    path('api/table/<int:id>/rows',
         TableRowAPIView.as_view(), name='table-row-list'),
]
