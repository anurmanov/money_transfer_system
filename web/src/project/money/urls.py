from django.urls import path, re_path, include
from django.conf.urls import url
from money.views import CurrencyListView, CourseListView, AccountListForOwnerView, AccountListView, TransferListView, TransferCreateView

urlpatterns = [
    path('currencies/', CurrencyListView.as_view(), name='currency_list'),
    path('courses/', CourseListView.as_view(), name='course_list'),
    path('transfers/create/', TransferCreateView.as_view(), name='transfer_create'),
    path('transfers/', TransferListView.as_view(), name='transfer_list'),
]