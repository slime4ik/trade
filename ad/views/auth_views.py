from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from ad.forms import LoginForm, CodeForm, UserRegistrationForm, SetPasswordForm
from ad.utils import set_code_in_redis, check_code_in_redis
from ad.tasks import send_code_to_email
from django.views.decorators.http import require_http_methods
from django.http import HttpRequest, HttpResponse
from ad.models import User
from ad.ad_vars import *

# 1 ЭТАП ввод username и email
@require_http_methods(['GET', 'POST'])
def register_view(request):
    # Проверка на то что пользователь авторизован
    if request.user.is_authenticated:
        return redirect('ad:home')
    # # Проверка есть ли id пользователя в сесси(должен ввести код)
    # if request.session.get('auth_user_id'):
    #     return redirect('ad:verify_code')
    user_data = request.session.get('registration_data', {})
    # Проверка шага пользователя
    if user_data.get('step') == 2:
        return redirect('ad:verify_code_register')
    if user_data.get('step') == 3:
        return redirect('ad:set_password')
    form = UserRegistrationForm(request.POST)
    if form.is_valid():
        print('SLIME+GEP=<3')
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            messages.error(request, MSG_EMAIL_ALREADY_TAKEN)
            print('message_printed')
            return redirect('ad:registration')
        registration_data = {
            'username': username,
            'email': email,
        }
        request.session['registration_data'] = registration_data
        try:
            code = set_code_in_redis(email)
            send_code_to_email.delay(email, code)
            registration_data.update({
                'step': 2
            })
            return redirect('ad:verify_code_register')
            # Выводим ошибку если код не отправился
        except Exception as e:
            print(e)
            messages.error(request, MSG_SEND_CODE_ERROR)
    context = {
        'form': form
    }
    return render(request, 'auth/register.html', context)

# 2 ЭТАП Ввод кода с почты
@require_http_methods(['GET', 'POST'])
def verify_code_register(request: HttpRequest) -> HttpResponse:
    # Проверка вошел ли пользователь в аккаунт
    if request.user.is_authenticated:
        return redirect('ad:home')
    # Проверка прошел ли пользователь 1 этап
    user_data = request.session.get('registration_data', {})
    if user_data.get('step') == 1:
        return redirect('ad:registration')
    if user_data.get('step') == 3:
        return redirect('ad:set_password')
    form = CodeForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']
        # Проверка введеного кода
        if check_code_in_redis(user_data['email'], code):
            user_data.update({
                'step': 3
            })
            request.session['registration_data'] = user_data
            return redirect('ad:set_password')
        else:
            messages.error(request, MSG_INVALID_CODE)
    else:
        form = CodeForm()

    return render(request, 'auth/verify_code_register.html', {'form': form})

# 3 ЭТАП ввод пароля
@require_http_methods(['GET', 'POST'])
def set_password(request):
    if request.user.is_authenticated:
        return redirect('ad:home')
    user_data = request.session.get('registration_data', {})
    if user_data.get('step') != 3:
        return redirect('ad:registration')
    form = SetPasswordForm(request.POST)
    if form.is_valid():
        try:
            # Создаем, сохраняем, логиним
            new_user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=form.cleaned_data['password'],  # Пароль хэшируется автоматически
            )
            login(request, new_user)

            # Удаляем не нужные сессии
            request.session.pop('registration_data', None)
            request.session.pop('auth_user_id', None)

            messages.success(request, MSG_ACCOUNT_CREATED)
            return redirect('ad:home')
        except Exception as e:
            print(e)
            messages.error(request, MSG_REGISTRATION_3_STEP_ISSUE)
    else:
        form = SetPasswordForm()
    context = {
        'form': form
    }
    return render(request, 'auth/set_password.html', context)

# Обратно на 1 ШАГ регистрации
@require_http_methods(['POST'])
def clear_session(request):
    request.session.flush()
    return redirect('ad:registration')
# @require_http_methods(['POST'])
# def resend_code(request):
#     request.session.get('auth_user_id') 

@require_http_methods(['GET', 'POST'])
def login_view(request: HttpRequest) -> HttpResponse:
    # Проверка на то что пользователь авторизован
    if request.user.is_authenticated:
        return redirect('ad:home')
    # Проверка есть ли id пользователя в сесси(должен ввести код)
    if request.session.get('auth_user_id'):
        return redirect('ad:verify_code')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)

            if user:
                try:
                    email = user.email
                    request.session['auth_user_id'] = user.id

                    code = set_code_in_redis(email)
                    send_code_to_email.delay(email, code)

                    return redirect('ad:verify_code')

                except Exception as e:
                    messages.error(request, MSG_SEND_CODE_ERROR)

            else:
                messages.error(request, MSG_INVALID_LOGIN_OR_PASSWORD)
    else:
        form = LoginForm()
    context = {
        'form': form
    }
    return render(request, 'auth/login.html', context)

@require_http_methods(['GET', 'POST'])
def verify_code_login(request: HttpRequest) -> HttpResponse:
    # Проверка вошел ли пользователь в аккаунт
    if request.user.is_authenticated:
        return redirect('ad:home')
    # Проверка отправлен ли пользователю код(если нет редирект на login)
    user_id = request.session.get('auth_user_id')
    if not user_id:
        return redirect('login')
    # Проверка существует ли такой пользователь
    user = get_object_or_404(User, id=user_id)
    if not user:
        return redirect('login')

    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                # Проверка введеного кода
                if check_code_in_redis(user.email, code):
                    login(request, user)
                    del request.session['auth_user_id']
                    request.session.pop('registration_data', None)
                    messages.success(request, MSG_LOGIN_SUCCESS)
                    return redirect('ad:home')
                else:
                    messages.error(request, MSG_INVALID_CODE)
            except Exception:
                messages.error(request, MSG_CODE_ISSUE)
    else:
        form = CodeForm()

    return render(request, 'auth/verify_code_login.html', {'form': form})
