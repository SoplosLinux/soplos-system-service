from utils.gettext.es import STRINGS_ES
from utils.gettext.en import STRINGS_EN
from utils.gettext.fr import STRINGS_FR
from utils.gettext.pt import STRINGS_PT
from utils.gettext.de import STRINGS_DE
from utils.gettext.it import STRINGS_IT
from utils.gettext.ro import STRINGS_RO
from utils.gettext.ru import STRINGS_RU
import os
import locale

STRINGS = {
    "es": STRINGS_ES,
    "en": STRINGS_EN,
    "fr": STRINGS_FR,
    "pt": STRINGS_PT,
    "de": STRINGS_DE,
    "it": STRINGS_IT,
    "ro": STRINGS_RO,
    "ru": STRINGS_RU,
}

def get_string(lang, key):
    """
    Get a string in the specified language, fallback to English.
    """
    dic = STRINGS.get(lang, STRINGS_EN)
    return dic.get(key, STRINGS_EN.get(key, key))

def get_system_language():
    """
    Detect system language and normalize to a supported one.
    """
    lang = None
    for env_var in ['SOPLOS_SYSTEM_SERVICE_LANG', 'LANG', 'LC_ALL']:
        lang_env = os.environ.get(env_var)
        if lang_env:
            lang = lang_env.split('.')[0][:2]
            break
    if not lang:
        lang_locale = locale.getdefaultlocale()[0]
        if lang_locale:
            lang = lang_locale[:2]
    if not lang or lang not in STRINGS:
        lang = 'en'
    return lang

STRINGS_FR = {
    "main.title": "Services système Soplos",
    "sidebar.services": "Services",
    "sidebar.units": "Unités",
    "sidebar.logs": "Journaux",
    "sidebar.about": "À propos",
    "main.placeholder": "La liste des services et les détails apparaîtront ici.",
    "table.name": "Nom",
    "table.loaded": "Chargé",
    "table.active": "Actif",
    "table.sub": "Sous-état",
    "table.description": "Description"
}

STRINGS_PT = {
    "main.title": "Serviços do sistema Soplos",
    "sidebar.services": "Serviços",
    "sidebar.units": "Unidades",
    "sidebar.logs": "Registos",
    "sidebar.about": "Sobre",
    "main.placeholder": "A lista de serviços e detalhes aparecerá aqui.",
    "table.name": "Nome",
    "table.loaded": "Carregado",
    "table.active": "Ativo",
    "table.sub": "Subestado",
    "table.description": "Descrição"
}

STRINGS_DE = {
    "main.title": "Soplos Systemdienste",
    "sidebar.services": "Dienste",
    "sidebar.units": "Einheiten",
    "sidebar.logs": "Protokolle",
    "sidebar.about": "Über",
    "main.placeholder": "Dienstliste und Details werden hier angezeigt.",
    "table.name": "Name",
    "table.loaded": "Geladen",
    "table.active": "Aktiv",
    "table.sub": "Substatus",
    "table.description": "Beschreibung"
}

STRINGS_IT = {
    "main.title": "Servizi di sistema Soplos",
    "sidebar.services": "Servizi",
    "sidebar.units": "Unità",
    "sidebar.logs": "Log",
    "sidebar.about": "Informazioni",
    "main.placeholder": "L'elenco dei servizi e i dettagli appariranno qui.",
    "table.name": "Nome",
    "table.loaded": "Caricato",
    "table.active": "Attivo",
    "table.sub": "Sottostato",
    "table.description": "Descrizione"
}

STRINGS_RO = {
    "main.title": "Servicii de sistem Soplos",
    "sidebar.services": "Servicii",
    "sidebar.units": "Unități",
    "sidebar.logs": "Jurnale",
    "sidebar.about": "Despre",
    "main.placeholder": "Lista serviciilor și detaliile vor apărea aici.",
    "table.name": "Nume",
    "table.loaded": "Încărcat",
    "table.active": "Activ",
    "table.sub": "Substare",
    "table.description": "Descriere"
}

STRINGS_RU = {
    "main.title": "Системные службы Soplos",
    "sidebar.services": "Службы",
    "sidebar.units": "Юниты",
    "sidebar.logs": "Журналы",
    "sidebar.about": "О программе",
    "main.placeholder": "Здесь появится список служб и детали.",
    "table.name": "Имя",
    "table.loaded": "Загружено",
    "table.active": "Активно",
    "table.sub": "Подстатус",
    "table.description": "Описание"
}

STRINGS = {
    "es": STRINGS_ES,
    "en": STRINGS_EN,
    "fr": STRINGS_FR,
    "pt": STRINGS_PT,
    "de": STRINGS_DE,
    "it": STRINGS_IT,
    "ro": STRINGS_RO,
    "ru": STRINGS_RU,
}

def get_string(lang, key):
    """
    Get a string in the specified language, fallback to English.
    """
    dic = STRINGS.get(lang, STRINGS_EN)
    return dic.get(key, STRINGS_EN.get(key, key))
    return dic.get(key, STRINGS_EN.get(key, key))
