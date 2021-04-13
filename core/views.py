from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http.response import Http404, JsonResponse
from django.shortcuts import redirect, render

from core.models import Evento

# Create your views here.


def handler404(request, exception):
    return render(request, '404.html')


def login_user(request):
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return redirect('/')


def submit_login(request):
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')
        usuario = authenticate(username=username, password=password)
        #next_page = req
        if usuario is not None:
            login(request, usuario)
            return redirect('/')
        else:
            messages.error(request, 'Usuário ou senha inválido')
    return redirect('/')


@login_required(login_url='/login/')
def lista_eventos(request):
    usuario = request.user
    data_atual = datetime.now() - timedelta(hours=8)
    evento = Evento.objects.filter(usuario=usuario,
                                   data_evento__gt=data_atual)
    dados = {'eventos': evento}
    return render(request, 'agenda.html', dados)


@login_required(login_url='/login/')
def lista_eventos_historico(request):
    usuario = request.user
    data_atual = datetime.now()
    evento = Evento.objects.filter(
        usuario=usuario,
        data_evento__lt=data_atual)
    dados = {'eventos': evento}
    return render(request, 'historico.html', dados)


@login_required(login_url='/login/')
def evento(request):
    id_evento = request.GET.get('id')
    dados = {}
    if id_evento:
        try:
            dados['evento'] = Evento.objects.get(id=id_evento)
        except Exception:
            raise Http404()
    return render(request, 'evento.html', dados)


@login_required(login_url='/login/')
def submit_evento(request):
    if request.POST:
        id_evento = request.POST.get('id_evento')
        titulo = request.POST.get('titulo')
        data_evento = request.POST.get('data_evento')
        descricao = request.POST.get('descricao')
        local_evento = request.POST.get('local_evento')
        usuario = request.user
        if id_evento:
            evento = Evento.objects.get(id=id_evento)
            if evento.usuario == usuario:
                evento.titulo = titulo
                evento.descricao = descricao
                evento.data_evento = data_evento
                evento.save()
        else:
            Evento.objects.create(
                titulo=titulo,
                data_evento=data_evento,
                descricao=descricao,
                local_evento=local_evento,
                usuario=usuario)
    return redirect('/')


@login_required(login_url='/login/')
def delete_evento(request, id_evento):
    usuario = request.user
    try:
        evento = Evento.objects.get(id=id_evento)
    except Exception:
        raise Http404()
    if usuario == evento.usuario:
        evento.delete()
    else:
        raise Http404()
    return redirect('/')


@login_required(login_url='/login/')
def json_lista_evento(request):
    usuario = request.user
    evento = Evento.objects.filter(usuario=usuario).values(
        'id', 'titulo', 'data_evento', 'local_evento', 'descricao')
    return JsonResponse(list(evento), safe=False)
