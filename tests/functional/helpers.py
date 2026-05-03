from __future__ import annotations

import time
from typing import Callable, Any

from django.utils.formats import number_format
from selenium.common.exceptions import WebDriverException


def esperar_condicion(funcion: Callable, tiempo=5, *args, **kwargs) -> Any:
    arranque = time.time()
    while True:
        try:
            return funcion(*args, **kwargs)
        except (AssertionError, WebDriverException) as noesperomas:
            if time.time() - arranque > tiempo:
                raise noesperomas
            time.sleep(0.2)


def float_format(num: str | float, lugares: int = 2) -> str:
    return number_format(round(float(num), lugares), lugares)


def format_float(num: str) -> float:
    return float(num.replace(',', '.'))
