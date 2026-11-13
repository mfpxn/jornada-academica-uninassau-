"""Proteção básica contra tentativas excessivas."""
from collections import deque
from threading import Lock
from time import monotonic

from flask import current_app, request

_guard = Lock()
_requests = {}


def limitar_formularios():
    if current_app.testing or request.method != "POST":
        return None

    regras = {
        "/professor/login": (8, 300),
        "/inscricao": (15, 600),
    }
    regra = regras.get(request.path)
    if not regra:
        return None

    maximo, janela = regra
    chave = (
        request.path,
        request.remote_addr or "desconhecido"
    )
    instante = monotonic()

    with _guard:
        if len(_requests) > 2000:
            for item, tentativas in list(_requests.items()):
                if not tentativas or instante - tentativas[-1] > 600:
                    del _requests[item]

        tentativas = _requests.setdefault(chave, deque())

        while tentativas and instante - tentativas[0] >= janela:
            tentativas.popleft()

        if len(tentativas) >= maximo:
            return (
                "Muitas tentativas. Aguarde alguns minutos.",
                429,
                {"Retry-After": str(janela)}
            )

        tentativas.append(instante)

    return None
