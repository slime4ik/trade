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
    login_view,
    verify_code_login,
    register_view,
    verify_code_register,
    clear_session,
    set_password
)

app_name = 'ad'

urlpatterns = [
    # Главная / Объявления
    path('', home, name='home'),
    path('ads/', ad_list, name='ad_list'),
    path('detail/<str:ad_id>/', ad_detail, name='ad_detail'),
    path('edit/<str:ad_id>/', ad_edit, name='ad_edit'),
    path('delete/<str:ad_id>/', ad_delete, name='ad_delete'),
    path('ad/create/', ad_create, name='ad_create'),
    path('search/', ad_search, name='ad_search'),
    # Авторизация пользователя
    path('login/', login_view, name='login'),
    path('verification/', verify_code_login, name='verify_code'),
    path('registration/', register_view, name='registration'),
    path('registration/verification/', verify_code_register, name='verify_code_register'),
    path('clear_session/', clear_session, name='clear_session'),
    path('registration/set_password/', set_password, name='set_password'),
    # Обмены
    path('exchange/<str:ad_id>/', exchange_proposal, name='exchange'),
    path('my_exchanges/', my_exchanges, name='exchanges'),
    path('accept/<int:ex_id>/', accept, name='accept'),
    path('reject/<int:ex_id>/', reject, name='reject')
]