"""ES/PT/TR/UK card names for tarot.py (TZ-080).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n. `key`
is the string form of the 0-77 card id (0-21 major arcana, 22-77 minor
arcana in suit/rank order). Each of the 78 names is translated as a single
whole string rather than composed from separate suit+rank parts — rank/suit
word order and grammatical case vary by language (e.g. genitive constructions
in Russian/Ukrainian, "de"-phrases in Spanish/Portuguese), so a generic
template would produce incorrect minor-arcana names in several languages.

Empty until scripts/generate_structural_translations.py --section tarot
populates it; localized_field() falls back to English for any language not
present here yet.
"""

























































































































































































































































































































CARD_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "0": {
            "name": "El Loco"
        },
        "1": {
            "name": "El Mago"
        },
        "10": {
            "name": "La Rueda de la Fortuna"
        },
        "11": {
            "name": "Justicia"
        },
        "12": {
            "name": "El Colgado"
        },
        "13": {
            "name": "Muerte"
        },
        "14": {
            "name": "Templanza"
        },
        "15": {
            "name": "El Diablo"
        },
        "16": {
            "name": "La Torre"
        },
        "17": {
            "name": "La Estrella"
        },
        "18": {
            "name": "La Luna"
        },
        "19": {
            "name": "El Sol"
        },
        "2": {
            "name": "Suma Sacerdotisa"
        },
        "20": {
            "name": "Juicio"
        },
        "21": {
            "name": "El Mundo"
        },
        "22": {
            "name": "As de Bastos"
        },
        "23": {
            "name": "Dos de Bastos"
        },
        "24": {
            "name": "Tres de Bastos"
        },
        "25": {
            "name": "Cuatro de Bastos"
        },
        "26": {
            "name": "Cinco de Bastos"
        },
        "27": {
            "name": "Seis de Bastos"
        },
        "28": {
            "name": "Siete de Bastos"
        },
        "29": {
            "name": "Ocho de Bastos"
        },
        "3": {
            "name": "La Emperatriz"
        },
        "30": {
            "name": "Nueve de Bastos"
        },
        "31": {
            "name": "Diez de Bastos"
        },
        "32": {
            "name": "Sota de Bastos"
        },
        "33": {
            "name": "Caballero de Bastos"
        },
        "34": {
            "name": "Reina de Bastos"
        },
        "35": {
            "name": "Rey de Bastos"
        },
        "36": {
            "name": "As de Copas"
        },
        "37": {
            "name": "Dos de Copas"
        },
        "38": {
            "name": "Tres de Copas"
        },
        "39": {
            "name": "Cuatro de Copas"
        },
        "4": {
            "name": "El Emperador"
        },
        "40": {
            "name": "Cinco de Copas"
        },
        "41": {
            "name": "Seis de Copas"
        },
        "42": {
            "name": "Siete de Copas"
        },
        "43": {
            "name": "Ocho de Copas"
        },
        "44": {
            "name": "Nueve de Copas"
        },
        "45": {
            "name": "Diez de Copas"
        },
        "46": {
            "name": "Paje de Copas"
        },
        "47": {
            "name": "Caballero de Copas"
        },
        "48": {
            "name": "Reina de Copas"
        },
        "49": {
            "name": "Rey de Copas"
        },
        "5": {
            "name": "El Hierofante"
        },
        "50": {
            "name": "As de Espadas"
        },
        "51": {
            "name": "Dos de Espadas"
        },
        "52": {
            "name": "Tres de Espadas"
        },
        "53": {
            "name": "Cuatro de Espadas"
        },
        "54": {
            "name": "Cinco de Espadas"
        },
        "55": {
            "name": "Seis de Espadas"
        },
        "56": {
            "name": "Siete de Espadas"
        },
        "57": {
            "name": "Ocho de Espadas"
        },
        "58": {
            "name": "Nueve de Espadas"
        },
        "59": {
            "name": "Diez de Espadas"
        },
        "6": {
            "name": "Los Enamorados"
        },
        "60": {
            "name": "Paje de Espadas"
        },
        "61": {
            "name": "Caballero de Espadas"
        },
        "62": {
            "name": "Reina de Espadas"
        },
        "63": {
            "name": "Rey de Espadas"
        },
        "64": {
            "name": "As de Pentáculos"
        },
        "65": {
            "name": "Dos de Pentáculos"
        },
        "66": {
            "name": "Tres de Pentáculos"
        },
        "67": {
            "name": "Cuatro de Pentáculos"
        },
        "68": {
            "name": "Cinco de Pentáculos"
        },
        "69": {
            "name": "Seis de Pentáculos"
        },
        "7": {
            "name": "El Carro"
        },
        "70": {
            "name": "Siete de Pentáculos"
        },
        "71": {
            "name": "Ocho de Pentáculos"
        },
        "72": {
            "name": "Nueve de Pentáculos"
        },
        "73": {
            "name": "Diez de Pentáculos"
        },
        "74": {
            "name": "Sota de Pentáculos"
        },
        "75": {
            "name": "Caballero de Pentáculos"
        },
        "76": {
            "name": "Reina de Pentáculos"
        },
        "77": {
            "name": "Rey de Pentáculos"
        },
        "8": {
            "name": "Fuerza"
        },
        "9": {
            "name": "El Ermitaño"
        }
    },
    "pt": {
        "0": {
            "name": "O Louco"
        },
        "1": {
            "name": "O Mago"
        },
        "10": {
            "name": "Roda da Fortuna"
        },
        "11": {
            "name": "Justiça"
        },
        "12": {
            "name": "O Enforcado"
        },
        "13": {
            "name": "Morte"
        },
        "14": {
            "name": "Temperança"
        },
        "15": {
            "name": "O Diabo"
        },
        "16": {
            "name": "A Torre"
        },
        "17": {
            "name": "A Estrela"
        },
        "18": {
            "name": "A Lua"
        },
        "19": {
            "name": "O Sol"
        },
        "2": {
            "name": "Suma Sacerdotisa"
        },
        "20": {
            "name": "Julgamento"
        },
        "21": {
            "name": "O Mundo"
        },
        "22": {
            "name": "Ás de Paus"
        },
        "23": {
            "name": "Dois de Paus"
        },
        "24": {
            "name": "Três de Paus"
        },
        "25": {
            "name": "Quatro de Paus"
        },
        "26": {
            "name": "Cinco de Paus"
        },
        "27": {
            "name": "Seis de Paus"
        },
        "28": {
            "name": "Sete de Paus"
        },
        "29": {
            "name": "Oito de Paus"
        },
        "3": {
            "name": "A Imperatriz"
        },
        "30": {
            "name": "Nove de Paus"
        },
        "31": {
            "name": "Dez de Paus"
        },
        "32": {
            "name": "Pajem de Paus"
        },
        "33": {
            "name": "Cavaleiro de Paus"
        },
        "34": {
            "name": "Rainha de Paus"
        },
        "35": {
            "name": "Rei de Paus"
        },
        "36": {
            "name": "Ás de Copas"
        },
        "37": {
            "name": "Dois de Copas"
        },
        "38": {
            "name": "Três de Copas"
        },
        "39": {
            "name": "Quatro de Copas"
        },
        "4": {
            "name": "O Imperador"
        },
        "40": {
            "name": "Cinco de Copas"
        },
        "41": {
            "name": "Seis de Copas"
        },
        "42": {
            "name": "Sete de Copas"
        },
        "43": {
            "name": "Oito de Copas"
        },
        "44": {
            "name": "Nove de Copas"
        },
        "45": {
            "name": "Dez de Copas"
        },
        "46": {
            "name": "Pajem de Copas"
        },
        "47": {
            "name": "Cavaleiro de Copas"
        },
        "48": {
            "name": "Rainha de Copas"
        },
        "49": {
            "name": "Rei de Copas"
        },
        "5": {
            "name": "O Hierofante"
        },
        "50": {
            "name": "Ás de Espadas"
        },
        "51": {
            "name": "Dois de Espadas"
        },
        "52": {
            "name": "Três de Espadas"
        },
        "53": {
            "name": "Quatro de Espadas"
        },
        "54": {
            "name": "Cinco de Espadas"
        },
        "55": {
            "name": "Seis de Espadas"
        },
        "56": {
            "name": "Sete de Espadas"
        },
        "57": {
            "name": "Oito de Espadas"
        },
        "58": {
            "name": "Nove de Espadas"
        },
        "59": {
            "name": "Dez de Espadas"
        },
        "6": {
            "name": "Os Amantes"
        },
        "60": {
            "name": "Pajem de Espadas"
        },
        "61": {
            "name": "Cavaleiro de Espadas"
        },
        "62": {
            "name": "Rainha de Espadas"
        },
        "63": {
            "name": "Rei de Espadas"
        },
        "64": {
            "name": "Ás de Pentáculos"
        },
        "65": {
            "name": "Dois de Pentáculos"
        },
        "66": {
            "name": "Três de Pentáculos"
        },
        "67": {
            "name": "Quatro de Pentáculos"
        },
        "68": {
            "name": "Cinco de Pentáculos"
        },
        "69": {
            "name": "Seis de Pentáculos"
        },
        "7": {
            "name": "A Carruagem"
        },
        "70": {
            "name": "Sete de Pentáculos"
        },
        "71": {
            "name": "Oito de Ouros"
        },
        "72": {
            "name": "Nove de Pentáculos"
        },
        "73": {
            "name": "Dez de Pentáculos"
        },
        "74": {
            "name": "Pajem de Pentáculos"
        },
        "75": {
            "name": "Cavaleiro de Pentáculos"
        },
        "76": {
            "name": "Rainha de Pentáculos"
        },
        "77": {
            "name": "Rei de Pentáculos"
        },
        "8": {
            "name": "Força"
        },
        "9": {
            "name": "O Eremita"
        }
    },
    "tr": {
        "0": {
            "name": "Aptal"
        },
        "1": {
            "name": "Büyücü"
        },
        "10": {
            "name": "Kader Çarkı"
        },
        "11": {
            "name": "Adalet"
        },
        "12": {
            "name": "Asılmış Adam"
        },
        "13": {
            "name": "Ölüm"
        },
        "14": {
            "name": "Ölçülülük"
        },
        "15": {
            "name": "Şeytan"
        },
        "16": {
            "name": "Kule"
        },
        "17": {
            "name": "Yıldız"
        },
        "18": {
            "name": "Ay"
        },
        "19": {
            "name": "Güneş"
        },
        "2": {
            "name": "Yüksek Rahibe"
        },
        "20": {
            "name": "Yargı"
        },
        "21": {
            "name": "Dünya"
        },
        "22": {
            "name": "Asa Ası"
        },
        "23": {
            "name": "İki Değnek"
        },
        "24": {
            "name": "Üç Asa"
        },
        "25": {
            "name": "Dört Değnek"
        },
        "26": {
            "name": "Beş Değnek"
        },
        "27": {
            "name": "Altı Değnek"
        },
        "28": {
            "name": "Yedi Değnek"
        },
        "29": {
            "name": "Sekiz Değnek"
        },
        "3": {
            "name": "İmparatoriçe"
        },
        "30": {
            "name": "Dokuzlu Değnek"
        },
        "31": {
            "name": "Onlu Değnek"
        },
        "32": {
            "name": "Değnek Sayfası"
        },
        "33": {
            "name": "Değnek Şövalyesi"
        },
        "34": {
            "name": "Asalar Kraliçesi"
        },
        "35": {
            "name": "Değnek Kralı"
        },
        "36": {
            "name": "Kupa Ası"
        },
        "37": {
            "name": "İki Kupa"
        },
        "38": {
            "name": "Üç Kupa"
        },
        "39": {
            "name": "Kupa Dörtlüsü"
        },
        "4": {
            "name": "İmparator"
        },
        "40": {
            "name": "Beş Kupa"
        },
        "41": {
            "name": "Altı Kupa"
        },
        "42": {
            "name": "Yedi Kupa"
        },
        "43": {
            "name": "Sekiz Kupa"
        },
        "44": {
            "name": "Dokuz Kupa"
        },
        "45": {
            "name": "Kupa Onlusu"
        },
        "46": {
            "name": "Kupa Valesi"
        },
        "47": {
            "name": "Kupa Şövalyesi"
        },
        "48": {
            "name": "Kupa Kraliçesi"
        },
        "49": {
            "name": "Kupa Kralı"
        },
        "5": {
            "name": "Hiyerofant"
        },
        "50": {
            "name": "Kılıçların Ası"
        },
        "51": {
            "name": "Kılıç İkilisi"
        },
        "52": {
            "name": "Üç Kılıç"
        },
        "53": {
            "name": "Dört Kılıç"
        },
        "54": {
            "name": "Beş Kılıç"
        },
        "55": {
            "name": "Altı Kılıç"
        },
        "56": {
            "name": "Yedi Kılıç"
        },
        "57": {
            "name": "Kılıçların Sekizlisi"
        },
        "58": {
            "name": "Dokuz Kılıç"
        },
        "59": {
            "name": "Kılıçların Onlusu"
        },
        "6": {
            "name": "Aşıklar"
        },
        "60": {
            "name": "Kılıç Sayfası"
        },
        "61": {
            "name": "Kılıç Şövalyesi"
        },
        "62": {
            "name": "Kılıçların Kraliçesi"
        },
        "63": {
            "name": "Kılıçların Kralı"
        },
        "64": {
            "name": "Pentagram Ası"
        },
        "65": {
            "name": "İki Pentagram"
        },
        "66": {
            "name": "Üç Pentakl"
        },
        "67": {
            "name": "Dörtlü Pentakül"
        },
        "68": {
            "name": "Beşli Pentagram"
        },
        "69": {
            "name": "Altılı Pentagram"
        },
        "7": {
            "name": "Araba"
        },
        "70": {
            "name": "Yedi Pentakl"
        },
        "71": {
            "name": "Sekiz Pentakl"
        },
        "72": {
            "name": "Dokuzlu Pentakl"
        },
        "73": {
            "name": "Onlu Pentagram"
        },
        "74": {
            "name": "Pentakl Sayfası"
        },
        "75": {
            "name": "Tılsımların Şövalyesi"
        },
        "76": {
            "name": "Pentakl Kraliçesi"
        },
        "77": {
            "name": "Pentak"
        },
        "8": {
            "name": "Güç"
        },
        "9": {
            "name": "Münzevi"
        }
    },
    "uk": {
        "0": {
            "name": "Дур"
        },
        "1": {
            "name": "Маг"
        },
        "10": {
            "name": "Колесо Фортуни"
        },
        "11": {
            "name": "Справедливість"
        },
        "12": {
            "name": "Повішений"
        },
        "13": {
            "name": "Смерть"
        },
        "14": {
            "name": "Помірність"
        },
        "15": {
            "name": "Диявол"
        },
        "16": {
            "name": "Вежа"
        },
        "17": {
            "name": "Зірка"
        },
        "18": {
            "name": "Місяць"
        },
        "19": {
            "name": "Сонце"
        },
        "2": {
            "name": "Верховна жриця"
        },
        "20": {
            "name": "Суд"
        },
        "21": {
            "name": "Світ"
        },
        "22": {
            "name": "Туз жезлів"
        },
        "23": {
            "name": "Двійка Жезлів"
        },
        "24": {
            "name": "Трійка Жезлів"
        },
        "25": {
            "name": "Четвірка Жезлів"
        },
        "26": {
            "name": "П'ятірка Жезлів"
        },
        "27": {
            "name": "Шістка Жезлів"
        },
        "28": {
            "name": "Сімка Жезлів"
        },
        "29": {
            "name": "Вісімка Жезлів"
        },
        "3": {
            "name": "Імператриця"
        },
        "30": {
            "name": "Дев’ятка Жезлів"
        },
        "31": {
            "name": "Десятка Жезлів"
        },
        "32": {
            "name": "Паж Жезлів"
        },
        "33": {
            "name": "Лицар Жезлів"
        },
        "34": {
            "name": "Королева Жезлів"
        },
        "35": {
            "name": "Король Жезлов"
        },
        "36": {
            "name": "Туз Кубків"
        },
        "37": {
            "name": "Двійка Кубків"
        },
        "38": {
            "name": "Трійка Кубків"
        },
        "39": {
            "name": "Четвірка Кубків"
        },
        "4": {
            "name": "Імператор"
        },
        "40": {
            "name": "П'ятірка Кубків"
        },
        "41": {
            "name": "Шістка Кубків"
        },
        "42": {
            "name": "Сімка Кубків"
        },
        "43": {
            "name": "Вісімка Кубків"
        },
        "44": {
            "name": "Дев'ятка Кубків"
        },
        "45": {
            "name": "Десятка Кубків"
        },
        "46": {
            "name": "Паж Кубків"
        },
        "47": {
            "name": "Лицар Кубків"
        },
        "48": {
            "name": "Королева Кубків"
        },
        "49": {
            "name": "Король Кубків"
        },
        "5": {
            "name": "Ієрофант"
        },
        "50": {
            "name": "Туз Мечів"
        },
        "51": {
            "name": "Двійка Мечів"
        },
        "52": {
            "name": "Трійка Мечів"
        },
        "53": {
            "name": "Четвірка Мечів"
        },
        "54": {
            "name": "П’ятірка Мечів"
        },
        "55": {
            "name": "Шістка Мечів"
        },
        "56": {
            "name": "Сімка Мечів"
        },
        "57": {
            "name": "Вісімка Мечів"
        },
        "58": {
            "name": "Дев'ятка Мечів"
        },
        "59": {
            "name": "Десятка Мечів"
        },
        "6": {
            "name": "Закохані"
        },
        "60": {
            "name": "Паж Мечей"
        },
        "61": {
            "name": "Лицар Мечів"
        },
        "62": {
            "name": "Королева Мечів"
        },
        "63": {
            "name": "Король Мечів"
        },
        "64": {
            "name": "Туз Пентаклів"
        },
        "65": {
            "name": "Двійка Пентаклів"
        },
        "66": {
            "name": "Трійка Пентаклів"
        },
        "67": {
            "name": "Четвірка Пентаклів"
        },
        "68": {
            "name": "П'ятірка Пентаклів"
        },
        "69": {
            "name": "Шістка Пентаклів"
        },
        "7": {
            "name": "Колісниця"
        },
        "70": {
            "name": "Сімка Пентаклів"
        },
        "71": {
            "name": "Вісімка Пентаклів"
        },
        "72": {
            "name": "Дев'ятка Пентаклів"
        },
        "73": {
            "name": "Десятка Пентаклів"
        },
        "74": {
            "name": "Паж Пентаклів"
        },
        "75": {
            "name": "Лицар Пентаклів"
        },
        "76": {
            "name": "Королева Пентаклів"
        },
        "77": {
            "name": "Король Пентаклів"
        },
        "8": {
            "name": "сила"
        },
        "9": {
            "name": "Відлюдник"
        }
    }
}
