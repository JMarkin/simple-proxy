def gen_dict_extract(key, var, func):
    """Поиск опр ключа в словаре в глубину и вызов функции изменения

    Args:
        key (str): ключ
        var (dict): словарь
        func (typing.Callable): функция на измнение

    Yields:
        typing.Any: новое значение
    """
    if hasattr(var, "items"):
        for k, v in var.items():
            if k == key and isinstance(v, str):
                func(var, key)
                yield v, var[key]
            if isinstance(v, dict):
                for result in gen_dict_extract(key, v, func):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in gen_dict_extract(key, d, func):
                        yield result
