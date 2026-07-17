"""ES/PT/TR/UK names for natal.py (TZ-080): planets and zodiac signs.

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n.
PLANET_NAMES_I18N is keyed by planet key (e.g. "sun", "true_node");
SIGNS_I18N is keyed by the normalized English sign name (e.g. "Aries").

Scope note: aspect names (ASPECT_TYPES) already have ru/en from TZ-076/079
and the 5 long natal interpretation prompt templates (SECTION_PROMPTS_RU/EN)
are handled separately (TZ-080 Module 5) — this module only covers the
short planet/sign labels.

Empty until scripts/generate_structural_translations.py --section natal
populates it; localized_field() falls back to English for any language not
present here yet.
"""





































































































PLANET_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "chiron": {
            "name": "Quirón"
        },
        "jupiter": {
            "name": "Júpiter"
        },
        "mars": {
            "name": "Marte"
        },
        "mercury": {
            "name": "Mercurio"
        },
        "moon": {
            "name": "Luna"
        },
        "neptune": {
            "name": "Neptuno"
        },
        "pluto": {
            "name": "Plutón"
        },
        "saturn": {
            "name": "Saturno"
        },
        "south_node": {
            "name": "Nodo Sur"
        },
        "sun": {
            "name": "Sol"
        },
        "true_node": {
            "name": "Nodo Norte"
        },
        "uranus": {
            "name": "Urano"
        },
        "venus": {
            "name": "Venus"
        }
    },
    "pt": {
        "chiron": {
            "name": "Quíron"
        },
        "jupiter": {
            "name": "Júpiter"
        },
        "mars": {
            "name": "Marte"
        },
        "mercury": {
            "name": "Mercúrio"
        },
        "moon": {
            "name": "Lua"
        },
        "neptune": {
            "name": "Netuno"
        },
        "pluto": {
            "name": "Plutão"
        },
        "saturn": {
            "name": "Saturno"
        },
        "south_node": {
            "name": "Nó Sul"
        },
        "sun": {
            "name": "Sol"
        },
        "true_node": {
            "name": "Nó Norte"
        },
        "uranus": {
            "name": "Urano"
        },
        "venus": {
            "name": "Vênus"
        }
    },
    "tr": {
        "chiron": {
            "name": "Kiron"
        },
        "jupiter": {
            "name": "Jüpiter"
        },
        "mars": {
            "name": "Mars"
        },
        "mercury": {
            "name": "Merkür"
        },
        "moon": {
            "name": "Ay"
        },
        "neptune": {
            "name": "Neptün"
        },
        "pluto": {
            "name": "Plüton"
        },
        "saturn": {
            "name": "Satürn"
        },
        "south_node": {
            "name": "Güney Düğümü"
        },
        "sun": {
            "name": "Güneş"
        },
        "true_node": {
            "name": "Kuzey Düğümü"
        },
        "uranus": {
            "name": "Uranüs"
        },
        "venus": {
            "name": "Venüs"
        }
    },
    "uk": {
        "chiron": {
            "name": "Хірон"
        },
        "jupiter": {
            "name": "Юпітер"
        },
        "mars": {
            "name": "Марс"
        },
        "mercury": {
            "name": "Меркурій"
        },
        "moon": {
            "name": "Місяць"
        },
        "neptune": {
            "name": "Нептун"
        },
        "pluto": {
            "name": "Плутон"
        },
        "saturn": {
            "name": "Сатурн"
        },
        "south_node": {
            "name": "Півд. вузол"
        },
        "sun": {
            "name": "Сонце"
        },
        "true_node": {
            "name": "Півн. вузол"
        },
        "uranus": {
            "name": "Уран"
        },
        "venus": {
            "name": "Венера"
        }
    }
}
SIGNS_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "Aquarius": {
            "name": "Acuario"
        },
        "Aries": {
            "name": "Aries"
        },
        "Cancer": {
            "name": "Cáncer"
        },
        "Capricorn": {
            "name": "Capricornio"
        },
        "Gemini": {
            "name": "Géminis"
        },
        "Leo": {
            "name": "Leo"
        },
        "Libra": {
            "name": "Libra"
        },
        "Pisces": {
            "name": "Piscis"
        },
        "Sagittarius": {
            "name": "Sagitario"
        },
        "Scorpio": {
            "name": "Escorpio"
        },
        "Taurus": {
            "name": "Tauro"
        },
        "Virgo": {
            "name": "Virgo"
        }
    },
    "pt": {
        "Aquarius": {
            "name": "Aquário"
        },
        "Aries": {
            "name": "Áries"
        },
        "Cancer": {
            "name": "câncer"
        },
        "Capricorn": {
            "name": "Capricórnio"
        },
        "Gemini": {
            "name": "Gêmeos"
        },
        "Leo": {
            "name": "Leão"
        },
        "Libra": {
            "name": "Libra"
        },
        "Pisces": {
            "name": "Peixes"
        },
        "Sagittarius": {
            "name": "Sagitário"
        },
        "Scorpio": {
            "name": "Escorpião"
        },
        "Taurus": {
            "name": "Touro"
        },
        "Virgo": {
            "name": "Virgem"
        }
    },
    "tr": {
        "Aquarius": {
            "name": "Kova"
        },
        "Aries": {
            "name": "Koç"
        },
        "Cancer": {
            "name": "kanser"
        },
        "Capricorn": {
            "name": "Oğlak"
        },
        "Gemini": {
            "name": "İkizler"
        },
        "Leo": {
            "name": "Aslan"
        },
        "Libra": {
            "name": "Terazi"
        },
        "Pisces": {
            "name": "Balık"
        },
        "Sagittarius": {
            "name": "Yay"
        },
        "Scorpio": {
            "name": "Akrep"
        },
        "Taurus": {
            "name": "Boğa"
        },
        "Virgo": {
            "name": "Başak"
        }
    },
    "uk": {
        "Aquarius": {
            "name": "Водолій"
        },
        "Aries": {
            "name": "Овен"
        },
        "Cancer": {
            "name": "рак"
        },
        "Capricorn": {
            "name": "Козеріг"
        },
        "Gemini": {
            "name": "Близнюки"
        },
        "Leo": {
            "name": "Лев"
        },
        "Libra": {
            "name": "Терези"
        },
        "Pisces": {
            "name": "Риби"
        },
        "Sagittarius": {
            "name": "Стрілець"
        },
        "Scorpio": {
            "name": "Скорпіон"
        },
        "Taurus": {
            "name": "Телець"
        },
        "Virgo": {
            "name": "Діва"
        }
    }
}
