import time
from typing import Dict, Any, Callable


def get_headers() -> Dict[str, str]:
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Content-Type': 'application/json',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }


def get_risk_dict() -> Dict[str, Dict[str, str]]:
    return {
        'I': {'key': 'income', 'value': 'Уровень дохода ниже ЧБ'},
        'C': {'key': 'credit', 'value': 'Семья имеет задолженность по кредиту больше 90 дней'},
        'M': {'key': 'medical_attachment', 'value': 'Член семьи не имеет прикрепление к медицинской организации'},
        'D': {'key': 'dispensary', 'value': 'Член семьи состоит на диспансерном учете'},
        'O': {'key': 'health_insurance', 'value': 'Член семьи не имеет прикрепление к медицинской организации'},
        'S': {'key': 'preschool', 'value': 'Дети не посещают дошкольные организации'},
        'E': {'key': 'school', 'value': 'Дети не посещают школы'}
    }


def get_social_status_dict() -> Dict[str, int]:
    return {
        'Пенсионеры': 0,
        'Участники и инвалиды ВОВ': 0,
        'Лица, приравненные по льготам и гарантиям к участникам и инвалидам ВОВ': 0,
        'Герои': 0,
        'Участники ликвидации последствий катастрофы на Чернобыльской АЭС': 0,
        'Лица, пострадавшие на Семипалатинском ядерном полигоне': 0,
        'Жертвы политических репрессий': 0,
        'Труженики тыла': 0,
        'Лица, награжденные знаками высшей степени отличия, орденами и медалями, а также удостоенные почетных званий Республики Казахстан': 0,
        'Многодетные матери, награжденные подвесками «Алтын алқа», «Күміс алқа» или получившие ранее звание «Мать-героиня», а также награжденные орденами «Материнская слава» I и II степени': 0,
        'Лица, имеющие группу инвалидности': 0,
        'Лица, осуществляющие уход за инвалидом первой группы с детства': 0,
        'Граждане, имевшие по состоянию на 1 января 1998 года стаж работы по Списку N 1 производств, работ, профессий, должностей и показателей на подземных и открытых горных работах, на работах с особо вредными и особо тяжелыми условиями труда': 0,
        'Граждане, имевшие по состоянию на 1 января 1998 года стаж работы по Списку N 2 производств, работ, профессий, должностей и показателей с вредными и тяжелыми условиями труда': 0,
        'Кандасы': 0,
        'Беременная женщина': 0,
        'Семьи с детьми': 0,
        'Лица обучающиеся в организациях образования, получившие или не имеющие образования': 0,
        'Лица, отбывающие наказание по приговору суда в учреждениях уголовно-исполнительной (пенитенциарной) системы (за исключением учреждений минимальной безопасности)': 0,
        'Лица, содержащиеся в следственных изоляторах': 0,
        'Лица, имеющие судимость': 0,
        'Лица, зарегистрированные в качестве ИП, ИПС и лиц, занимающихся частной практикой': 0,
        'Лица, являющиеся учредителями юридического лица (государственного предприятия, хозяйственного товарищества, акционерного общества, производственного кооператива)': 0,
        'Лица, зарегистрированные в качестве безработных': 0,
        'Домохозяйки': 0,
        'Получатели адресной социальной помощи': 0,
        'Лица, потерявшие кормильца': 0,
        'Лица, не имеющие определенного места жительства, документов': 0,
        'Лица, признанные судом недееспособными или ограниченно-недееспособными': 0,
        'Жертвы бытового насилия': 0,
        'Жертвы торговли людьми': 0,
        'Наемные работники': 0,
        'Дети до 18 лет': 0,
        'Лица, имеющие ЕСП': 0,
        'Лица, имеющие соц отчисления': 0,
        'Военные': 0,
        'Иностранные граждане': 0,
        'Лица пенсионного возраста без статуса': 0,
        'Многодетные семьи': 0,
        'Ветераны боевых действий на территории других государств': 0,
        'Семьи погибших (умерших, пропавших без вести)   военнослужащих': 0,
        'Получатель пособий': 0,
        'Член многодетной семьи ': 0,
        'Лица проживающие в Медико-социальных учреждениях': 0,
        'Беженцы': 0,
    }


def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    """A decorator function that measures the time it takes for another function to execute.
    Args:
        func (function): The function to be timed.
    Returns:
        function: A wrapper function that measures the elapsed time.
    """

    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f'Elapsed time: {elapsed_time:.4f} seconds')
        return result

    return wrapper
