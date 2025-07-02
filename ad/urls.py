from django.urls import path
from .views import (
    home,
    ad_list,
    ad_detail,
    ad_edit,
    ad_delete,
    ad_create,
    ad_search,
    exchange_proposal,
    my_exchanges,
    accept,
    reject,
)

app_name = 'ad'

urlpatterns = [
    path('', home, name='ad_list'),
    path('ads/', ad_list, name='ad_list'),
    path('detail/<str:ad_id>/', ad_detail, name='ad_detail'),
    path('edit/<str:ad_id>/', ad_edit, name='ad_edit'),
    path('delete/<str:ad_id>/', ad_delete, name='ad_delete'),
    path('ad/create/', ad_create, name='ad_create'),
    path('search/', ad_search, name='ad_search'),
    path('exchange/<str:ad_id>/', exchange_proposal, name='exchange'),
    path('my_exchanges/', my_exchanges, name='exchanges'),
    path('accept/<int:ex_id>/', accept, name='accept'),
    path('reject/<int:ex_id>/', reject, name='reject')
]