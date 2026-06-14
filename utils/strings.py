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

_current_lang = "en"


def set_language(lang):
    global _current_lang
    _current_lang = lang if lang in STRINGS else "en"


def get_current_language():
    return _current_lang


def _(key):
    dic = STRINGS.get(_current_lang, STRINGS_EN)
    return dic.get(key, STRINGS_EN.get(key, key))


def get_string(lang, key):
    dic = STRINGS.get(lang, STRINGS_EN)
    return dic.get(key, STRINGS_EN.get(key, key))


def get_system_language():
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
