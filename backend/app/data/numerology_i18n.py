"""ES/PT/TR/UK content for numerology.py (TZ-080).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n.
- NUMBER_DATA_I18N: key is str(number) (e.g. "1", "11", "22"); list fields
  (strengths/challenges/famous) are stored as indexed scalar items
  ("strengths_0", "strengths_1", ...) — see pick_list().
- KARMIC_I18N: key is str(karmic number) (13/14/16/19), field "description".
- CELL_NAMES_I18N / CELL_LEVELS_I18N: key is str(0-9), field "name"/"description".
- LINE_DEFS_I18N: key is str(index into LINE_DEFS), fields "title"/"desc".
- ANGEL_NUMBERS_I18N: key is the angel number string (e.g. "11:11"), field "meaning".

Empty until scripts/generate_structural_translations.py --section numerology
populates it; localized_field()/pick()/pick_list() fall back to English for
any language not present here yet.
"""



































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































NUMBER_DATA_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "1": {
            "career": "Emprendimiento, liderazgo, innovación, freelance.",
            "challenges_0": "egoísmo",
            "challenges_1": "Impaciencia",
            "challenges_2": "Terquedad",
            "description": "Independencia, ambición, pionero. Has nacido para liderar y abrir nuevos caminos. La voluntad fuerte y la determinación son tus principales herramientas.",
            "famous_0": "Napoleón Bonaparte",
            "famous_1": "Steve Jobs",
            "famous_2": "Martin Luther King",
            "love": "Necesita un compañero que respete su independencia. Evite dominar a su pareja.",
            "name": "Uno",
            "strengths_0": "determinación",
            "strengths_1": "iniciativa",
            "strengths_2": "Independencia",
            "strengths_3": "originalidad",
            "title": "Líder"
        },
        "11": {
            "career": "Mentoría espiritual, arte, psicología, invención.",
            "challenges_0": "Tensión nerviosa",
            "challenges_1": "Hipersensibilidad",
            "challenges_2": "conflicto interno",
            "description": "Intuición de orden superior, inspiración, liderazgo espiritual. Ves lo que está oculto para otros y llevas la luz.",
            "famous_0": "Wolfgang Mozart",
            "famous_1": "Barack Obama",
            "famous_2": "Edgar Allan Poe",
            "love": "La conexión espiritual profunda es lo más importante. Busca un alma afín.",
            "name": "Número Maestro 11",
            "strengths_0": "Superintuición",
            "strengths_1": "Inspiración de las masas",
            "strengths_2": "Profundidad espiritual",
            "strengths_3": "carisma",
            "title": "visionario"
        },
        "2": {
            "career": "Mediación, psicología, arte, trabajo en equipo, RR. HH.",
            "challenges_0": "Indecisión",
            "challenges_1": "Dependencia de la opinión de los demás",
            "challenges_2": "Timidez",
            "description": "Armonía, cooperación, intuición. Sientes a las personas en un nivel sutil y sabes encontrar el equilibrio en cualquier situación.",
            "famous_0": "Barack Obama",
            "famous_1": "Madonna",
            "famous_2": "Ronald Reagan",
            "love": "Romántico, busca una conexión emocional profunda. Evite perderse en su pareja.",
            "name": "dos",
            "strengths_0": "diplomacia",
            "strengths_1": "Sensibilidad",
            "strengths_2": "Paciencia",
            "strengths_3": "Pacificación",
            "title": "Diplomático"
        },
        "22": {
            "career": "Arquitectura, grandes negocios, política, proyectos internacionales.",
            "challenges_0": "perfeccionismo",
            "challenges_1": "Presión de la responsabilidad",
            "challenges_2": "Control",
            "description": "Grandes proyectos, materialización de sueños, sabiduría práctica. Construyes para la eternidad, convirtiendo la visión en realidad.",
            "famous_0": "Paul McCartney",
            "famous_1": "Dalái lama",
            "famous_2": "Richard Branson",
            "love": "Se necesita un socio igual que comparta sus ambiciones.",
            "name": "Número Maestro 22",
            "strengths_0": "Pensamiento a gran escala",
            "strengths_1": "Ejecución práctica",
            "strengths_2": "Talento organizador",
            "strengths_3": "Resistencia",
            "title": "Arquitecto"
        },
        "3": {
            "career": "Arte, medios, marketing, enseñanza, entretenimiento.",
            "challenges_0": "Enfoque disperso",
            "challenges_1": "Superficialidad",
            "challenges_2": "Tendencia a criticar",
            "description": "Autoexpresión, inspiración, sociabilidad. Tu energía creativa es contagiosa y atrae a las personas.",
            "famous_0": "Jim Carrey",
            "famous_1": "Christina Aguilera",
            "famous_2": "John Travolta",
            "love": "Compañero divertido y fácil, pero necesita aprender la profundidad en las relaciones.",
            "name": "Tres",
            "strengths_0": "Creatividad",
            "strengths_1": "Optimismo",
            "strengths_2": "Elocuencia",
            "strengths_3": "Artismo",
            "title": "Creador"
        },
        "33": {
            "career": "Sanación, prácticas espirituales, educación, caridad.",
            "challenges_0": "Agotamiento emocional",
            "challenges_1": "autosacrificio",
            "challenges_2": "Perfeccionismo",
            "description": "Compasión de orden superior, enseñanza, amor sacrificial. Usted sana el mundo con su presencia.",
            "famous_0": "Albert Einstein",
            "famous_1": "Francis Bacon",
            "famous_2": "Stephen King",
            "love": "Tu amor es ilimitado, pero no olvides amarte a ti mismo.",
            "name": "Número Maestro 33",
            "strengths_0": "Amor incondicional",
            "strengths_1": "sanación",
            "strengths_2": "Sabiduría",
            "strengths_3": "Abnegación",
            "title": "sanador"
        },
        "4": {
            "career": "Ingeniería, construcción, finanzas, gestión de proyectos.",
            "challenges_0": "rigidez",
            "challenges_1": "trabajolismo",
            "challenges_2": "Conservadurismo",
            "description": "Estabilidad, disciplina, laboriosidad. Usted crea una base sólida para todo lo que emprende.",
            "famous_0": "Bill Gates",
            "famous_1": "Oprah Winfrey",
            "famous_2": "Elton John",
            "love": "Compañero leal y confiable. Necesita aprender espontaneidad y romance.",
            "name": "Cuatro",
            "strengths_0": "Fiabilidad",
            "strengths_1": "Practicidad",
            "strengths_2": "Organización",
            "strengths_3": "resistencia",
            "title": "Constructor"
        },
        "5": {
            "career": "Viajes, periodismo, ventas, startups, consultoría.",
            "challenges_0": "Inconsistencia",
            "challenges_1": "impulsividad",
            "challenges_2": "Miedo al compromiso",
            "description": "Libertad, aventura, cambios. No puedes quedarte quieto y siempre estás en busca de nuevas experiencias.",
            "famous_0": "Abraham Lincoln",
            "famous_1": "Angelina Jolie",
            "famous_2": "Mick Jagger",
            "love": "Necesita libertad en las relaciones. Un compañero no debe ser una jaula.",
            "name": "Cinco",
            "strengths_0": "Adaptabilidad",
            "strengths_1": "Curiosidad",
            "strengths_2": "carisma",
            "strengths_3": "Versatilidad",
            "title": "Buscador"
        },
        "6": {
            "career": "Medicina, educación, diseño, trabajo social, cocina.",
            "challenges_0": "Hipercontrol",
            "challenges_1": "Sacrificio propio",
            "challenges_2": "Perfeccionismo",
            "description": "Cuidado, responsabilidad, familia. Ustedes traen luz y calidez a la vida de sus seres queridos. La armonía es su principal valor.",
            "famous_0": "Albert Einstein",
            "famous_1": "John Lennon",
            "famous_2": "Galileo Galilei",
            "love": "Ideal hombre de familia, pero no hay que olvidarse de uno mismo.",
            "name": "seis",
            "strengths_0": "Naturaleza cariñosa",
            "strengths_1": "Responsabilidad",
            "strengths_2": "Gusto estético",
            "strengths_3": "Lealtad",
            "title": "Guardián"
        },
        "7": {
            "career": "Ciencia, investigación, IT, filosofía, psicología.",
            "challenges_0": "Introversión",
            "challenges_1": "Escepticismo",
            "challenges_2": "Frialdad emocional",
            "description": "Sabiduría, espiritualidad, mente analítica. Buscas el significado profundo en todo y anhelas conocimiento.",
            "famous_0": "Nikola Tesla",
            "famous_1": "Princesa Diana",
            "famous_2": "Vladímir Putin",
            "love": "Necesito un compañero intelectual. Aprende a abrir tus sentimientos.",
            "name": "Siete",
            "strengths_0": "Mente analítica",
            "strengths_1": "Intuición",
            "strengths_2": "profundidad",
            "strengths_3": "Perfeccionismo",
            "title": "Pensador"
        },
        "8": {
            "career": "Negocios, finanzas, bienes raíces, gestión, jurisprudencia.",
            "challenges_0": "Materialismo",
            "challenges_1": "Dominación",
            "challenges_2": "trabajolismo",
            "description": "Poder, éxito, abundancia material. Sabes atraer recursos y gestionar grandes proyectos.",
            "famous_0": "Nelson Mandela",
            "famous_1": "Pablo Picasso",
            "famous_2": "Sandra Bullock",
            "love": "Compañero de estatus. Pero no conviertas las relaciones en un trato.",
            "name": "Ocho",
            "strengths_0": "Perspicacia empresarial",
            "strengths_1": "Autoridad",
            "strengths_2": "Pensamiento estratégico",
            "strengths_3": "Resistencia",
            "title": "Magnate"
        },
        "9": {
            "career": "Caridad, arte, medicina, prácticas espirituales.",
            "challenges_0": "Idealismo",
            "challenges_1": "Decepción en las personas",
            "challenges_2": "Dificultad con los finales",
            "description": "Compasión, sabiduría, culminación. Sirves a un propósito superior y ves el mundo a gran escala.",
            "famous_0": "Mahatma Gandhi",
            "famous_1": "Madre Teresa",
            "famous_2": "Jimi Hendrix",
            "love": "El amor incondicional es tu regalo. No tengas miedo de dejar ir.",
            "name": "nueve",
            "strengths_0": "sabiduría",
            "strengths_1": "Generosidad",
            "strengths_2": "Carisma",
            "strengths_3": "Amplia perspectiva",
            "title": "Humanitario"
        }
    },
    "pt": {
        "1": {
            "career": "Empreendedorismo, liderança, inovação, freelance.",
            "challenges_0": "Egoísmo",
            "challenges_1": "Impaciência",
            "challenges_2": "Teimosia",
            "description": "Independência, ambição, pioneirismo. Você nasceu para liderar e abrir novos caminhos. Força de vontade e determinação são suas principais ferramentas.",
            "famous_0": "Napoleão Bonaparte",
            "famous_1": "Steve Jobs",
            "famous_2": "Martin Luther King",
            "love": "Precisa de um parceiro que respeite sua independência. Evite dominar a sua cara-metade.",
            "name": "Um",
            "strengths_0": "Determinação",
            "strengths_1": "Iniciativa",
            "strengths_2": "Independência",
            "strengths_3": "Originalidade",
            "title": "Líder"
        },
        "11": {
            "career": "Mentoria espiritual, arte, psicologia, invenção.",
            "challenges_0": "Tensão nervosa",
            "challenges_1": "Hipersensibilidade",
            "challenges_2": "conflito interno",
            "description": "Intuição de ordem superior, inspiração, liderança espiritual. Você vê o que está oculto dos outros e carrega a luz.",
            "famous_0": "Wolfgang Mozart",
            "famous_1": "Barack Obama",
            "famous_2": "Edgar Allan Poe",
            "love": "Conexão espiritual profunda é o que mais importa. Busque uma alma gêmea.",
            "name": "Número Mestre 11",
            "strengths_0": "Superintuição",
            "strengths_1": "Inspiração das massas",
            "strengths_2": "Profundidade espiritual",
            "strengths_3": "Carisma",
            "title": "Visionário"
        },
        "2": {
            "career": "Mediação, psicologia, arte, trabalho em equipe, RH.",
            "challenges_0": "Indecisão",
            "challenges_1": "Dependência da opinião dos outros",
            "challenges_2": "Timidez",
            "description": "Harmonia, cooperação, intuição. Você sente as pessoas em um nível sutil e sabe encontrar equilíbrio em qualquer situação.",
            "famous_0": "Barack Obama",
            "famous_1": "Madonna",
            "famous_2": "Ronald Reagan",
            "love": "Romântico, busca uma conexão emocional profunda. Evite se perder no parceiro.",
            "name": "Dois",
            "strengths_0": "Diplomacia",
            "strengths_1": "sensibilidade",
            "strengths_2": "Paciência",
            "strengths_3": "Pacificação",
            "title": "Diplomata"
        },
        "22": {
            "career": "Arquitetura, grandes negócios, política, projetos internacionais.",
            "challenges_0": "Perfeccionismo",
            "challenges_1": "Pressão da responsabilidade",
            "challenges_2": "Problemas de controle",
            "description": "Projetos grandiosos, materialização de sonhos, sabedoria prática. Você constrói para a eternidade, transformando visão em realidade.",
            "famous_0": "Paul McCartney",
            "famous_1": "Dalai Lama",
            "famous_2": "Richard Branson",
            "love": "Precisa de um parceiro igual que compartilhe suas ambições.",
            "name": "Número Mestre 22",
            "strengths_0": "Pensamento em grande escala",
            "strengths_1": "Execução prática",
            "strengths_2": "Talento organizacional",
            "strengths_3": "Resistência",
            "title": "arquiteto"
        },
        "3": {
            "career": "Arte, mídia, marketing, ensino, entretenimento.",
            "challenges_0": "foco disperso",
            "challenges_1": "Superficialidade",
            "challenges_2": "Tendência a criticar",
            "description": "Autoexpressão, inspiração, sociabilidade. Sua energia criativa é contagiante e atrai as pessoas.",
            "famous_0": "Jim Carrey",
            "famous_1": "Christina Aguilera",
            "famous_2": "John Travolta",
            "love": "Parceiro leve e divertido, mas precisa aprender profundidade nos relacionamentos.",
            "name": "Três",
            "strengths_0": "Criatividade",
            "strengths_1": "Otimismo",
            "strengths_2": "Eloquência",
            "strengths_3": "Artismo",
            "title": "Criador"
        },
        "33": {
            "career": "Cura, práticas espirituais, educação, caridade.",
            "challenges_0": "Burnout emocional",
            "challenges_1": "Autossacrifício",
            "challenges_2": "Perfeccionismo",
            "description": "Compaixão de ordem superior, magistério, amor sacrificial. Vocês curam o mundo com sua presença.",
            "famous_0": "Albert Einstein",
            "famous_1": "Francis Bacon",
            "famous_2": "Stephen King",
            "love": "Seu amor é ilimitado, mas não se esqueça de amar a si mesmo.",
            "name": "Número Mestre 33",
            "strengths_0": "Amor incondicional",
            "strengths_1": "Cura",
            "strengths_2": "Sabedoria",
            "strengths_3": "abnegação",
            "title": "Curandeiro"
        },
        "4": {
            "career": "Engenharia, construção, finanças, gerenciamento de projetos.",
            "challenges_0": "Rigidez",
            "challenges_1": "trabalholismo",
            "challenges_2": "Conservadorismo",
            "description": "Estabilidade, disciplina, trabalho árduo. Você cria uma base sólida para tudo o que empreende.",
            "famous_0": "Bill Gates",
            "famous_1": "Oprah Winfrey",
            "famous_2": "Elton John",
            "love": "Parceiro leal e confiável. Precisa aprender espontaneidade e romance.",
            "name": "Quatro",
            "strengths_0": "Confiabilidade",
            "strengths_1": "praticidade",
            "strengths_2": "Organização",
            "strengths_3": "Resistência",
            "title": "Construtor"
        },
        "5": {
            "career": "Viagens, jornalismo, vendas, startups, consultoria.",
            "challenges_0": "Inconstância",
            "challenges_1": "Impulsividade",
            "challenges_2": "medo de compromisso",
            "description": "Liberdade, aventura, mudanças. Você não pode ficar parado e está sempre em busca de novas experiências.",
            "famous_0": "Abraham Lincoln",
            "famous_1": "Angelina Jolie",
            "famous_2": "Mick Jagger",
            "love": "Precisa de liberdade nos relacionamentos. Um parceiro não deve ser uma gaiola.",
            "name": "Cinco",
            "strengths_0": "adaptabilidade",
            "strengths_1": "curiosidade",
            "strengths_2": "Carisma",
            "strengths_3": "Versatilidade",
            "title": "Buscador"
        },
        "6": {
            "career": "Medicina, educação, design, trabalho social, culinária.",
            "challenges_0": "Hipercontrole",
            "challenges_1": "abnegação",
            "challenges_2": "Perfeccionismo",
            "description": "Cuidado, responsabilidade, família. Você traz luz e calor para a vida dos entes queridos. A harmonia é o seu principal valor.",
            "famous_0": "Albert Einstein",
            "famous_1": "John Lennon",
            "famous_2": "Galileu Galilei",
            "love": "Perfeito pai de família, mas não se esqueça de si mesmo.",
            "name": "Seis",
            "strengths_0": "natureza cuidadosa",
            "strengths_1": "responsabilidade",
            "strengths_2": "Gosto estético",
            "strengths_3": "Lealdade",
            "title": "Guardião"
        },
        "7": {
            "career": "Ciência, pesquisa, TI, filosofia, psicologia.",
            "challenges_0": "Introversão",
            "challenges_1": "Ceticismo",
            "challenges_2": "Frieza emocional",
            "description": "Sabedoria, espiritualidade, mente analítica. Você busca um significado profundo em tudo e almeja o conhecimento.",
            "famous_0": "Nikola Tesla",
            "famous_1": "Princesa Diana",
            "famous_2": "Vladimir Putin",
            "love": "Precisa de um parceiro intelectual. Aprenda a abrir os sentimentos.",
            "name": "Sete",
            "strengths_0": "Mente analítica",
            "strengths_1": "Intuição",
            "strengths_2": "Profundidade",
            "strengths_3": "perfeccionismo",
            "title": "Pensador"
        },
        "8": {
            "career": "Negócios, finanças, imóveis, gestão, direito.",
            "challenges_0": "Materialismo",
            "challenges_1": "Dominação",
            "challenges_2": "Trabalholismo",
            "description": "Poder, sucesso, abundância material. Você sabe atrair recursos e gerenciar grandes projetos.",
            "famous_0": "Nelson Mandela",
            "famous_1": "Pablo Picasso",
            "famous_2": "Sandra Bullock",
            "love": "Parceiro de status. Mas não transforme o relacionamento em um negócio.",
            "name": "Oito",
            "strengths_0": "tino empresarial",
            "strengths_1": "autoridade",
            "strengths_2": "Pensamento estratégico",
            "strengths_3": "Resistência",
            "title": "Magnata"
        },
        "9": {
            "career": "Caridade, arte, medicina, práticas espirituais.",
            "challenges_0": "Idealismo",
            "challenges_1": "Desapontamento com as pessoas",
            "challenges_2": "Dificuldade com finais",
            "description": "Compaixão, sabedoria, conclusão. Você serve a um propósito superior e vê o mundo em grande escala.",
            "famous_0": "Mahatma Gandhi",
            "famous_1": "Madre Teresa",
            "famous_2": "Jimi Hendrix",
            "love": "O amor incondicional é o seu dom. Não tenha medo de deixar ir.",
            "name": "Nove",
            "strengths_0": "Sabedoria",
            "strengths_1": "Generosidade",
            "strengths_2": "Carisma",
            "strengths_3": "Visão ampla",
            "title": "Humanitário"
        }
    },
    "tr": {
        "1": {
            "career": "Girişimcilik, liderlik, yenilikçilik, serbest çalışma.",
            "challenges_0": "Bencillik",
            "challenges_1": "sabırsızlık",
            "challenges_2": "İnatçılık",
            "description": "Bağımsızlık, hırs, öncü. Siz liderlik etmek ve yeni yollar açmak için doğdunuz. Güçlü irade ve kararlılık sizin ana araçlarınızdır.",
            "famous_0": "Napolyon Bonapart",
            "famous_1": "Steve Jobs",
            "famous_2": "Martin Luther King",
            "love": "Bağımsızlığınıza saygı duyan bir partnere ihtiyacınız var. İkinci yarınızı bastırmaktan kaçının.",
            "name": "Bir",
            "strengths_0": "Kararlılık",
            "strengths_1": "inisiyatif",
            "strengths_2": "Bağımsızlık",
            "strengths_3": "Özgünlük",
            "title": "Lider"
        },
        "11": {
            "career": "Ruhsal rehberlik, sanat, psikoloji, icat.",
            "challenges_0": "Sinir gerginliği",
            "challenges_1": "Aşırı duyarlılık",
            "challenges_2": "İç çatışma",
            "description": "Yüksek düzey sezgi, ilham, ruhsal liderlik. Başkalarından gizleneni görür ve ışığı taşırsınız.",
            "famous_0": "Wolfgang Mozart",
            "famous_1": "Barack Obama",
            "famous_2": "Edgar Allan Poe",
            "love": "Derin ruhsal bağ her şeyden önemlidir. Ruhdaşınızı arayın.",
            "name": "Usta Sayı 11",
            "strengths_0": "Süper sezgi",
            "strengths_1": "Kitle ilhamı",
            "strengths_2": "Ruhsal derinlik",
            "strengths_3": "Karizma",
            "title": "Vizyoner"
        },
        "2": {
            "career": "Arabuluculuk, psikoloji, sanat, takım çalışması, İK.",
            "challenges_0": "Kararsızlık",
            "challenges_1": "Başkalarının görüşlerine bağımlılık",
            "challenges_2": "Utangaçlık",
            "description": "Uyum, iş birliği, sezgi. İnsanları ince bir düzeyde hissediyor ve her durumda dengeyi bulabiliyorsunuz.",
            "famous_0": "Barack Obama",
            "famous_1": "Madonna",
            "famous_2": "Ronald Reagan",
            "love": "Romantik, derin bir duygusal bağ arıyor. Partnerin içinde kaybolmaktan kaçının.",
            "name": "İki",
            "strengths_0": "Diplomasi",
            "strengths_1": "Hassasiyet",
            "strengths_2": "Sabır",
            "strengths_3": "barış yapma",
            "title": "diplomat"
        },
        "22": {
            "career": "Mimarlık, büyük iş, politika, uluslararası projeler.",
            "challenges_0": "mükemmeliyetçilik",
            "challenges_1": "Sorumluluğun baskısı",
            "challenges_2": "Kontrol sorunları",
            "description": "Büyük projeler, hayallerin gerçekleşmesi, pratik bilgelik. Sonsuzluk için inşa ediyorsunuz, vizyonu gerçeğe dönüştürerek.",
            "famous_0": "Paul McCartney",
            "famous_1": "Dalay Lama",
            "famous_2": "Richard Branson",
            "love": "Eşit bir ortağa ihtiyacınız var, hırslarınızı paylaşan.",
            "name": "Usta Sayı 22",
            "strengths_0": "Büyük ölçekli düşünme",
            "strengths_1": "Pratik uygulama",
            "strengths_2": "organizasyon yeteneği",
            "strengths_3": "dayanıklılık",
            "title": "mimar"
        },
        "3": {
            "career": "Sanat, medya, pazarlama, öğretim, eğlence.",
            "challenges_0": "Dağınık odak",
            "challenges_1": "yüzeysellik",
            "challenges_2": "Eleştirme eğilimi",
            "description": "Kendini ifade etme, ilham, sosyallik. Yaratıcı enerjiniz bulaşıcıdır ve insanları çeker.",
            "famous_0": "Jim Carrey",
            "famous_1": "Christina Aguilera",
            "famous_2": "John Travolta",
            "love": "Hafif ve neşeli bir partner, ancak ilişkilerde derinliği öğrenmesi gerekiyor.",
            "name": "üç",
            "strengths_0": "Yaratıcılık",
            "strengths_1": "İyimserlik",
            "strengths_2": "Belagat",
            "strengths_3": "sanatçılık",
            "title": "Yaratıcı"
        },
        "33": {
            "career": "Şifa, manevi uygulamalar, eğitim, hayır.",
            "challenges_0": "Duygusal tükenmişlik",
            "challenges_1": "Özveri",
            "challenges_2": "Mükemmeliyetçilik",
            "description": "Yüksek merhamet, öğretmenlik, fedakar sevgi. Varlığınla dünyayı iyileştiriyorsun.",
            "famous_0": "Albert Einstein",
            "famous_1": "Francis Bacon",
            "famous_2": "Stephen King",
            "love": "Sevginiz sınırsız, ama kendinizi sevmeyi unutmayın.",
            "name": "Üstat Sayı 33",
            "strengths_0": "Koşulsuz sevgi",
            "strengths_1": "şifacılık",
            "strengths_2": "Bilgelik",
            "strengths_3": "özveri",
            "title": "Şifacı"
        },
        "4": {
            "career": "Mühendislik, inşaat, finans, proje yönetimi.",
            "challenges_0": "rijitlik",
            "challenges_1": "işkoliklik",
            "challenges_2": "Muhafazakârlık",
            "description": "İstikrar, disiplin, çalışkanlık. Üstlendiğiniz her şey için sağlam bir temel oluşturuyorsunuz.",
            "famous_0": "Bill Gates",
            "famous_1": "Oprah Winfrey",
            "famous_2": "Elton John",
            "love": "Sadık ve güvenilir bir partner. Kendiliğindenlik ve romantizmi öğrenmesi gerekiyor.",
            "name": "dört",
            "strengths_0": "Güvenilirlik",
            "strengths_1": "Pratiklik",
            "strengths_2": "Organize olma",
            "strengths_3": "Dayanıklılık",
            "title": "İnşaatçı"
        },
        "5": {
            "career": "Seyahat, gazetecilik, satış, startuplar, danışmanlık.",
            "challenges_0": "Tutarsızlık",
            "challenges_1": "dürtüsellik",
            "challenges_2": "Taahhüt korkusu",
            "description": "Özgürlük, macera, değişim. Yerinde duramazsınız ve her zaman yeni deneyimlerin peşindesiniz.",
            "famous_0": "Abraham Lincoln",
            "famous_1": "Angelina Jolie",
            "famous_2": "Mick Jagger",
            "love": "İlişkilerde özgürlük gerekli. Partner bir kafes olmamalı.",
            "name": "beş",
            "strengths_0": "Uyarlanabilirlik",
            "strengths_1": "Merak",
            "strengths_2": "karizma",
            "strengths_3": "Çok yönlülük",
            "title": "Arayıcı"
        },
        "6": {
            "career": "Tıp, eğitim, tasarım, sosyal hizmet, mutfak sanatları.",
            "challenges_0": "aşırı kontrol",
            "challenges_1": "özveri",
            "challenges_2": "Mükemmeliyetçilik",
            "description": "Bakım, sorumluluk, aile. Sevdiklerinizin hayatına ışık ve sıcaklık getiriyorsunuz. Uyum sizin temel değerinizdir.",
            "famous_0": "Albert Einstein",
            "famous_1": "John Lennon",
            "famous_2": "Galileo Galilei",
            "love": "İdeal bir aile babası, ama kendini unutmamalısın.",
            "name": "Altı",
            "strengths_0": "Şefkatlilik",
            "strengths_1": "Sorumluluk",
            "strengths_2": "estetik zevk",
            "strengths_3": "Sadakat",
            "title": "Koruyucu"
        },
        "7": {
            "career": "Bilim, araştırma, BT, felsefe, psikoloji.",
            "challenges_0": "İçe dönüklük",
            "challenges_1": "Kuşkuculuk",
            "challenges_2": "Duygusal soğukluk",
            "description": "Bilgelik, maneviyat, analitik zihin. Her şeyde derin anlam arar ve bilgiye ulaşmaya çabalarsınız.",
            "famous_0": "Nikola Tesla",
            "famous_1": "Prenses Diana",
            "famous_2": "Vladimir Putin",
            "love": "Entelektüel bir partnere ihtiyacım var. Duyguları açmayı öğrenin.",
            "name": "Yedi",
            "strengths_0": "Analitik zihin",
            "strengths_1": "Sezgi",
            "strengths_2": "Derinlik",
            "strengths_3": "mükemmeliyetçilik",
            "title": "Düşünür"
        },
        "8": {
            "career": "İş, finans, gayrimenkul, yönetim, hukuk.",
            "challenges_0": "Materyalizm",
            "challenges_1": "Hakimiyet",
            "challenges_2": "işkoliklik",
            "description": "Güç, başarı, maddi bolluk. Kaynakları çekmeyi ve büyük projeleri yönetmeyi biliyorsunuz.",
            "famous_0": "Nelson Mandela",
            "famous_1": "Pablo Picasso",
            "famous_2": "Sandra Bullock",
            "love": "Statü odaklı partner. Ama ilişkileri anlaşmaya dönüştürmeyin.",
            "name": "sekiz",
            "strengths_0": "İş kavrayışı",
            "strengths_1": "Otorite",
            "strengths_2": "Stratejik düşünme",
            "strengths_3": "Dayanıklılık",
            "title": "Magnat"
        },
        "9": {
            "career": "Hayırseverlik, sanat, tıp, manevi uygulamalar.",
            "challenges_0": "İdealizm",
            "challenges_1": "İnsanlarda hayal kırıklığı",
            "challenges_2": "Sonlarla ilgili zorluk",
            "description": "Merhamet, bilgelik, tamamlama. Daha yüksek bir amaca hizmet ediyorsunuz ve dünyayı büyük ölçekte görüyorsunuz.",
            "famous_0": "Mahatma Gandhi",
            "famous_1": "Rahibe Teresa",
            "famous_2": "Jimi Hendrix",
            "love": "Koşulsuz sevgi sizin hediyeniz. Bırakmaktan korkmayın.",
            "name": "Dokuz",
            "strengths_0": "Bilgelik",
            "strengths_1": "cömertlik",
            "strengths_2": "Karizma",
            "strengths_3": "Geniş ufuk",
            "title": "hümanist"
        }
    },
    "uk": {
        "1": {
            "career": "Підприємництво, керівництво, інновації, фріланс.",
            "challenges_0": "егоїзм",
            "challenges_1": "Нетерпіння",
            "challenges_2": "упертість",
            "description": "Незалежність, амбіції, першопроходець. Ви народжені вести за собою і прокладати нові шляхи. Сильна воля і рішучість — ваші головні інструменти.",
            "famous_0": "Наполеон Бонапарт",
            "famous_1": "Стів Джобс",
            "famous_2": "Мартін Лютер Кінг",
            "love": "Потрібен партнер, який поважає вашу незалежність. Уникайте пригнічення другої половинки.",
            "name": "Одиниця",
            "strengths_0": "Рішучість",
            "strengths_1": "ініціативність",
            "strengths_2": "Самостійність",
            "strengths_3": "оригінальність",
            "title": "Лідер"
        },
        "11": {
            "career": "Духовне наставництво, мистецтво, психологія, винахідництво.",
            "challenges_0": "Нервове напруження",
            "challenges_1": "Гіперчутливість",
            "challenges_2": "Внутрішній конфлікт",
            "description": "Інтуїція вищого порядку, натхнення, духовне лідерство. Ви бачите те, що приховано від інших, і несете світло.",
            "famous_0": "Вольфганг Моцарт",
            "famous_1": "Барак Обама",
            "famous_2": "Едгар Аллан По",
            "love": "Глибокий духовний зв'язок найважливіший. Шукайте споріднену душу.",
            "name": "Мастер-число 11",
            "strengths_0": "Надінтуїція",
            "strengths_1": "Натхнення мас",
            "strengths_2": "Духовна глибина",
            "strengths_3": "Харизма",
            "title": "Провидець"
        },
        "2": {
            "career": "Медіація, психологія, мистецтво, командна робота, HR.",
            "challenges_0": "Нерішучість",
            "challenges_1": "Залежність від думки інших",
            "challenges_2": "сором'язливість",
            "description": "Гармонія, співробітництво, інтуїція. Ви відчуваєте людей на тонкому рівні і вмієте знаходити баланс у будь-якій ситуації.",
            "famous_0": "Барак Обама",
            "famous_1": "Мадонна",
            "famous_2": "Рональд Рейган",
            "love": "Романтик, шукає глибокий емоційний зв'язок. Уникайте розчинення в партнері.",
            "name": "Двійка",
            "strengths_0": "дипломатичність",
            "strengths_1": "Чутливість",
            "strengths_2": "Терпіння",
            "strengths_3": "миротворчість",
            "title": "Диплома"
        },
        "22": {
            "career": "Архітектура, великий бізнес, політика, міжнародні проекти.",
            "challenges_0": "Перфекціонізм",
            "challenges_1": "Тиск відповідальності",
            "challenges_2": "Контроль",
            "description": "Масштабні проєкти, матеріалізація мрій, практична мудрість. Ви будуєте для ві",
            "famous_0": "Пол Маккартні",
            "famous_1": "Далай-лама",
            "famous_2": "Річард Бренсон",
            "love": "Потрібен рівний партнер, який поділяє ваші амбіції.",
            "name": "Мастер-число 22",
            "strengths_0": "Масштабне мислення",
            "strengths_1": "Практична реалізація",
            "strengths_2": "Організаторський талант",
            "strengths_3": "витримка",
            "title": "Зодчий"
        },
        "3": {
            "career": "Мистецтво, медіа, маркетинг, викладання, розваги.",
            "challenges_0": "розсіяність",
            "challenges_1": "Поверхневість",
            "challenges_2": "Схильність до критики",
            "description": "Самовираження, натхнення, товариськість. Ваша творча енергія заразлива і притягує людей.",
            "famous_0": "Джим Керрі",
            "famous_1": "Крістіна Агілера",
            "famous_2": "Джон Траволта",
            "love": "Легкий і веселий партнер, але потрібно вчитися глибині відносин.",
            "name": "Трійка",
            "strengths_0": "Креативність",
            "strengths_1": "Оптимізм",
            "strengths_2": "красномовство",
            "strengths_3": "Артистизм",
            "title": "Творець"
        },
        "33": {
            "career": "Цілительство, духовні практики, освіта, благодійність.",
            "challenges_0": "Емоційне вигорання",
            "challenges_1": "самопожертва",
            "challenges_2": "Перфекціонізм",
            "description": "Співчуття вищого порядку, учительство, жертовна любов. Ви зцілюєте світ своєю присутністю.",
            "famous_0": "Альберт Ейнштейн",
            "famous_1": "Френсіс Бекон",
            "famous_2": "Стівен Кінг",
            "love": "Ваша любов безмежна, але не забувайте любити себе.",
            "name": "Майстер-число 33",
            "strengths_0": "Безумовна любов",
            "strengths_1": "Цілительство",
            "strengths_2": "Мудрість",
            "strengths_3": "самовідданість",
            "title": "Цілитель"
        },
        "4": {
            "career": "Інженерія, будівництво, фінанси, управління проєктами.",
            "challenges_0": "ригідність",
            "challenges_1": "Трудоголізм",
            "challenges_2": "Консерватизм",
            "description": "Стабільність, дисципліна, працьовитість. Ви створюєте міцний фундамент для всього, за що беретеся.",
            "famous_0": "Білл Гейтс",
            "famous_1": "Опра Вінфрі",
            "famous_2": "Елтон Джон",
            "love": "Вірний і надійний партнер. Потрібно вчи",
            "name": "четвірка",
            "strengths_0": "Надійність",
            "strengths_1": "Практичність",
            "strengths_2": "Організованість",
            "strengths_3": "витривалість",
            "title": "Будівельник"
        },
        "5": {
            "career": "Подорожі, журналістика, продажі, стартапи, консалтинг.",
            "challenges_0": "Непостійність",
            "challenges_1": "Імпульсивність",
            "challenges_2": "Страх зобов'язань",
            "description": "Свобода, пригоди, зміни. Ви не можете стояти на місці й завжди в пошуку нового досвіду.",
            "famous_0": "Авраам Лінкольн",
            "famous_1": "Анджеліна Джолі",
            "famous_2": "Мік Джаггер",
            "love": "Потрібна свобода у відносинах. Партнер не повинен бути кліткою.",
            "name": "П’ятірка",
            "strengths_0": "Адаптивність",
            "strengths_1": "Допитливість",
            "strengths_2": "Харизма",
            "strengths_3": "Багатогранність",
            "title": "Шукач"
        },
        "6": {
            "career": "Медицина, освіта, дизайн, соціальна робота, кулінарія.",
            "challenges_0": "гіперконтроль",
            "challenges_1": "Жертовність",
            "challenges_2": "Перфекціонізм",
            "description": "Турбота, відповідальність, сім'я. Ви несете світло і тепло в життя близьких. Гармонія — ваша головна цінність.",
            "famous_0": "Альберт Ейнштейн",
            "famous_1": "Джон Леннон",
            "famous_2": "Галілео Галілей",
            "love": "Ідеальний сім'янин, але треба не забувати про себе.",
            "name": "шістка",
            "strengths_0": "Турботливість",
            "strengths_1": "відповідальність",
            "strengths_2": "Естетичний смак",
            "strengths_3": "Вірність",
            "title": "Хранитель"
        },
        "7": {
            "career": "Наука, дослідження, IT, філософія, психологія.",
            "challenges_0": "Замкненість",
            "challenges_1": "Скептицизм",
            "challenges_2": "Емоційна холодність",
            "description": "Мудрість, духовність, аналітичний розум. Ви шукаєте глибинний сенс у всьому і прагнете до знань.",
            "famous_0": "Нікола Тесла",
            "famous_1": "Принцеса Діана",
            "famous_2": "Володимир Путін",
            "love": "Потрібен інтелектуальний партнер. Вчіться відкривати почуття.",
            "name": "Сімка",
            "strengths_0": "Аналітичний розум",
            "strengths_1": "Інтуїція",
            "strengths_2": "Глибина",
            "strengths_3": "Перфекціонізм",
            "title": "Мислитель"
        },
        "8": {
            "career": "Бізнес, фінанси, нерухомість, управління, юриспруденція.",
            "challenges_0": "Матеріалізм",
            "challenges_1": "владність",
            "challenges_2": "Трудоголізм",
            "description": "Влада, успіх, матеріальна достаток. Ви вмієте притягувати ресурси та керувати великими проєктами.",
            "famous_0": "Нельсон Мандела",
            "famous_1": "Пабло Пікассо",
            "famous_2": "Сандра Буллок",
            "love": "Статусний партнер. Але не перетворюйте стосунки на угоду.",
            "name": "Вісімка",
            "strengths_0": "Ділова хватка",
            "strengths_1": "Авторитетність",
            "strengths_2": "Стратегічне мислення",
            "strengths_3": "Витривалість",
            "title": "Магнат"
        },
        "9": {
            "career": "Благодійність, мистецтво, медицина, духовні практики.",
            "challenges_0": "Ідеалізм",
            "challenges_1": "Розчарування в людях",
            "challenges_2": "Складність із завершеннями",
            "description": "Співчуття, мудрість, завершення. Ви служите вищій",
            "famous_0": "Махатма Ґанді",
            "famous_1": "Мати Тереза",
            "famous_2": "Джимі Гендрікс",
            "love": "Безумовна любов — ваш дар. Не бійтеся відпускати.",
            "name": "дев'ятка",
            "strengths_0": "Мудрість",
            "strengths_1": "Щедрість",
            "strengths_2": "Харизма",
            "strengths_3": "Широкий кругозір",
            "title": "Гуманіст"
        }
    }
}
KARMIC_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "13": {
            "description": "Deuda kármica 13 — pereza en vidas pasadas. Hay que aprender a trabajar con diligencia y llevar las cosas hasta el final."
        },
        "14": {
            "description": "Deuda kármica 14 — abuso de la libertad. Lección de moderación y responsabilidad por tus acciones."
        },
        "16": {
            "description": "Deuda kármica 16 — destrucción del ego. Lección de humildad, crecimiento espiritual a través de pérdidas y reconstrucción."
        },
        "19": {
            "description": "Deuda kármica 19 — abuso de poder. Lección de independencia sin reprimir a los demás."
        }
    },
    "pt": {
        "13": {
            "description": "Dívida cármica 13 — preguiça em vidas passadas. É preciso aprender a trabalhar com afinco e terminar o que começa."
        },
        "14": {
            "description": "Dívida cármica 14 — abuso da liberdade. Lição de moderação e responsabilidade por suas ações."
        },
        "16": {
            "description": "Dívida cármica 16 — destruição do ego. Lição de humildade, crescimento espiritual através de perdas e reconstrução."
        },
        "19": {
            "description": "Dívida cármica 19 — abuso de poder. Lição de independência sem oprimir os outros."
        }
    },
    "tr": {
        "13": {
            "description": "Karmik borç 13 — geçmiş yaşamlardaki tembellik. Sıkı çalışmayı ve başladığın işleri bitirmeyi öğrenmelisin."
        },
        "14": {
            "description": "Karmik borç 14 — özgürlüğün kötüye kullanılması. Ilımlılık ve eylemlerinin sorumluluğunu üstlenme dersi."
        },
        "16": {
            "description": "Karmik borç 16 — egonun yıkımı. Alçakgönüllülük dersi, kayıplar ve yeniden yapılanma yoluyla ruhsal büyüme."
        },
        "19": {
            "description": "Karmik borç 19 — gücü kötüye kullanma. Başkalarını bastırmadan bağımsızlık dersi."
        }
    },
    "uk": {
        "13": {
            "description": "Кармічний борг 13 — лінь у минулих життях. Потрібно вчитися працювати старанно та доводити справи до кінця."
        },
        "14": {
            "description": "Кармічний борг 14 — зловживання свободою. Урок помірності та відповідальності за свої дії."
        },
        "16": {
            "description": "Кармічний борг 16 — руйнування его. Урок смирення, духовного зростання через втрати та перебудову."
        },
        "19": {
            "description": "Кармічний борг 19 — зловживання владою. Урок самостійності без пригнічення інших."
        }
    }
}
CELL_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "1": {
            "name": "Carácter y fuerza de voluntad"
        },
        "2": {
            "name": "Energía y biocampo"
        },
        "3": {
            "name": "Cognición e interés en las ciencias"
        },
        "4": {
            "name": "Salud y estado físico"
        },
        "5": {
            "name": "Lógica e intuición"
        },
        "6": {
            "name": "Laboriosidad y responsabilidad"
        },
        "7": {
            "name": "Suerte y fortuna"
        },
        "8": {
            "name": "Sentido del deber y responsabilidad"
        },
        "9": {
            "name": "Memoria e inteligencia"
        }
    },
    "pt": {
        "1": {
            "name": "Caráter e força de vontade"
        },
        "2": {
            "name": "Energia e biocampo"
        },
        "3": {
            "name": "Cognição e interesse pelas ciências"
        },
        "4": {
            "name": "Saúde e condição física"
        },
        "5": {
            "name": "Lógica e intuição"
        },
        "6": {
            "name": "Diligência e responsabilidade"
        },
        "7": {
            "name": "Sorte e fortuna"
        },
        "8": {
            "name": "Senso de dever e confiabilidade"
        },
        "9": {
            "name": "Memória e intelecto"
        }
    },
    "tr": {
        "1": {
            "name": "Karakter ve irade gücü"
        },
        "2": {
            "name": "Enerji ve biyoalan"
        },
        "3": {
            "name": "Bilim ve bilime ilgi"
        },
        "4": {
            "name": "Sağlık ve fiziksel durum"
        },
        "5": {
            "name": "Mantık ve sezgi"
        },
        "6": {
            "name": "Çalışkanlık ve sorumluluk"
        },
        "7": {
            "name": "Şans ve talih"
        },
        "8": {
            "name": "Görev duygusu ve güvenilirlik"
        },
        "9": {
            "name": "Hafıza ve zekâ"
        }
    },
    "uk": {
        "1": {
            "name": "Характер і сила волі"
        },
        "2": {
            "name": "Енергетика і біополе"
        },
        "3": {
            "name": "Пізнання та інтерес до наук"
        },
        "4": {
            "name": "Здоров'я та фізичний стан"
        },
        "5": {
            "name": "Логіка і інтуїція"
        },
        "6": {
            "name": "Працьовитість і відповідальність"
        },
        "7": {
            "name": "Везіння і удача"
        },
        "8": {
            "name": "Почуття обов'язку та надійність"
        },
        "9": {
            "name": "Пам'ять і інтелект"
        }
    }
}
CELL_LEVELS_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "0": {
            "description": "Ausente — calidad no desarrollada, necesita trabajo"
        },
        "1": {
            "description": "Débil — hay potencial básico, necesita desarrollo"
        },
        "2": {
            "description": "Promedio — nivel normal, estable"
        },
        "3": {
            "description": "Fuerte — claramente expresado, su apoyo"
        },
        "4": {
            "description": "Muy fuerte — domina, puede ser excesivo"
        }
    },
    "pt": {
        "0": {
            "description": "Ausente — qualidade não desenvolvida, precisa de trabalho"
        },
        "1": {
            "description": "Fraco — potencial básico, precisa ser desenvolvido"
        },
        "2": {
            "description": "Médio — nível normal, estável"
        },
        "3": {
            "description": "Forte — claramente expresso, seu apoio"
        },
        "4": {
            "description": "Muito forte — domina, pode ser excessivo"
        }
    },
    "tr": {
        "0": {
            "description": "Yok — kalite gelişmemiş, çalışma gerektiriyor"
        },
        "1": {
            "description": "Zayıf — temel potansiyel, geliştirilmesi gerek"
        },
        "2": {
            "description": "Ortalama — normal seviye, stabil"
        },
        "3": {
            "description": "Güçlü — belirgin bir şekilde ifade edilmiş, sizin dayanağınız"
        },
        "4": {
            "description": "Çok güçlü — baskın, aşırı olabilir"
        }
    },
    "uk": {
        "0": {
            "description": "Відсутня — якість не розвинена, потребує роботи"
        },
        "1": {
            "description": "Слабке — є задатки, потрібно розвивати"
        },
        "2": {
            "description": "Середнє — нормальний рівень, стабільно"
        },
        "3": {
            "description": "Сильне — яскраво виражено, ваша опора"
        },
        "4": {
            "description": "Дуже сильне — домінує, може бути надмірним"
        }
    }
}
LINE_DEFS_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "0": {
            "desc": "Cuantos más dígitos, mayor es la autoestima y más fuerte la determinación.",
            "title": "Autoestima y determinación"
        },
        "1": {
            "desc": "Muestra deseo de familia, estabilidad y comodidad.",
            "title": "Estabilidad familiar"
        },
        "2": {
            "desc": "Conexión con el yo superior, talento, intuición, prácticas espirituales.",
            "title": "Desarrollo espiritual"
        },
        "3": {
            "desc": "Capacidad de realizarse a uno mismo y alcanzar metas.",
            "title": "potencial personal"
        },
        "4": {
            "desc": "Sociabilidad, capacidad para interactuar con las personas.",
            "title": "Actividad social"
        },
        "5": {
            "desc": "Capacidad de ganar y multiplicar bienes materiales.",
            "title": "Potencial financiero"
        },
        "6": {
            "desc": "Núcleo interno, autoconocimiento, confianza profunda.",
            "title": "Diagonal espiritual (autoestima)"
        },
        "7": {
            "desc": "Intuición natural, suerte, habilidad para estar en el lugar correcto.",
            "title": "Diagonal de la intuición y la suerte"
        }
    },
    "pt": {
        "0": {
            "desc": "Quanto mais dígitos, maior a autoestima e mais forte a determinação.",
            "title": "autoestima e determinação"
        },
        "1": {
            "desc": "Mostra desejo por família, estabilidade e conforto.",
            "title": "Estabilidade da família"
        },
        "2": {
            "desc": "Conexão com o eu superior, talento, intuição, práticas espirituais.",
            "title": "Desenvolvimento espiritual"
        },
        "3": {
            "desc": "Capacidade de realizar a si mesmo e alcançar objetivos.",
            "title": "potencial pessoal"
        },
        "4": {
            "desc": "Sociabilidade, habilidade de interagir com pessoas.",
            "title": "Atividade social"
        },
        "5": {
            "desc": "Capacidade de ganhar e multiplicar bens materiais.",
            "title": "Potencial financeiro"
        },
        "6": {
            "desc": "Núcleo interno, autoconhecimento, confiança profunda.",
            "title": "Diagonal espiritual (autoestima)"
        },
        "7": {
            "desc": "Intuição natural, sorte, habilidade de estar no lugar certo na hora certa.",
            "title": "Diagonal da intuição e da sorte"
        }
    },
    "tr": {
        "0": {
            "desc": "Ne kadar çok rakam varsa, öz saygı o kadar yüksek ve kararlılık o kadar güçlüdür.",
            "title": "Öz saygı ve kararlılık"
        },
        "1": {
            "desc": "Aileye, istikrara ve rahata duyulan arzuyu gösterir.",
            "title": "Aile istikrarı"
        },
        "2": {
            "desc": "Üst benlikle bağlantı, yetenek, sezgi, ruhsal uygulamalar.",
            "title": "Ruhsal gelişim"
        },
        "3": {
            "desc": "Kendini gerçekleştirme ve hedeflere ulaşma yeteneği",
            "title": "Kişisel potansiyel"
        },
        "4": {
            "desc": "Sosyallik, insanlarla etkileşim kurabilme yeteneği.",
            "title": "Sosyal aktivite"
        },
        "5": {
            "desc": "Maddi varlıkları kazanma ve çoğaltma yeteneği.",
            "title": "Finansal potansiyel"
        },
        "6": {
            "desc": "İç çekirdek, kendini tanıma, derin güven.",
            "title": "Ruhsal diyagonal (öz saygı)"
        },
        "7": {
            "desc": "Doğal sezgi, şans, doğru zamanda doğru yerde olma becerisi.",
            "title": "Sezgi ve şans diyagonali"
        }
    },
    "uk": {
        "0": {
            "desc": "Чим більше цифр — тим вища самооцін",
            "title": "Самооцінка і цілеспрямованість"
        },
        "1": {
            "desc": "Показує прагнення до сім'ї, стабільності та комфорту.",
            "title": "Стабільність сім'ї"
        },
        "2": {
            "desc": "Зв'язок з вищим, талант, інтуїція, духовні практи",
            "title": "Духовний розвиток"
        },
        "3": {
            "desc": "Здатність реалізувати себе і досягти цілей.",
            "title": "Особистісний потенціал"
        },
        "4": {
            "desc": "Товариськість, вміння взаємодіяти з людьми.",
            "title": "Соціальна активність"
        },
        "5": {
            "desc": "Здатність заробляти та примножувати матеріальні блага.",
            "title": "Фінансовий потенціал"
        },
        "6": {
            "desc": "Внутрішній стрижень, самопізнання, глибинна впевненість.",
            "title": "Духовна діагональ (самооцінка)"
        },
        "7": {
            "desc": "Природна інтуїція, везіння, вміння опинитися в потрібному місці.",
            "title": "Діагональ інтуїції та удачі"
        }
    }
}
ANGEL_NUMBERS_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "00:00": {
            "meaning": "Comienzo de un nuevo ciclo. El universo reinicia el contador — pide un deseo y empieza de cero."
        },
        "01:01": {
            "meaning": "Tus pensamientos se materializan. Cuida lo que piensas — se convertirá en realidad."
        },
        "02:02": {
            "meaning": "Confíen en el proceso. La asociación y la cooperación traerán resultados."
        },
        "03:03": {
            "meaning": "Los maestros ascendidos están cerca. La energía creativa está en su punto máximo — actúen."
        },
        "04:04": {
            "meaning": "Los ángeles los protegen. El fundamento de su vida se fortalece."
        },
        "05:05": {
            "meaning": "Se avecinan cambios importantes. Acéptalos — son para mejor."
        },
        "06:06": {
            "meaning": "Presta atención a la familia y al hogar. La armonía en las relaciones cercanas importa más que la carrera."
        },
        "07:07": {
            "meaning": "Estás en el camino correcto del desarrollo espiritual. Continúa meditando y estudiándote a ti mismo."
        },
        "08:08": {
            "meaning": "La abundancia financiera se acerca. Usted merece prosperidad."
        },
        "09:09": {
            "meaning": "Un ciclo termina. Suelta lo viejo — lo nuevo ya está en el umbral."
        },
        "10:10": {
            "meaning": "Las fuerzas superiores confirman tu elección. Confía en tu intuición."
        },
        "111": {
            "meaning": "Poderoso flujo de energía. Sus pensamientos toman forma instantáneamente — controlenlos."
        },
        "1111": {
            "meaning": "El portal cósmico está abierto. Todo lo que pienses se materializará. Pide tu deseo más profundo."
        },
        "11:11": {
            "meaning": "El portal de oportunidades está abierto. Sus pensamientos se materializan instantáneamente — piensen en positivo."
        },
        "12:12": {
            "meaning": "El optimismo dará frutos. Cree en lo mejor: el universo está de tu lado."
        },
        "13:13": {
            "meaning": "La transformación es inevitable. No teman a los cambios: traen renovación."
        },
        "14:14": {
            "meaning": "Los ángeles ayudan a mantener el equilibrio. La moderación es la clave del éxito."
        },
        "15:15": {
            "meaning": "Cambios en la vida personal. El amor y las relaciones alcanzan un nuevo nivel."
        },
        "16:16": {
            "meaning": "Dejen ir las ilusiones. La verdad los liberará de falsos apegos."
        },
        "17:17": {
            "meaning": "Estás al borde de la suerte. Tus esfuerzos pronto serán recompensados."
        },
        "18:18": {
            "meaning": "El ciclo financiero termina positivamente. Espere ganancias."
        },
        "19:19": {
            "meaning": "Termina lo que empezaste. Es hora de cosechar los frutos de tu trabajo."
        },
        "20:20": {
            "meaning": "El apoyo divino se está fortaleciendo. La fe y la paciencia te llevarán a tu objetivo."
        },
        "21:21": {
            "meaning": "Manténganse positivos. Su optimismo atrae a las personas adecuadas."
        },
        "222": {
            "meaning": "Todo va según lo planeado. No pierdan la fe: el resultado ya está cerca."
        },
        "2222": {
            "meaning": "Maestro constructor. Su fundamento es sólido — construya su sueño sin miedo."
        },
        "22:22": {
            "meaning": "Vibración maestra. Tus sueños están tomando forma — no te detengas."
        },
        "23:23": {
            "meaning": "Maestros ascendidos te están ayudando. Confía en tus talentos y actúa."
        },
        "333": {
            "meaning": "Los maestros ascendidos te rodean de amor. Libera tus habilidades creativas."
        },
        "444": {
            "meaning": "Miles de ángeles están cerca. Están completamente a salvo — continúen su camino."
        },
        "555": {
            "meaning": "Cambios de gran escala en el horizonte. Estén preparados — la vida está cambiando de rumbo."
        },
        "666": {
            "meaning": "Restablece el equilibrio en el mundo material. Lo espiritual es más importante que lo material."
        },
        "777": {
            "meaning": "¡Suerte divina! Estás completamente alineado con el flujo universal."
        },
        "888": {
            "meaning": "La abundancia financiera fluye a raudales. Ha comenzado un ciclo de prosperidad."
        },
        "999": {
            "meaning": "Gran finalización. Un capítulo se cierra — uno nuevo ya se está escribiendo."
        }
    },
    "pt": {
        "00:00": {
            "meaning": "Início de um novo ciclo. O universo zera o contador — faça um pedido e comece do zero."
        },
        "01:01": {
            "meaning": "Seus pensamentos estão se materializando. Cuidado com o que você pensa — isso se tornará realidade."
        },
        "02:02": {
            "meaning": "Confie no processo. Parceria e cooperação trarão resultados."
        },
        "03:03": {
            "meaning": "Mestres ascensionados estão por perto. A energia criativa está no auge — aja."
        },
        "04:04": {
            "meaning": "Anjos estão protegendo você. A fundação da sua vida está sendo fortalecida."
        },
        "05:05": {
            "meaning": "Mudanças importantes estão chegando. Aceite-as — elas são para melhor."
        },
        "06:06": {
            "meaning": "Dê atenção à família e ao lar. A harmonia nos relacionamentos próximos é mais importante que a carreira."
        },
        "07:07": {
            "meaning": "Você está no caminho certo do desenvolvimento espiritual. Continue meditando e estudando a si mesmo."
        },
        "08:08": {
            "meaning": "A abundância financeira está se aproximando. Você merece prosperidade."
        },
        "09:09": {
            "meaning": "O ciclo está se encerrando. Deixe o velho ir — o novo já está à porta."
        },
        "10:10": {
            "meaning": "Forças superiores confirmam sua escolha. Confie na sua intuição."
        },
        "111": {
            "meaning": "Fluxo poderoso de energia. Seus pensamentos instantaneamente tomam forma — controle-os."
        },
        "1111": {
            "meaning": "Portal cósmico está aberto. Tudo o que você pensa se manifestará. Faça o seu desejo mais profundo."
        },
        "11:11": {
            "meaning": "Portal de oportunidades está aberto. Seus pensamentos se materializam instantaneamente — pense positivo."
        },
        "12:12": {
            "meaning": "O otimismo dará frutos. Acredite no melhor — o universo está ao seu lado."
        },
        "13:13": {
            "meaning": "A transformação é inevitável. Não tenha medo das mudanças — elas trazem renovação."
        },
        "14:14": {
            "meaning": "Anjos ajudam a manter o equilíbrio. Moderação é a chave para o sucesso."
        },
        "15:15": {
            "meaning": "Mudanças na vida pessoal. Amor e relacionamentos atingem um novo nível."
        },
        "16:16": {
            "meaning": "Abandone as ilusões. A verdade libertará você de falsos apegos."
        },
        "17:17": {
            "meaning": "Você está no limiar da sorte. Seus esforços serão recompensados em breve."
        },
        "18:18": {
            "meaning": "O ciclo financeiro está terminando positivamente. Espere lucro."
        },
        "19:19": {
            "meaning": "Termine o que começou. Hora de colher os frutos do seu trabalho."
        },
        "20:20": {
            "meaning": "O apoio divino está se fortalecendo. Fé e paciência levarão ao seu objetivo."
        },
        "21:21": {
            "meaning": "Mantenham-se positivos. O seu otimismo atrai as pessoas certas."
        },
        "222": {
            "meaning": "Tudo está indo conforme o plano. Não percam a fé — o resultado está próximo."
        },
        "2222": {
            "meaning": "Mestre-construtor. Sua fundação é sólida — construa o seu sonho sem medo."
        },
        "22:22": {
            "meaning": "Vibração mestra. Seus sonhos estão tomando forma — não pare."
        },
        "23:23": {
            "meaning": "Mestres ascensionados estão ajudando você. Confie em seus talentos e aja."
        },
        "333": {
            "meaning": "Mestres ascensionados cercam"
        },
        "444": {
            "meaning": "Milhares de anjos estão por perto. Vocês estão completamente seguros — continuem seu caminho."
        },
        "555": {
            "meaning": "Mudanças significativas no horizonte. Esteja preparado — a vida está mudando de rumo."
        },
        "666": {
            "meaning": "Restabeleça o equilíbrio no mundo material. O espiritual é mais importante que o material."
        },
        "777": {
            "meaning": "Sorte divina! Você está totalmente alinhado com o fluxo universal."
        },
        "888": {
            "meaning": "A abundância financeira está fluindo. Um ciclo de prosperidade começou."
        },
        "999": {
            "meaning": "Grande conclusão. Um capítulo está se fechando — um novo já está sendo escrito."
        }
    },
    "tr": {
        "00:00": {
            "meaning": "Yeni bir döngünün başlangıcı. Evren sayacı sıfırlıyor — bir dilek tutun ve temiz bir sayfayla başlayın."
        },
        "01:01": {
            "meaning": "Düşünceleriniz somutlaşıyor. Ne düşündüğünüze dikkat edin — bu gerçek olacak."
        },
        "02:02": {
            "meaning": "Sürece güvenin. Ortaklık ve işbirliği sonuç get"
        },
        "03:03": {
            "meaning": "Yükselmiş üstatlar yakında. Yaratıcı enerji zirvede — harekete geçin."
        },
        "04:04": {
            "meaning": "Melekler sizi koruyor. Hayatınızın temeli güçlendiriliyor."
        },
        "05:05": {
            "meaning": "Önemli değişiklikler geliyor. Onları kabul edin — daha iyisi için."
        },
        "06:06": {
            "meaning": "Ailenize ve evinize dikkat edin. Yakın ilişkilerdeki uyum, kariyerden daha önemlidir."
        },
        "07:07": {
            "meaning": "Doğru ruhsal gelişim yolundasınız. Meditasyon yapmaya ve kendinizi incelemeye devam edin."
        },
        "08:08": {
            "meaning": "Finansal bolluk yaklaşıyor. Refahı hak ediyorsunuz"
        },
        "09:09": {
            "meaning": "Bir döngü sona eriyor. Eskiyi bırakın — yeni çoktan kapıda."
        },
        "10:10": {
            "meaning": "Yüksek güçler seçiminizi onaylıyor. Sezgilerinize güvenin."
        },
        "111": {
            "meaning": "Güçlü enerji akışı. Düşünceleriniz anında şekil alıyor — onları kontrol edin."
        },
        "1111": {
            "meaning": "Kozmik portal açık. Düşündüğünüz her şey gerçekleşecek. En gizli dileğinizi dileyin."
        },
        "11:11": {
            "meaning": "Fırsatlar portalı açık. Düşünceleriniz anında somutlaşıyor — iyi şeyler düşünün."
        },
        "12:12": {
            "meaning": "İyimserlik meyve verecek. En iyiye inanın — evren sizin tarafınızda."
        },
        "13:13": {
            "meaning": "Dönüşüm kaçınılmazdır. Değişimlerden korkmayın — onlar yenilenme getirir."
        },
        "14:14": {
            "meaning": "Melekler dengeyi korumaya yardımcı olur. Ölçülülük başarının anahtarıdır."
        },
        "15:15": {
            "meaning": "Kişisel hayatta değişiklikler. Aşk ve ilişkiler yeni bir seviyeye ulaşıyor."
        },
        "16:16": {
            "meaning": "Bırakın illüzyonları. Gerçek sizi sahte bağlılıklardan kurtaracak."
        },
        "17:17": {
            "meaning": "Şansın eşiğindesiniz. Çabalarınız yakında ödüllendirilecek."
        },
        "18:18": {
            "meaning": "Finansal döngü olumlu bir şekilde sona eriyor. Kâr bekleyin."
        },
        "19:19": {
            "meaning": "Başladığını bitir. Emeğinin meyvesini toplama zamanı."
        },
        "20:20": {
            "meaning": "İlahi destek güçleniyor"
        },
        "21:21": {
            "meaning": "Pozitif kalın. İyimserliğiniz doğru insanları çeker."
        },
        "222": {
            "meaning": "Her şey plana göre gidiyor. İnancınızı kaybetmeyin — sonuç çok yakında."
        },
        "2222": {
            "meaning": "Usta inşaatçı. Temeliniz sağlam — hayalinizi korkusuzca inşa edin."
        },
        "22:22": {
            "meaning": "Master titreşim. Hayalleriniz şekilleniyor — durmayın."
        },
        "23:23": {
            "meaning": "Yükselmiş üstatlar size yardım ediyor. Yeteneklerinize güvenin ve harekete geçin."
        },
        "333": {
            "meaning": "Yükselmiş üstatlar sizi sevgiyle kuşatıyor. Yaratıcı yeteneklerinizi serbest bırakın."
        },
        "444": {
            "meaning": "Binlerce melek yanınızda. Tamamen güvendesiniz — yolunuza devam edin."
        },
        "555": {
            "meaning": "Ufukta büyük değişiklikler. Hazır olun — hayat rotasını değiştiriyor."
        },
        "666": {
            "meaning": "Maddi dünyada dengeyi yeniden sağlayın. Maneviyat, maddiyattan daha önemlidir."
        },
        "777": {
            "meaning": "İlahi şans! Evrensel akışla tamamen uyum içindesiniz."
        },
        "888": {
            "meaning": "Finansal bolluk nehir gibi akıyor. Refah döngüsü başladı."
        },
        "999": {
            "meaning": "Büyük tamamlanma. Bir bölüm kapanıyor — yenisi zaten yazılıyor."
        }
    },
    "uk": {
        "00:00": {
            "meaning": "Початок нового циклу. Всесвіт обнулює лічильник — загадайте бажання та почніть з чистого аркуша."
        },
        "01:01": {
            "meaning": "Ваші думки матеріалізуються. Слідкуйте за тим, про що думаєте — це стане реальністю."
        },
        "02:02": {
            "meaning": "Довіртеся процесу. Партнерство та співпраця принесуть результат."
        },
        "03:03": {
            "meaning": "Піднесені майстри поруч. Творча енергія на піку — дійте."
        },
        "04:04": {
            "meaning": "Ангели захищають вас. Фундамент вашого життя зміцнюється."
        },
        "05:05": {
            "meaning": "Насувають важливі зміни. Прийміть їх — вони на краще."
        },
        "06:06": {
            "meaning": "Приділіть увагу сім’ї та дому. Гармонія в близьких стосунках важливіша за кар’єру."
        },
        "07:07": {
            "meaning": "Ви на правильному шляху духовного розвитку. Продовжуйте медитувати та вивчати себе."
        },
        "08:08": {
            "meaning": "Фінансова достатність наближається. Ви заслуговуєте на процвітання."
        },
        "09:09": {
            "meaning": "Цикл завершується. Відпустіть старе — нове вже на порозі."
        },
        "10:10": {
            "meaning": "Вищі сили підтверджують ваш вибір. Довіртеся інтуїції."
        },
        "111": {
            "meaning": "Потужний потік енергії. Ваші думки миттєво набувають форми — контролюйте їх."
        },
        "1111": {
            "meaning": "Космічний портал відкрито. Все, про що ви думаєте, втілиться. Загадайте найпотаємніше."
        },
        "11:11": {
            "meaning": "Портал можливостей відкритий. Ваші думки миттєво матеріалізуються — думайте про хороше."
        },
        "12:12": {
            "meaning": "Оптимізм принесе плоди. Вірте в краще — всесвіт на вашому боці."
        },
        "13:13": {
            "meaning": "Трансформація неминуча. Не бійтеся змін — вони несуть оновлення."
        },
        "14:14": {
            "meaning": "Ангели допомагають зберігати баланс. Помірність — ключ до успіху."
        },
        "15:15": {
            "meaning": "Зміни в особистому житті. Любов і відносини виходять на новий рівень."
        },
        "16:16": {
            "meaning": "Відпустіть ілюзії. Істина звільнить вас від хибних прив'язаностей."
        },
        "17:17": {
            "meaning": "Ви на порозі удачі. Ваші зусилля скоро будуть винагороджені."
        },
        "18:18": {
            "meaning": "Фінансовий цикл завершується позитивно. Очікуйте прибутку."
        },
        "19:19": {
            "meaning": "Завершіть розпочате. Пора зібрати врожай своїх трудів."
        },
        "20:20": {
            "meaning": "Божественна підтримка посилюється. Віра та терпіння приведуть до мети."
        },
        "21:21": {
            "meaning": "Залишайтеся позитивними. Ваш оптимізм притягує потрібних людей."
        },
        "222": {
            "meaning": "Все йде за планом. Не втрачайте віру — результат вже близько."
        },
        "2222": {
            "meaning": "Майстер-будівельник. Ваш фундамент міцний — будуйте мрію без страху."
        },
        "22:22": {
            "meaning": "Майстер-вібрація. Ваші мрії набувають форми — не зупиняйтесь."
        },
        "23:23": {
            "meaning": "Вознесені майстри допомагають вам. Довіряйте своїм та"
        },
        "333": {
            "meaning": "Вознесені майстри оточують вас любов’ю. Розкрийте свої творчі здібності."
        },
        "444": {
            "meaning": "Тисячі ангелів поруч. Ви в повній безпеці — продовжуйте шлях."
        },
        "555": {
            "meaning": "Масштабні зміни на горизонті. Будьте готові — життя змінює курс."
        },
        "666": {
            "meaning": "Поверніть баланс у матеріальний світ. Духовне важливіше за матеріальне."
        },
        "777": {
            "meaning": "Божественна удача! Ви повністю вирівняні з потоком всесвіту."
        },
        "888": {
            "meaning": "Фінансова достаток ллється рікою. Цикл процвітання розпочався"
        },
        "999": {
            "meaning": "Велике завершення. Глава закривається — нова вже пишеться."
        }
    }
}
