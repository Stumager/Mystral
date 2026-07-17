"""ES/PT/TR/UK labels for compatibility.py (TZ-080).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n. `key` is
the string index into the matching ru/en list (e.g. SIGNS_I18N["es"]["3"] is
the Spanish name for SIGNS[3]/SIGNS_RU[3]) for the parallel-list sections, or
the planet key (e.g. "sun") for COMPOSITE_PLANET_NAMES_I18N.

Empty until scripts/generate_structural_translations.py --section
compatibility populates it; pick()/localized_field() fall back to English
for any language not present here yet.
"""

























































































































































SIGNS_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "0": {
            "name": "Aries"
        },
        "1": {
            "name": "Tauro"
        },
        "10": {
            "name": "Acuario"
        },
        "11": {
            "name": "Piscis"
        },
        "2": {
            "name": "Géminis"
        },
        "3": {
            "name": "cáncer"
        },
        "4": {
            "name": "Leo"
        },
        "5": {
            "name": "Virgo"
        },
        "6": {
            "name": "Libra"
        },
        "7": {
            "name": "Escorpio"
        },
        "8": {
            "name": "Sagitario"
        },
        "9": {
            "name": "Capricornio"
        }
    },
    "pt": {
        "0": {
            "name": "Áries"
        },
        "1": {
            "name": "Touro"
        },
        "10": {
            "name": "Aquário"
        },
        "11": {
            "name": "Peixes"
        },
        "2": {
            "name": "Gêmeos"
        },
        "3": {
            "name": "Câncer"
        },
        "4": {
            "name": "Leão"
        },
        "5": {
            "name": "Virgem"
        },
        "6": {
            "name": "Libra"
        },
        "7": {
            "name": "Escorpião"
        },
        "8": {
            "name": "Sagitário"
        },
        "9": {
            "name": "Capricórnio"
        }
    },
    "tr": {
        "0": {
            "name": "Koç"
        },
        "1": {
            "name": "Boğa"
        },
        "10": {
            "name": "Kova"
        },
        "11": {
            "name": "Balık"
        },
        "2": {
            "name": "İkizler"
        },
        "3": {
            "name": "kanser"
        },
        "4": {
            "name": "Aslan"
        },
        "5": {
            "name": "Başak"
        },
        "6": {
            "name": "Terazi"
        },
        "7": {
            "name": "Akrep"
        },
        "8": {
            "name": "Yay"
        },
        "9": {
            "name": "Oğlak"
        }
    },
    "uk": {
        "0": {
            "name": "Овен"
        },
        "1": {
            "name": "Телець"
        },
        "10": {
            "name": "Водолій"
        },
        "11": {
            "name": "Риби"
        },
        "2": {
            "name": "Близнюки"
        },
        "3": {
            "name": "Рак"
        },
        "4": {
            "name": "Лев"
        },
        "5": {
            "name": "Діва"
        },
        "6": {
            "name": "Терези"
        },
        "7": {
            "name": "Скорпіон"
        },
        "8": {
            "name": "Стрілець"
        },
        "9": {
            "name": "Козеріг"
        }
    }
}
ELEMENTS_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "0": {
            "name": "Fuego"
        },
        "1": {
            "name": "Tierra"
        },
        "2": {
            "name": "Aire"
        },
        "3": {
            "name": "Agua"
        }
    },
    "pt": {
        "0": {
            "name": "Fogo"
        },
        "1": {
            "name": "Terra"
        },
        "2": {
            "name": "Ar"
        },
        "3": {
            "name": "Água"
        }
    },
    "tr": {
        "0": {
            "name": "Ateş"
        },
        "1": {
            "name": "Dünya"
        },
        "2": {
            "name": "Hava"
        },
        "3": {
            "name": "su"
        }
    },
    "uk": {
        "0": {
            "name": "Вогонь"
        },
        "1": {
            "name": "Земля"
        },
        "2": {
            "name": "Повітря"
        },
        "3": {
            "name": "Вода"
        }
    }
}
CHINESE_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "0": {
            "name": "Rata"
        },
        "1": {
            "name": "buey"
        },
        "10": {
            "name": "Perro"
        },
        "11": {
            "name": "cerdo"
        },
        "2": {
            "name": "Tigre"
        },
        "3": {
            "name": "Conejo"
        },
        "4": {
            "name": "Dragón"
        },
        "5": {
            "name": "Serpiente"
        },
        "6": {
            "name": "Caballo"
        },
        "7": {
            "name": "Cabra"
        },
        "8": {
            "name": "Mono"
        },
        "9": {
            "name": "Gallo"
        }
    },
    "pt": {
        "0": {
            "name": "Rato"
        },
        "1": {
            "name": "Boi"
        },
        "10": {
            "name": "Cachorro"
        },
        "11": {
            "name": "porco"
        },
        "2": {
            "name": "tigre"
        },
        "3": {
            "name": "Coelho"
        },
        "4": {
            "name": "Dragão"
        },
        "5": {
            "name": "Cobra"
        },
        "6": {
            "name": "Cavalo"
        },
        "7": {
            "name": "cabra"
        },
        "8": {
            "name": "Macaco"
        },
        "9": {
            "name": "Galo"
        }
    },
    "tr": {
        "0": {
            "name": "Sıçan"
        },
        "1": {
            "name": "Öküz"
        },
        "10": {
            "name": "Köpek"
        },
        "11": {
            "name": "Domuz"
        },
        "2": {
            "name": "Kaplan"
        },
        "3": {
            "name": "Tavşan"
        },
        "4": {
            "name": "Ejderha"
        },
        "5": {
            "name": "Yılan"
        },
        "6": {
            "name": "At"
        },
        "7": {
            "name": "Keçi"
        },
        "8": {
            "name": "Maymun"
        },
        "9": {
            "name": "Horoz"
        }
    },
    "uk": {
        "0": {
            "name": "Щур"
        },
        "1": {
            "name": "віл"
        },
        "10": {
            "name": "Собака"
        },
        "11": {
            "name": "свиня"
        },
        "2": {
            "name": "Тигр"
        },
        "3": {
            "name": "Кролик"
        },
        "4": {
            "name": "Дракон"
        },
        "5": {
            "name": "змія"
        },
        "6": {
            "name": "кінь"
        },
        "7": {
            "name": "Коза"
        },
        "8": {
            "name": "Мавпа"
        },
        "9": {
            "name": "Півень"
        }
    }
}
COMPOSITE_PLANET_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
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
        "sun": {
            "name": "Sol"
        },
        "uranus": {
            "name": "Urano"
        },
        "venus": {
            "name": "Venus"
        }
    },
    "pt": {
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
        "sun": {
            "name": "Sol"
        },
        "uranus": {
            "name": "Urano"
        },
        "venus": {
            "name": "Vênus"
        }
    },
    "tr": {
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
        "sun": {
            "name": "Güneş"
        },
        "uranus": {
            "name": "Uranüs"
        },
        "venus": {
            "name": "Venüs"
        }
    },
    "uk": {
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
        "sun": {
            "name": "Сонце"
        },
        "uranus": {
            "name": "Уран"
        },
        "venus": {
            "name": "Венера"
        }
    }
}
