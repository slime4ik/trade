from django.shortcuts import render, redirect, get_object_or_404
from ad.models import Ad, ExchangeProposal
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from ad.forms import AdForm, SearchForm, ExchangeProposalForm
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required # Будет 404 так как страница входа отсутствует
from django.contrib import messages
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from ad.ad_vars.variables import *
# import logging
# logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["GET"])
def home(request: HttpRequest) -> HttpResponse:
    return render(request, 'base.html')

@login_required
@require_http_methods(["GET"])
def ad_list(request: HttpRequest) -> HttpResponse:
    ads = Ad.objects\
    .select_related('user', 'category')\
    .only('title', 'condition', 'user', 'category')\
    .order_by('-created_at')
    #====== PAGINATOR ========
    paginator = Paginator(ads, ADS_PER_PAGE)
    page_number = request.GET.get('page')
    ads = paginator.get_page(page_number)
    #====== PAGINATOR ========
    context = {
        'ads': ads,
    }
    return render(request, 'ad_list.html', context)

@login_required
@require_http_methods(["GET"])
def ad_detail(request: HttpRequest, ad_id: str) -> HttpResponse:
    ad = get_object_or_404(Ad.objects.select_related('user', 'category'),
                           article=ad_id)
    form = ExchangeProposalForm(user=request.user) if request.user.is_authenticated else None
    context = {
        'ad': ad,
        'form': form
    }
    return render(request, 'ad_detail.html', context)

@login_required
@require_http_methods(["GET", "POST"])
def ad_edit(request: HttpRequest, ad_id: str) -> HttpResponse:
    ad = get_object_or_404(Ad.objects.select_related('user', 'category'), article=ad_id)
    if request.user != ad.user:
        return HttpResponseForbidden(MSG_NO_PERMISSION)
    if request.method == 'POST':
        form = AdForm(request.POST, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, MSG_AD_EDITED)
            return redirect('ad:ad_detail', ad_id=ad.article)
    else:
        form = AdForm(instance=ad)

    context = {
        'form': form,
    }
    return render(request, 'ad_edit.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def ad_create(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        form = AdForm(request.POST)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.user = request.user
            ad.save()
            messages.success(request, MSG_AD_CREATED)
            return redirect('ad:ad_detail', ad_id=ad.article)
    else:
        form = AdForm()
    context = {
        'form': form,
    }
    return render(request, 'ad_create.html', context)

@login_required
@require_http_methods(['POST'])
def ad_delete(request: HttpRequest, ad_id: str) -> HttpResponse:
    ad = get_object_or_404(Ad.objects.select_related('user', 'category'), article=ad_id)

    if request.user != ad.user:
       return HttpResponseForbidden(MSG_NO_PERMISSION)
    
    ad.delete()
    messages.success(request, MSG_AD_DELETED)
    return redirect('ad:ad_list')

@login_required
@require_http_methods(['GET'])
def ad_search(request: HttpRequest) -> HttpResponse:
    form = SearchForm(request.GET)
    ads = Ad.objects\
    .select_related('user', 'category')\
    .only('title', 'condition', 'user', 'category')\
    .order_by('-created_at')
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        condition = form.cleaned_data.get('condition')
    # 222 Поиск обьявлений по вводу пользователя 222
        if query:
            ads = ads.annotate(
                search=SearchVector('title', 'description', 'article'),
                rank=SearchRank(
                    SearchVector('title', weight='A') + 
                    SearchVector('description', weight='B') +
                    SearchVector('article', weight='C'), # Низкий приоритет т.к. предполагается что артикул будет совпадать с query
                    SearchQuery(query)
                )
            ).filter(search=SearchQuery(query))\
            .order_by('-rank')
    # 222 Поиск обьявлений по вводу пользователя 222
        # Фильтрация по категории и состоянию
        if category:
            ads = ads.filter(category=category)
        if condition:
            ads = ads.filter(condition=condition)
        # Фильтрация по категории и состоянию
    #---ПАГИНАЦИЯ---
    paginator = Paginator(ads, ADS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    #---ПАГИНАЦИЯ---
    # Сохраняем все GET-параметры кроме page
    get_params = request.GET.copy()
    if 'page' in get_params:
        del get_params['page']

    context = {
        'ads': page_obj,
        'is_search': True,
        'search_params': get_params.urlencode()  # Добавляем параметры поиска чтоб пагинация не сломалась
    }
    return render(request, 'ad_search.html', context)

@login_required
@require_http_methods(["POST"])
def exchange_proposal(request: HttpRequest, ad_id: str) -> HttpResponse:
    ad = get_object_or_404(Ad, article=ad_id)
    form = ExchangeProposalForm(request.POST, user=request.user)
    if form.is_valid():
        proposal = form.save(commit=False)
        proposal.ad_receiver = ad
        # ---проверка есть ли уже такое предложение---
        already_exists = ExchangeProposal.objects.filter(
            ad_sender=proposal.ad_sender,
            ad_receiver=proposal.ad_receiver
        ).exists()
        if already_exists:
            messages.warning(request, 'Вы уже отправляли предложение на этот товар.')
        elif proposal.ad_sender.user == proposal.ad_receiver.user:
            messages.warning(request, 'Вы не можете отправить предложение обмена самому себе.')
        else:
            proposal.save()
            messages.success(request, 'Предложение отправлено!')
            return redirect('ad:ad_detail', ad_id=ad.article)
        # ---проверка есть ли уже такое предложение---
    #Если форма не валидна показываем ошибки и форму на этой же странице
    return render(request, 'ad_detail.html', {
        'ad': ad,
        'form': form
    })

@login_required
@require_http_methods(['GET'])
def my_exchanges(request: HttpRequest) -> HttpResponse:
    ru = request.user
    status_filter = request.GET.get('status', None)
    
    exchanges = ExchangeProposal.objects.\
                select_related('ad_sender__user', 'ad_receiver__user', 'ad_sender', 'ad_receiver').\
                filter(ad_receiver__user=ru)
    
    # Применяем фильтр если он есть
    if status_filter and status_filter in ['pending', 'accepted', 'rejected']:
        exchanges = exchanges.filter(status=status_filter)
    
    context = {
        'exchanges': exchanges,
        'current_status': status_filter  # Передаем текущий фильтр в шаблон
    }
    return render(request, 'exchange.html', context)

@login_required
@require_http_methods(['POST'])
def accept(request: HttpRequest, ex_id: int) -> HttpResponse:
    ex = get_object_or_404(ExchangeProposal, id=ex_id)
    if request.user != ex.ad_receiver.user:
        return HttpResponseForbidden(MSG_NO_PERMISSION)
    else:
        ex.status = 'accepted'
        ex.save()
        messages.success(request, MSG_ACCEPTED)
        return redirect('ad:exchanges')

@login_required
@require_http_methods(['POST'])
def reject(request: HttpRequest, ex_id: int) -> HttpResponse:
    ex = get_object_or_404(ExchangeProposal, id=ex_id)
    if request.user != ex.ad_receiver.user:
        return HttpResponseForbidden(MSG_NO_PERMISSION)
    else:
        ex.status = 'rejected'
        ex.save()
        messages.success(request, MSG_REJECTED)
        return redirect('ad:exchanges')
    