"""ES/PT/TR/UK content for runes.py / staves.py (TZ-080).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n.
- RUNES_I18N: key is the rune id (e.g. "fehu"); fields are name, keyword,
  meaning, reversed_meaning (only for runes where can_reverse is true),
  deity, love, career, health, magic, as_amulet.
- SPREADS_RUNES_I18N: key is the spread id (e.g. "rune_of_day"); fields are
  name, desc, and indexed position items ("positions_0", "positions_1", ...).
- STAVES_I18N: key is the stave id; fields are name, purpose, description,
  how_to_use.

`areas` (RUNES) is deliberately not covered here — it's never read by the
API (dead data), so translating it would be pure cost with no user-visible
effect.

Generated in batches by scripts/generate_structural_translations.py
--section runes (all fields of one rune/spread/stave in a single API call,
not one call per field — see BATCHED_SECTIONS in that script). Empty until
that runs; pick()/pick_list() fall back to English for any language not
present here yet.
"""

















































































































































































RUNES_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "algiz": {
            "as_amulet": "Amuleto protector principal. Usar para seguridad y protección.",
            "career": "Protección contra competidores e intrigas. Patrocinio del jefe.",
            "deity": "Heimdall",
            "health": "Inmunidad fortalecida. El cuerpo se protege a sí mismo.",
            "keyword": "Protección",
            "love": "Protección de las relaciones de amenazas externas. Vínculo espiritual con la pareja.",
            "magic": "Signo protector más poderoso. Escudo contra cualquier negatividad.",
            "meaning": "Poderosa protección divina. El instinto de autoconservación se agudiza. La conexión espiritual con las fuerzas superiores se fortalece. Estás bajo protección.",
            "name": "Algiz",
            "reversed_meaning": "Vulnerabilidad, peligro oculto. Tu protección está debilitada. Mantente vigilante."
        },
        "ansuz": {
            "as_amulet": "Para sabiduría, suerte en exámenes, desarrollo de la intuición.",
            "career": "Mentoría, negociaciones, hablar en público — tu momento.",
            "deity": "Odín",
            "health": "Presta atención a la garganta, el cuello, el sistema nervioso.",
            "keyword": "Sabiduría",
            "love": "Una conversación profunda aclarará las relaciones. Escucha a tu pareja con atención.",
            "magic": "Conexión con fuerzas superiores, desarrollo de la elocuencia, obtención de conocimiento.",
            "meaning": "Inspiración divina y sabiduría. Recibirás un mensaje importante — presta atención a las señales. La comunicación, el aprendizaje y la transmisión de conocimientos son favorables.",
            "name": "Ansuz",
            "reversed_meaning": "Engaño, manipulación, malentendido. Alguien distorsiona la verdad. No confíes ciegamente en los consejos."
        },
        "berkano": {
            "as_amulet": "Para el embarazo, la maternidad y los suaves nuevos comienzos.",
            "career": "Nacimiento de un nuevo proyecto. Crecimiento suave pero constante.",
            "deity": "Frigg",
            "health": "Salud femenina, sistema reproductivo, maternidad.",
            "keyword": "Abedul",
            "love": "Embarazo, boda, nacimiento de sentimientos. Energía femenina.",
            "magic": "Fertilidad, protección maternal, sanación suave.",
            "meaning": "Nacimiento, crecimiento, fertilidad, feminidad. Nuevo comienzo, fuerza suave de la naturaleza. Cuidar de la familia y los hijos es favorecido.",
            "name": "Berkano",
            "reversed_meaning": "Infertilidad, estancamiento del crecimiento, conflictos familiares. El cuidado se convierte en control."
        },
        "dagaz": {
            "as_amulet": "Para nuevos comienzos, avances y atraer luz a la vida.",
            "career": "Giro radical en la carrera. Nuevos horizontes se abren.",
            "deity": "Heimdall",
            "health": "Recuperación, mejora tras la crisis. Luz al final del túnel.",
            "keyword": "Amanecer",
            "love": "Nuevo amanecer en las relaciones. Después de la oscuridad — la luz. Perdón.",
            "magic": "Rompiendo bloqueos, transformación de la realidad, nuevo comienzo.",
            "meaning": "Avance, amanecer, transformación. La oscuridad queda atrás — la luz por delante. Cambio radical para mejor. Iluminación y esperanza.",
            "name": "Dagaz"
        },
        "ehwaz": {
            "as_amulet": "Para avance rápido y encontrar un aliado leal.",
            "career": "Avance rápido, cambio de trabajo para mejor, reubicación.",
            "deity": "Freyr",
            "health": "Piernas, caderas. La equitación y los deportes son beneficiosos.",
            "keyword": "Caballo",
            "love": "Unión armoniosa, avanzando juntos. La confianza se fortalece.",
            "magic": "Acelerar procesos, viajar entre mundos, aliado leal.",
            "meaning": "Movimiento, progreso, confianza entre socios. Cambios rápidos para mejor. Un compañero leal está cerca. Trabajo en equipo.",
            "name": "Ehwaz",
            "reversed_meaning": "Estancamiento, desconfianza, vínculos rotos. Movimiento en la dirección equivocada."
        },
        "eihwaz": {
            "as_amulet": "Para resistencia, protección y conexión con los ancestros.",
            "career": "Resistencia en condiciones difíciles. La experiencia es tu arma.",
            "deity": "Odín",
            "health": "Columna vertebral, huesos. Fortalece el sistema musculoesquelético.",
            "keyword": "Tejo",
            "love": "Transformación profunda de la relación. Superación de la crisis juntos.",
            "magic": "Protección contra la muerte, viaje entre mundos, prácticas chamánicas.",
            "meaning": "Resistencia, conexión de mundos, transformación a través de pruebas. El Árbol del Mundo es tu apoyo. Superación del miedo a la muerte y renacimiento.",
            "name": "Eihwaz"
        },
        "fehu": {
            "as_amulet": "Usar para atraer dinero y bienestar material.",
            "career": "Crecimiento financiero, ascenso, nuevo proyecto rentable. Actúa con decisión.",
            "deity": "Freya",
            "health": "La energía está en aumento. Invierte en salud — los resultados llegarán.",
            "keyword": "Riqueza",
            "love": "La generosidad en las relaciones da frutos. Las inversiones conjuntas fortalecen el vínculo.",
            "magic": "Atraer riqueza, fortalecer el flujo financiero, protección de la propiedad.",
            "meaning": "Bienestar material y prosperidad. Nuevos emprendimientos traen ganancias. La energía de adquisición y crecimiento fluye hacia ti. Es momento de invertir tus esfuerzos.",
            "name": "Fehu",
            "reversed_meaning": "Pérdidas financieras, avaricia, estancamiento. Gastos imprudentes o aferrarse a lo que debe soltarse. Reconsidera tu relación con lo material."
        },
        "gebo": {
            "as_amulet": "Para atraer el amor y fortalecer la pareja.",
            "career": "Asociación rentable, firma de contratos, acuerdos ganar-ganar.",
            "deity": "Odín",
            "health": "Equilibrio y armonía del cuerpo. Las prácticas en pareja son beneficiosas.",
            "keyword": "Regalo",
            "love": "Momento perfecto para las relaciones. Reciprocidad y armonía. Posible compromiso.",
            "magic": "Runa de amor, fortalecimiento de vínculos, armonización de relaciones.",
            "meaning": "Regalo, asociación, intercambio equitativo. La generosidad regresa. Relaciones armoniosas basadas en el respeto mutuo. Los acuerdos y alianzas son favorecidos.",
            "name": "Gebo"
        },
        "hagalaz": {
            "as_amulet": "Para protección contra los elementos y destrucción de patrones negativos.",
            "career": "Despido, bancarrota, colapso de planes. Pero es liberación para lo nuevo.",
            "deity": "Hel",
            "health": "Brotes de enfermedades crónicas. Presta atención al sistema nervioso.",
            "keyword": "Granizo",
            "love": "Crisis en las relaciones. Pero a través de ella, renovación o liberación.",
            "magic": "Destrucción de la negatividad, eliminación de maldiciones, renovación radical.",
            "meaning": "Destrucción y transformación inevitable. Cambios elementales fuera de tu control. A través de la destrucción de lo viejo, nace lo nuevo. Acepta y adáptate.",
            "name": "Hagalaz"
        },
        "ingwaz": {
            "as_amulet": "Para la fertilidad, completar tareas y la fuerza masculina.",
            "career": "Proyecto completado con éxito. Descanso merecido antes de una nueva fase.",
            "deity": "Freyr",
            "health": "Sistema reproductivo. Descanso y restauración de energía.",
            "keyword": "Semilla",
            "love": "Concepción, período acogedor en pareja. Felicidad doméstica.",
            "magic": "Fertilidad, finalización de rituales, acumulación de poder mágico.",
            "meaning": "Fertilidad, finalización del ciclo, paz interior. La semilla está plantada — déjala crecer. Período de acumulación de fuerzas antes de un avance.",
            "name": "Ingwaz"
        },
        "isa": {
            "as_amulet": "Para encontrar paz y detener procesos no deseados.",
            "career": "Proyectos congelados. Usa la pausa para planificar.",
            "deity": "Verdandi",
            "health": "Procesos lentos. El descanso y la recuperación son necesarios.",
            "keyword": "Hielo",
            "love": "Enfriamiento de sentimientos, pausa en la relación. No tomes decisiones ahora.",
            "magic": "Congelar una situación, detener acciones hostiles, meditación.",
            "meaning": "Inmovilidad, pausa, introspección. Todo se detuvo por una razón — es tiempo de trabajo interno. No apresures los acontecimientos. La quietud trae claridad.",
            "name": "Isa"
        },
        "jera": {
            "as_amulet": "Para buena cosecha, éxito en los negocios y resultados justos.",
            "career": "Ascenso merecido, pago de bonificación, finalización del proyecto.",
            "deity": "Freyr",
            "health": "Recuperación, mejora después de un tratamiento prolongado.",
            "keyword": "Cosecha",
            "love": "Las relaciones dan frutos. Esfuerzos conjuntos recompensados.",
            "magic": "Atraer fertilidad, éxito en los negocios, resultado favorable.",
            "meaning": "Cosecha, recompensa por el esfuerzo, finalización del ciclo. Cosechas lo que sembraste. Resultados justos. Los ciclos de la naturaleza trabajan para ti.",
            "name": "Jera"
        },
        "kenaz": {
            "as_amulet": "Para inspiración, desarrollo de talentos y claridad mental.",
            "career": "Avance creativo, nuevas ideas, el aprendizaje da frutos.",
            "deity": "Freya",
            "health": "Procesos inflamatorios. Atención a la temperatura y la fiebre.",
            "keyword": "Antorcha",
            "love": "Pasión y atracción. Nuevo romance o renacimiento de sentimientos.",
            "magic": "Revelación de secretos, potenciación de la intuición, rituales creativos.",
            "meaning": "Luz del conocimiento y fuego creativo. Visión, claridad de pensamiento, inspiración. Los proyectos creativos tienen éxito. Tiempo de aprender y crear.",
            "name": "Kenaz",
            "reversed_meaning": "Oscuridad, ignorancia, bloqueo creativo. Pérdida de inspiración. Falsas ilusiones nublan la mente."
        },
        "laguz": {
            "as_amulet": "Para el desarrollo de la intuición, la creatividad y el poder femenino.",
            "career": "Profesiones creativas. Las decisiones intuitivas son correctas.",
            "deity": "Njord",
            "health": "Riñones, vejiga, linfa. Bebe más agua.",
            "keyword": "Agua",
            "love": "Emociones profundas, romance. Confía en los sentimientos, no en la lógica.",
            "magic": "Mejorar la intuición, trabajo con sueños, rituales acuáticos.",
            "meaning": "Flujo, intuición, subconsciente. Confía en la corriente — el agua encuentra el camino. Las emociones y los sueños transmiten mensajes importantes. Sabiduría femenina.",
            "name": "Laguz",
            "reversed_meaning": "Miedo, ilusiones, perder el camino. Las emociones abruman. No confíes en las primeras impresiones."
        },
        "mannaz": {
            "as_amulet": "Para el desarrollo del intelecto, el autoconocimiento y la armonía con la sociedad.",
            "career": "Trabajo en equipo, mentoría. Tu intelecto es la clave del éxito.",
            "deity": "Heimdall",
            "health": "Salud mental. Meditación y autoconocimiento.",
            "keyword": "Humano",
            "love": "Comprensión mutua, conexión intelectual. Conocerse el uno al otro.",
            "magic": "Potenciar la mente, autoconocimiento, conexión con la conciencia colectiva.",
            "meaning": "Autoconocimiento, mente, sociedad. Eres parte de un todo mayor. Tiempo para la introspección y la actividad social. La ayuda vendrá de las personas.",
            "name": "Mannaz",
            "reversed_meaning": "Soledad, egoísmo, autoengaño. Te has aislado del mundo. Acepta la ayuda."
        },
        "nauthiz": {
            "as_amulet": "Para desarrollar la paciencia y superar las dificultades de la vida.",
            "career": "Restricciones en el trabajo. La paciencia será recompensada. No abandones lo empezado.",
            "deity": "Skuld",
            "health": "Una dieta restrictiva es beneficiosa. El endurecimiento y el ascetismo fortalecen.",
            "keyword": "Necesidad",
            "love": "Soledad o restricciones en las relaciones. Pero es tiempo de autoconocimiento.",
            "magic": "Superación de obstáculos, paciencia, protección a través de restricciones.",
            "meaning": "Necesidad y limitaciones. La paciencia es tu herramienta principal. A través de la necesidad llega la comprensión de los verdaderos deseos. Tiempo de ascetismo.",
            "name": "Nauthiz",
            "reversed_meaning": "Impaciencia, pereza, negarse a aprender de los errores. Te resistes a las lecciones necesarias."
        },
        "othala": {
            "as_amulet": "Para protección del hogar, conexión con el clan y obtención de herencia.",
            "career": "Negocio familiar, herencia, transacciones inmobiliarias.",
            "deity": "Odín",
            "health": "Condiciones hereditarias. Estudia el historial médico familiar.",
            "keyword": "Herencia",
            "love": "Valores familiares, encuentro con un 'alma afín'. El hogar es una fortaleza.",
            "magic": "Protección del hogar, conexión con los antepasados, transmisión del poder del clan.",
            "meaning": "Hogar, clan, herencia ancestral. La conexión con las raíces da fuerza. Bienes raíces, herencia, valores familiares. La sabiduría del clan te guía.",
            "name": "Othala",
            "reversed_meaning": "Pérdida del hogar, ruptura con el clan, alienación. Falta de hogar, rechazo de tradiciones."
        },
        "perthro": {
            "as_amulet": "Para la suerte, revelar secretos y potenciar la intuición.",
            "career": "Oportunidades ocultas emergen. Suerte en concursos y loterías.",
            "deity": "Frigg",
            "health": "Condiciones ocultas. Hazte un chequeo médico.",
            "keyword": "Misterio",
            "love": "Sentimientos secretos revelados. Encuentro o confesión inesperados.",
            "magic": "Adivinación, profecía, revelación de secretos, trabajo con el destino.",
            "meaning": "Destino, conocimiento oculto, misterio. Algo oculto está a punto de revelarse. Suerte en juegos y adivinaciones. Confía en el flujo del destino.",
            "name": "Perthro",
            "reversed_meaning": "Secretos revelados en el momento equivocado. Estancamiento, decepción en predicciones. No intentes controlar el destino."
        },
        "raido": {
            "as_amulet": "Para viajes seguros y encontrar el camino correcto en la vida.",
            "career": "Viajes de negocios, reubicación por trabajo. Crecimiento profesional a través del movimiento.",
            "deity": "Thor",
            "health": "El estilo de vida activo es beneficioso. Caminar y viajar curan.",
            "keyword": "Viaje",
            "love": "Un viaje conjunto fortalecerá la relación. Nueva fase para la pareja.",
            "magic": "Protección en el viaje, encontrar la dirección correcta, viaje espiritual.",
            "meaning": "Viaje — físico o espiritual. Movimiento hacia adelante, progreso, ritmo de vida. La dirección correcta está elegida — sigue adelante.",
            "name": "Raido",
            "reversed_meaning": "Estancamiento, retrasos en el viaje, ruta equivocada. Reconsidera los planes de viaje. Inquietud interior."
        },
        "sowilo": {
            "as_amulet": "Para la victoria, el éxito y el llenado de energía vital.",
            "career": "Triunfo, premios, reconocimiento público. Tu mejor momento.",
            "deity": "Baldr",
            "health": "Vitamina D, sol, energía. Excelente bienestar.",
            "keyword": "Sol",
            "love": "Período brillante y alegre en las relaciones. El amor brilla.",
            "magic": "Victoria sobre la oscuridad, sanación, llenado de energía solar.",
            "meaning": "Sol, victoria, fuerza vital. Totalidad y éxito. La luz disipa la oscuridad. Tiempo de triunfo y plenitud de energía.",
            "name": "Sowilo"
        },
        "thurisaz": {
            "as_amulet": "Protección contra enemigos e influencias negativas. Superación de obstáculos.",
            "career": "Avance a través de obstáculos. Pero ten cuidado con los conflictos.",
            "deity": "Thor",
            "health": "Condiciones agudas. No retrases la visita al médico.",
            "keyword": "Puerta",
            "love": "Período apasionado pero peligroso. No presiones a tu pareja. Protege los límites.",
            "magic": "Protección poderosa, destrucción de influencias hostiles, apertura de caminos.",
            "meaning": "Protección y ruptura de barreras. Fuerza poderosa que requiere control. Estás ante una puerta — tu decisión lo cambia todo. Actúa conscientemente.",
            "name": "Thurisaz",
            "reversed_meaning": "Vulnerabilidad, decisiones apresuradas, peligro. No actúes impulsivamente. Enemigos ocultos están cerca."
        },
        "tiwaz": {
            "as_amulet": "Para la victoria, la justicia y la fuerza masculina.",
            "career": "Victoria competitiva. Asuntos legales resueltos a tu favor.",
            "deity": "Tyr",
            "health": "Brazos, lado derecho del cuerpo. Salud masculina.",
            "keyword": "Guerrero",
            "love": "Honestidad en las relaciones. Sacrificio por amor. Energía masculina.",
            "magic": "Victoria en disputas, justicia, protección del guerrero.",
            "meaning": "Justicia, honor, coraje, victoria en una causa justa. La ley está de tu lado. El sacrificio por un propósito superior está justificado.",
            "name": "Tiwaz",
            "reversed_meaning": "Injusticia, derrota, traición. El sacrificio es en vano. Asuntos legales no a tu favor."
        },
        "uruz": {
            "as_amulet": "Para la salud, la fuerza física y la recuperación tras una enfermedad.",
            "career": "Avance mediante la persistencia. El esfuerzo físico es recompensado.",
            "deity": "Thor",
            "health": "Buena salud, recuperación rápida. Practica deportes.",
            "keyword": "Fuerza",
            "love": "Relaciones apasionadas y fuertes. Atracción física. Superación de dificultades juntos.",
            "magic": "Sanación, fortalecimiento del cuerpo y el espíritu, obtención de poder interior.",
            "meaning": "Fuerza primitiva y salud. Resistencia física y mental en su punto máximo. Superación de obstáculos mediante la perseverancia. Momento de actuar, no de esperar.",
            "name": "Uruz",
            "reversed_meaning": "Debilidad, enfermedad, oportunidades perdidas. Estás desperdiciando energía. Detente y recupera tus fuerzas."
        },
        "wunjo": {
            "as_amulet": "Para la felicidad, la alegría y el cumplimiento de los deseos.",
            "career": "Satisfacción laboral. Reconocimiento de los colegas, atmósfera agradable.",
            "deity": "Odín",
            "health": "Bienestar. Las emociones positivas sanan.",
            "keyword": "Alegría",
            "love": "Felicidad en las relaciones. Amor mutuo, período cálido.",
            "magic": "Atraer la felicidad, cumplimiento de deseos, armonización del espacio.",
            "meaning": "Alegría, felicidad, armonía. Los deseos se cumplen. Período de satisfacción y elevación emocional. Disfruta el momento.",
            "name": "Wunjo",
            "reversed_meaning": "Tristeza, crisis, decepción. La alegría no está disponible temporalmente. Reevaluación de valores."
        },
        "wyrd": {
            "as_amulet": "No se usa como amuleto — símbolo de aceptación de lo desconocido.",
            "career": "Incertidumbre. El resultado no depende de ti.",
            "deity": "Nornas",
            "health": "Situación poco clara. Confía en un sanador y en fuerzas superiores.",
            "keyword": "Destino",
            "love": "El destino decidirá por ti. Confía en el flujo.",
            "magic": "Entrega total al destino. Meditación sobre el vacío. Aceptación.",
            "meaning": "Runa en blanco — destino puro. Lo incognoscible, intervención divina. La situación está completamente en manos de fuerzas superiores. Confía y acepta.",
            "name": "Wyrd"
        }
    },
    "pt": {
        "algiz": {
            "as_amulet": "Amuleto protetor principal. Use para segurança e proteção.",
            "career": "Proteção contra concorrentes e intrigas. Patrocínio do chefe.",
            "deity": "Heimdall",
            "health": "Imunidade fortalecida. O corpo se protege.",
            "keyword": "Proteção",
            "love": "Protegendo relacionamentos de ameaças externas. Vínculo espiritual com o parceiro.",
            "magic": "Sinal protetor mais poderoso. Escudo contra qualquer negatividade.",
            "meaning": "Poderosa proteção divina. O instinto de autopreservação está aguçado. A conexão espiritual com forças superiores se fortalece. Você está sob guarda.",
            "name": "Algiz",
            "reversed_meaning": "Vulnerabilidade, perigo oculto. Sua proteção está enfraquecida. Fique vigilante."
        },
        "ansuz": {
            "as_amulet": "Para sabedoria, sorte em exames, desenvolvimento da intuição.",
            "career": "Mentoria, negociações, falar em público — sua hora.",
            "deity": "Odin",
            "health": "Preste atenção à garganta, pescoço, sistema nervoso.",
            "keyword": "Sabedoria",
            "love": "Uma conversa profunda esclarecerá os relacionamentos. Ouça seu parceiro com atenção.",
            "magic": "Conexão com forças superiores, desenvolvimento da eloquência, obtenção de conhecimento.",
            "meaning": "Inspiração divina e sabedoria. Você receberá uma mensagem importante — fique atento aos sinais. Comunicação, aprendizado e compartilhamento de conhecimento são favorecidos.",
            "name": "Ansuz",
            "reversed_meaning": "Engano, manipulação, mal-entendido. Alguém distorce a verdade. Não confie cegamente em conselhos."
        },
        "berkano": {
            "as_amulet": "Para gravidez, maternidade e novos começos suaves.",
            "career": "Nascimento de um novo projeto. Crescimento suave, mas constante.",
            "deity": "Frigg",
            "health": "Saúde feminina, sistema reprodutivo, maternidade.",
            "keyword": "Bétula",
            "love": "Gravidez, casamento, nascimento de sentimentos. Energia feminina.",
            "magic": "Fertilidade, proteção materna, cura suave.",
            "meaning": "Nascimento, crescimento, fertilidade, feminilidade. Novo começo, força suave da natureza. Cuidar da família e dos filhos é favorecido.",
            "name": "Berkano",
            "reversed_meaning": "Infertilidade, estagnação no crescimento, conflitos familiares. O cuidado se transforma em controle."
        },
        "dagaz": {
            "as_amulet": "Para novos começos, avanços e atrair luz para a vida.",
            "career": "Mudança radical de carreira. Novos horizontes se abrindo.",
            "deity": "Heimdall",
            "health": "Recuperação, melhora após crise. Luz no fim do túnel.",
            "keyword": "Amanhecer",
            "love": "Novo amanhecer nos relacionamentos. Após a escuridão — a luz. Perdão.",
            "magic": "Rompendo bloqueios, transformação da realidade, novo começo.",
            "meaning": "Avanço, amanhecer, transformação. A escuridão está atrás — a luz à frente. Mudança radical para melhor. Iluminação e esperança.",
            "name": "Dagaz"
        },
        "ehwaz": {
            "as_amulet": "Para avanço rápido e encontrar um aliado leal.",
            "career": "Avanço rápido, mudança de emprego para melhor, realocação.",
            "deity": "Freyr",
            "health": "Pernas, quadris. Passeios a cavalo e esportes são benéficos.",
            "keyword": "Cavalo",
            "love": "União harmoniosa, avançando juntos. A confiança se fortalece.",
            "magic": "Aceleração de processos, jornada entre mundos, aliado leal.",
            "meaning": "Movimento, progresso, confiança entre parceiros. Mudanças rápidas para melhor. Um companheiro leal está por perto. Trabalho em equipe.",
            "name": "Ehwaz",
            "reversed_meaning": "Estagnação, desconfiança, laços rompidos. Movimento na direção errada."
        },
        "eihwaz": {
            "as_amulet": "Para resiliência, proteção e conexão com os ancestrais.",
            "career": "Resiliência em condições difíceis. A experiência é sua arma.",
            "deity": "Odin",
            "health": "Coluna, ossos. Fortaleça o sistema musculoesquelético.",
            "keyword": "Teixo",
            "love": "Transformação profunda do relacionamento. Superação da crise juntos.",
            "magic": "Proteção contra a morte, jornada entre mundos, práticas xamânicas.",
            "meaning": "Resiliência, conexão mundial, transformação através de provações. A Árvore do Mundo é seu apoio. Superar o medo da morte e renascimento.",
            "name": "Eihwaz"
        },
        "fehu": {
            "as_amulet": "Usar para atrair dinheiro e bem-estar material.",
            "career": "Crescimento financeiro, promoção, novo projeto lucrativo. Aja com determinação.",
            "deity": "Freya",
            "health": "Energia em ascensão. Invista na saúde — o resultado virá.",
            "keyword": "Riqueza",
            "love": "Generosidade nos relacionamentos dá frutos. Investimentos conjuntos fortalecem o vínculo.",
            "magic": "Atrair riqueza, fortalecer o fluxo financeiro, proteção de propriedade.",
            "meaning": "Bem-estar material e prosperidade. Novos empreendimentos trazem lucro. A energia de aquisição e crescimento flui em sua direção. Hora de investir seus esforços.",
            "name": "Fehu",
            "reversed_meaning": "Perdas financeiras, ganância, estagnação. Gastos imprudentes ou apego ao que deve ser liberado. Reconsidere sua relação com o material."
        },
        "gebo": {
            "as_amulet": "Para atrair amor e fortalecer parceria.",
            "career": "Parceria lucrativa, assinatura de contratos, negócios ganha-ganha.",
            "deity": "Odin",
            "health": "Equilíbrio e harmonia do corpo. Práticas em pares são benéficas.",
            "keyword": "Dom",
            "love": "Momento ideal para relacionamentos. Reciprocidade e harmonia. Possível noivado.",
            "magic": "Runa do amor, fortalecendo laços, harmonizando relacionamentos.",
            "meaning": "Dom, parceria, troca equivalente. A generosidade retorna. Relacionamentos harmoniosos baseados em respeito mútuo. Acordos e alianças são favorecidos.",
            "name": "Gebo"
        },
        "hagalaz": {
            "as_amulet": "Para proteção contra os elementos e destruição de programas negativos.",
            "career": "Demissão, falência, colapso de planos. Mas é libertação para o novo.",
            "deity": "Hel",
            "health": "Exacerbações de doenças crônicas. Preste atenção ao sistema nervoso.",
            "keyword": "Granizo",
            "love": "Crise no relacionamento. Mas através dela — renovação ou libertação.",
            "magic": "Destruição do negativo, remoção de maldição, renovação radical.",
            "meaning": "Destruição e transformação inevitável. Mudanças elementares fora do seu controle. Através da destruição do velho, o novo nasce. Aceite e adapte-se.",
            "name": "Hagalaz"
        },
        "ingwaz": {
            "as_amulet": "Para fertilidade, conclusão de tarefas e força masculina.",
            "career": "Projeto concluído com sucesso. Descanso merecido antes de uma nova fase.",
            "deity": "Freyr",
            "health": "Sistema reprodutivo. Descanso e restauração de energias.",
            "keyword": "Semente",
            "love": "Concepção, período aconchegante no casal. Felicidade doméstica.",
            "magic": "Fertilidade, conclusão de rituais, acúmulo de poder mágico.",
            "meaning": "Fertilidade, conclusão de ciclo, paz interior. A semente foi plantada — deixe-a germinar. Período de acúmulo de forças antes de um avanço.",
            "name": "Ingwaz"
        },
        "isa": {
            "as_amulet": "Para obter paz e interromper processos indesejados.",
            "career": "Projetos congelados. Use a pausa para planejar.",
            "deity": "Verdandi",
            "health": "Desaceleração dos processos. Descanso e recuperação são necessários.",
            "keyword": "Gelo",
            "love": "Esfriamento dos sentimentos, pausa no relacionamento. Não tome decisões agora.",
            "magic": "Congelamento da situação, interrupção de ações hostis, meditação.",
            "meaning": "Imobilidade, pausa, autoanálise. Tudo parou por um motivo — é hora de trabalho interno. Não se apresse. A quietude traz clareza.",
            "name": "Isa"
        },
        "jera": {
            "as_amulet": "Para boa colheita, sucesso nos negócios e resultados justos.",
            "career": "Promoção merecida, pagamento de bônus, conclusão de projeto.",
            "deity": "Freyr",
            "health": "Recuperação, melhora após tratamento prolongado.",
            "keyword": "Colheita",
            "love": "Os relacionamentos dão frutos. Esforços conjuntos são recompensados.",
            "magic": "Atrair fertilidade, sucesso nos negócios, resultado favorável.",
            "meaning": "Colheita, recompensa pelo esforço, conclusão de ciclo. Você colhe o que plantou. Resultado justo. Os ciclos da natureza trabalham a seu favor.",
            "name": "Jera"
        },
        "kenaz": {
            "as_amulet": "Para inspiração, desbloqueio de talentos e clareza mental.",
            "career": "Avanço criativo, novas ideias, aprendizado dá frutos.",
            "deity": "Freya",
            "health": "Processos inflamatórios. Atenção à temperatura e febre.",
            "keyword": "Tocha",
            "love": "Paixão e atração. Novo romance ou renascimento dos sentimentos.",
            "magic": "Revelação de segredos, fortalecimento da intuição, rituais criativos.",
            "meaning": "Luz do conhecimento e do fogo criativo. Percepção, clareza de pensamento, inspiração. Projetos criativos são bem-sucedidos. Tempo de aprender e criar.",
            "name": "Kenaz",
            "reversed_meaning": "Trevas, ignorância, bloqueio criativo. Perda de inspiração. Ilusões falsas obscurecem a mente."
        },
        "laguz": {
            "as_amulet": "Para desenvolvimento da intuição, criatividade e poder feminino.",
            "career": "Profissões criativas. Decisões intuitivas estão corretas.",
            "deity": "Njord",
            "health": "Rins, bexiga, linfa. Beba mais água.",
            "keyword": "Água",
            "love": "Emoções profundas, romance. Confie nos sentimentos, não na lógica.",
            "magic": "Aprimoramento da intuição, trabalho com sonhos, rituais aquáticos.",
            "meaning": "Fluxo, intuição, subconsciente. Confie na correnteza — a água encontra o caminho. Emoções e sonhos carregam mensagens importantes. Sabedoria feminina.",
            "name": "Laguz",
            "reversed_meaning": "Medo, ilusões, perda do caminho. Emoções avassaladoras. Não confie na primeira impressão."
        },
        "mannaz": {
            "as_amulet": "Para desenvolvimento do intelecto, autoconhecimento e harmonia com a sociedade.",
            "career": "Trabalho em equipe, mentoria. Seu intelecto é a chave para o sucesso.",
            "deity": "Heimdall",
            "health": "Saúde mental. Meditação e autoconhecimento.",
            "keyword": "Humano",
            "love": "Compreensão mútua, conexão intelectual. Conhecendo um ao outro.",
            "magic": "Aprimoramento da mente, autoconhecimento, conexão com a consciência coletiva.",
            "meaning": "Autoconhecimento, mente, sociedade. Você faz parte de um todo maior. Hora de autorreflexão e atividade social. A ajuda virá das pessoas.",
            "name": "Mannaz",
            "reversed_meaning": "Solidão, egoísmo, autoengano. Você se isolou. Aceite ajuda."
        },
        "nauthiz": {
            "as_amulet": "Para desenvolver paciência e superar dificuldades da vida.",
            "career": "Restrições no trabalho. A paciência será recompensada. Não desista.",
            "deity": "Skuld",
            "health": "Dieta restritiva é benéfica. O endurecimento e a ascese fortalecem.",
            "keyword": "Necessidade",
            "love": "Solidão ou restrições no relacionamento. Mas é tempo de autoconhecimento.",
            "magic": "Superação de obstáculos, paciência, proteção através de restrições.",
            "meaning": "Necessidade e restrições. A paciência é sua principal ferramenta. Através da necessidade vem a compreensão dos verdadeiros desejos. Tempo de ascese.",
            "name": "Nauthiz",
            "reversed_meaning": "Impaciência, preguiça, recusa em aprender com os erros. Você resiste às lições necessárias."
        },
        "othala": {
            "as_amulet": "Para proteção do lar, conexão com o clã e obtenção da herança.",
            "career": "Negócio familiar, herança, negócios imobiliários.",
            "deity": "Odin",
            "health": "Condições hereditárias. Estude o histórico médico familiar.",
            "keyword": "Herança",
            "love": "Valores familiares, encontrar uma 'alma gêmea'. Lar é uma fortaleza.",
            "magic": "Proteção do lar, conexão com ancestrais, transmissão do poder do clã.",
            "meaning": "Lar, clã, herança ancestral. A conexão com as raízes dá força. Imóveis, herança, valores familiares. A sabedoria do clã guia você.",
            "name": "Othala",
            "reversed_meaning": "Perda do lar, ruptura com o clã, alienação. Falta de lar, rejeição das tradições."
        },
        "perthro": {
            "as_amulet": "Para sorte, revelação de segredos e aumento da intuição.",
            "career": "Oportunidades ocultas emergem. Sorte em competições e loterias.",
            "deity": "Frigg",
            "health": "Condições ocultas. Faça um exame médico.",
            "keyword": "Mistério",
            "love": "Sentimentos secretos revelados. Encontro ou confissão inesperada.",
            "magic": "Adivinhação, profecia, revelação de segredos, trabalho com o destino.",
            "meaning": "Destino, conhecimento oculto, mistério. Algo escondido está prestes a ser revelado. Sorte em jogos e adivinhação. Confie no fluxo do destino.",
            "name": "Perthro",
            "reversed_meaning": "Segredos revelados na hora errada. Estagnação, decepção em previsões. Não tente controlar o destino."
        },
        "raido": {
            "as_amulet": "Para viagens seguras e encontrar o caminho certo na vida.",
            "career": "Viagens a trabalho, mudança por motivo profissional. Crescimento na carreira através do movimento.",
            "deity": "Thor",
            "health": "Um estilo de vida ativo é benéfico. Caminhadas e viagens curam.",
            "keyword": "Jornada",
            "love": "Uma viagem conjunta fortalecerá o relacionamento. Nova fase para o casal.",
            "magic": "Proteção durante a viagem, busca pela direção certa, jornada espiritual.",
            "meaning": "Jornada — física ou espiritual. Movimento para frente, progresso, ritmo da vida. A direção correta foi escolhida — continue.",
            "name": "Raido",
            "reversed_meaning": "Estagnação, atrasos na viagem, rota errada. Reconsidere planos de viagem. Inquietação interior."
        },
        "sowilo": {
            "as_amulet": "Para vitória, sucesso e preenchimento com energia vital.",
            "career": "Triunfo, prêmios, reconhecimento público. Sua hora de glória.",
            "deity": "Baldr",
            "health": "Vitamina D, sol, energia. Excelente bem-estar.",
            "keyword": "Sol",
            "love": "Período brilhante e alegre nos relacionamentos. O amor brilha.",
            "magic": "Vitória sobre a escuridão, cura, preenchimento com energia solar.",
            "meaning": "Sol, vitória, força vital. Integridade e sucesso. A luz dissipa a escuridão. Tempo de triunfo e plenitude de energia.",
            "name": "Sowilo"
        },
        "thurisaz": {
            "as_amulet": "Proteção contra inimigos e influências negativas. Superando obstáculos.",
            "career": "Avanço através de obstáculos. Mas tenha cuidado com conflitos.",
            "deity": "Thor",
            "health": "Condições agudas. Não adie a consulta médica.",
            "keyword": "Portal",
            "love": "Período apaixonado, mas perigoso. Não pressione seu parceiro. Proteja os limites.",
            "magic": "Proteção poderosa, destruindo influências hostis, abrindo caminhos.",
            "meaning": "Proteção e quebra de barreiras. Força poderosa que requer controle. Você está diante de um portal — sua decisão muda tudo. Aja conscientemente.",
            "name": "Thurisaz",
            "reversed_meaning": "Vulnerabilidade, decisões precipitadas, perigo. Não aja impulsivamente. Inimigos ocultos estão próximos."
        },
        "tiwaz": {
            "as_amulet": "Para vitória, justiça e força masculina.",
            "career": "Vitória competitiva. Questões legais resolvidas a seu favor.",
            "deity": "Tyr",
            "health": "Braços, lado direito do corpo. Saúde masculina.",
            "keyword": "Guerreiro",
            "love": "Honestidade nos relacionamentos. Sacrifício por amor. Energia masculina.",
            "magic": "Vitória em disputas, justiça, proteção do guerreiro.",
            "meaning": "Justiça, honra, coragem, vitória em uma causa justa. A lei está ao seu lado. O sacrifício por um propósito superior é justificado.",
            "name": "Tiwaz",
            "reversed_meaning": "Injustiça, derrota, traição. Sacrifício em vão. Questões legais não a seu favor."
        },
        "uruz": {
            "as_amulet": "Para saúde, força física e recuperação de doenças.",
            "career": "Avanço através da persistência. O esforço físico é recompensado.",
            "deity": "Thor",
            "health": "Saúde forte, recuperação rápida. Pratique esportes.",
            "keyword": "Força",
            "love": "Relacionamentos apaixonados e fortes. Atração física. Superação de dificuldades juntos.",
            "magic": "Cura, fortalecimento do corpo e espírito, obtenção de poder interior.",
            "meaning": "Força primal e saúde. Resistência física e mental no auge. Superação de obstáculos através da persistência. Hora de agir, não esperar.",
            "name": "Uruz",
            "reversed_meaning": "Fraqueza, doença, oportunidades perdidas. Você está desperdiçando energia. Pare e restaure suas forças."
        },
        "wunjo": {
            "as_amulet": "Para felicidade, alegria e realização de desejos.",
            "career": "Satisfação no trabalho. Reconhecimento dos colegas, atmosfera agradável.",
            "deity": "Odin",
            "health": "Bem-estar. Emoções positivas curam.",
            "keyword": "Alegria",
            "love": "Felicidade nos relacionamentos. Amor mútuo, período acolhedor.",
            "magic": "Atrair felicidade, realização de desejos, harmonização do espaço.",
            "meaning": "Alegria, felicidade, harmonia. Desejos se realizam. Período de satisfação e elevação emocional. Aproveite o momento.",
            "name": "Wunjo",
            "reversed_meaning": "Tristeza, crise, decepção. Alegria temporariamente indisponível. Reavaliação de valores."
        },
        "wyrd": {
            "as_amulet": "Não usado como amuleto — símbolo de aceitação do desconhecido.",
            "career": "Incerteza. O resultado não depende de você.",
            "deity": "Nornas",
            "health": "Situação incerta. Confie em um curador e em forças superiores.",
            "keyword": "Destino",
            "love": "O destino decidirá por você. Confie no fluxo.",
            "magic": "Rendição total ao destino. Meditação no vazio. Aceitação.",
            "meaning": "Runa em branco — destino puro. O incognoscível, intervenção divina. A situação está inteiramente nas mãos de forças superiores. Confie e aceite.",
            "name": "Wyrd"
        }
    },
    "tr": {
        "algiz": {
            "as_amulet": "Birincil koruyucu muska. Güvenlik ve himaye için takılır.",
            "career": "Rakiplerden ve entrikalardan koruma. Patronun himayesi.",
            "deity": "Heimdall",
            "health": "Bağışıklık güçlenmiştir. Vücut kendini korur.",
            "keyword": "Koruma",
            "love": "İlişkileri dış tehditlerden koruma. Partnerle manevi bağ.",
            "magic": "En güçlü koruyucu işaret. Her türlü negatifliğe karşı kalkan.",
            "meaning": "Güçlü ilahi koruma. Kendini koruma içgüdüsü keskinleşmiştir. Yüksek güçlerle manevi bağ güçlenir. Himaye altındasınız.",
            "name": "Algiz",
            "reversed_meaning": "Kırılganlık, gizli tehlike. Korumanız zayıflamıştır. Dikkatli olun."
        },
        "ansuz": {
            "as_amulet": "Bilgelik, sınav şansı, sezgi gelişimi için.",
            "career": "Mentorluk, müzakereler, topluluk önünde konuşma — sizin zamanınız.",
            "deity": "Odin",
            "health": "Boğaz, boyun, sinir sistemine dikkat edin.",
            "keyword": "Bilgelik",
            "love": "Derin bir konuşma ilişkileri netleştirecek. Partnerinizi dikkatlice dinleyin.",
            "magic": "Yüksek güçlerle bağlantı, hitabet geliştirme, bilgi edinme.",
            "meaning": "İlahi ilham ve bilgelik. Önemli bir mesaj alacaksınız — işaretlere dikkat edin. İletişim, öğrenme ve bilgi paylaşımı desteklenir.",
            "name": "Ansuz",
            "reversed_meaning": "Aldatma, manipülasyon, yanlış anlama. Birisi gerçeği çarpıtıyor. Tavsiyelere körü körüne güvenmeyin."
        },
        "berkano": {
            "as_amulet": "Hamilelik, annelik ve yumuşak yeni başlangıçlar için.",
            "career": "Yeni bir projenin doğuşu. Yumuşak ama istikrarlı büyüme.",
            "deity": "Frigg",
            "health": "Kadın sağlığı, üreme sistemi, annelik.",
            "keyword": "Huş",
            "love": "Hamilelik, düğün, duyguların doğuşu. Kadınsı enerji.",
            "magic": "Doğurganlık, anne koruması, yumuşak şifa.",
            "meaning": "Doğum, büyüme, doğurganlık, kadınlık. Yeni başlangıç, doğanın yumuşak gücü. Aile ve çocuklarla ilgilenmek desteklenir.",
            "name": "Berkano",
            "reversed_meaning": "Kısırlık, büyüme durgunluğu, aile çatışmaları. Bakım kontrole dönüşür."
        },
        "dagaz": {
            "as_amulet": "Yeni başlangıçlar, atılımlar ve hayata ışık çekmek için.",
            "career": "Kariyerde köklü dönüş. Yeni ufuklar açılıyor.",
            "deity": "Heimdall",
            "health": "İyileşme, kriz sonrası düzelme. Tünelin sonundaki ışık.",
            "keyword": "Şafak",
            "love": "İlişkilerde yeni bir şafak. Karanlıktan sonra — ışık. Bağışlama.",
            "magic": "Engelleri aşma, gerçekliğin dönüşümü, yeni başlangıç.",
            "meaning": "Atılım, şafak, dönüşüm. Arkada karanlık — önde ışık. Daha iyiye doğru köklü değişim. Aydınlanma ve umut.",
            "name": "Dagaz"
        },
        "ehwaz": {
            "as_amulet": "Hızlı ilerleme ve sadık bir müttefik bulma için.",
            "career": "Hızlı ilerleme, daha iyiye iş değişikliği, yer değiştirme.",
            "deity": "Freyr",
            "health": "Bacaklar, kalçalar. Binicilik ve spor faydalıdır.",
            "keyword": "At",
            "love": "Uyumlu birliktelik, birlikte ilerlemek. Güven güçlenir.",
            "magic": "Süreçleri hızlandırma, dünyalar arasında yolculuk, sadık müttefik.",
            "meaning": "Hareket, ilerleme, ortaklar arasında güven. Daha iyiye doğru hızlı değişimler. Sadık bir yol arkadaşı yakında. Takım çalışması.",
            "name": "Ehwaz",
            "reversed_meaning": "Durgunluk, güvensizlik, kopmuş bağlar. Yanlış yönde hareket."
        },
        "eihwaz": {
            "as_amulet": "Dayanıklılık, korunma ve atalarla bağlantı için.",
            "career": "Zor koşullarda dayanıklılık. Tecrübe sizin silahınızdır.",
            "deity": "Odin",
            "health": "Omurga, kemikler. Kas-iskelet sistemini güçlendirin.",
            "keyword": "Porsuk",
            "love": "İlişkilerde derin dönüşüm. Krizin birlikte üstesinden gelmek.",
            "magic": "Ölümden korunma, dünyalar arasında yolculuk, şamanik uygulamalar.",
            "meaning": "Dayanıklılık, dünyalar arası bağlantı, sınavlar yoluyla dönüşüm. Dünya Ağacı sizin desteğinizdir. Ölüm korkusunun üstesinden gelmek ve yeniden doğuş.",
            "name": "Eihwaz"
        },
        "fehu": {
            "as_amulet": "Para ve maddi refah çekmek için takın.",
            "career": "Finansal büyüme, terfi, yeni kârlı proje. Kararlı hareket edin.",
            "deity": "Freya",
            "health": "Enerji yükseliyor. Sağlığa yatırım yapın — sonuç gelecek.",
            "keyword": "Zenginlik",
            "love": "İlişkilerde cömertlik meyve verir. Ortak yatırımlar bağı güçlendirir.",
            "magic": "Zenginlik çekme, finansal akışı güçlendirme, mülk koruma.",
            "meaning": "Maddi refah ve bolluk. Yeni girişimler kâr getirir. Edinme ve büyüme enerjisi size doğru akar. Çabalarınızı yatırma zamanı.",
            "name": "Fehu",
            "reversed_meaning": "Finansal kayıplar, açgözlülük, durgunluk. Akılsız harcamalar veya bırakılması gerekeni tutmak. Maddi olana ilişkin tutumunuzu yeniden değerlendirin."
        },
        "gebo": {
            "as_amulet": "Aşk çekmek ve ortaklığı güçlendirmek için.",
            "career": "Kârlı ortaklık, sözleşme imzalama, kazan-kazan anlaşmaları.",
            "deity": "Odin",
            "health": "Vücut dengesi ve uyumu. Çift uygulamaları faydalıdır.",
            "keyword": "Hediye",
            "love": "İlişkiler için mükemmel zaman. Karşılıklılık ve uyum. Nişan mümkün.",
            "magic": "Aşk runesi, bağları güçlendirme, ilişkileri uyumlu hale getirme.",
            "meaning": "Hediye, ortaklık, eşit değişim. Cömertlik geri döner. Karşılıklı saygıya dayalı uyumlu ilişkiler. Anlaşmalar ve ittifaklar tercih edilir.",
            "name": "Gebo"
        },
        "hagalaz": {
            "as_amulet": "Elementlerden korunma ve negatif kalıpları yok etme için.",
            "career": "İşten çıkarılma, iflas, plan çöküşü. Ama bu yenisi için özgürleşmedir.",
            "deity": "Hel",
            "health": "Kronik hastalık alevlenmeleri. Sinir sistemine dikkat edin.",
            "keyword": "Dolu",
            "love": "İlişki krizi. Ama bunun aracılığıyla — yenilenme veya özgürleşme.",
            "magic": "Negatifliği yok etme, büyü bozma, köklü yenilenme.",
            "meaning": "Yıkım ve kaçınılmaz dönüşüm. Kontrolünüz dışındaki elementel değişimler. Eskiyi yok ederek yenisi doğar. Kabul edin ve uyum sağlayın.",
            "name": "Hagalaz"
        },
        "ingwaz": {
            "as_amulet": "Bereket, işleri tamamlama ve eril güç için.",
            "career": "Proje başarıyla tamamlandı. Yeni aşamadan önce hak edilmiş dinlenme.",
            "deity": "Freyr",
            "health": "Üreme sistemi. Dinlenme ve enerji yenileme.",
            "keyword": "Tohum",
            "love": "Döllenme, çiftte rahat dönem. Ev içi mutluluk.",
            "magic": "Bereket, ritüel tamamlama, büyülü güç biriktirme.",
            "meaning": "Bereket, döngü tamamlanması, iç huzur. Tohum ekildi — büyümesine izin ver. Atılım öncesi güç toplama dönemi.",
            "name": "Ingwaz"
        },
        "isa": {
            "as_amulet": "Huzur bulmak ve istenmeyen süreçleri durdurmak için.",
            "career": "Projeler donduruldu. Planlama için duraklamayı kullanın.",
            "deity": "Verdandi",
            "health": "Yavaşlamış süreçler. Dinlenme ve iyileşme gerekli.",
            "keyword": "Buz",
            "love": "Duyguların soğuması, ilişkide duraklama. Şimdi karar vermeyin.",
            "magic": "Bir durumu dondurma, düşmanca eylemleri durdurma, meditasyon.",
            "meaning": "Durgunluk, duraklama, içe dönüş. Her şey bir sebeple durdu — içsel çalışma zamanı. Acele etme. Durgunluk netlik getirir.",
            "name": "İsa"
        },
        "jera": {
            "as_amulet": "İyi hasat, iş başarısı ve adil sonuçlar için.",
            "career": "Hak edilmiş terfi, ikramiye ödemesi, proje tamamlama.",
            "deity": "Freyr",
            "health": "İyileşme, uzun tedavi sonrası düzelme.",
            "keyword": "Hasat",
            "love": "İlişkiler meyve verir. Ortak çabalar ödüllendirilir.",
            "magic": "Doğurganlığı çekme, iş başarısı, olumlu sonuç.",
            "meaning": "Hasat, çabanın ödülü, döngü tamamlanması. Ne ekersen onu biçersin. Adil sonuçlar. Doğanın döngüleri sizin için çalışır.",
            "name": "Jera"
        },
        "kenaz": {
            "as_amulet": "İlham, yeteneklerin açığa çıkarılması ve zihinsel berraklık için.",
            "career": "Yaratıcı atılım, yeni fikirler, öğrenme karşılığını verir.",
            "deity": "Freya",
            "health": "Enflamatuar süreçler. Sıcaklık ve ateşe dikkat edin.",
            "keyword": "Meşale",
            "love": "Tutku ve çekim. Yeni bir romantizm veya duyguların canlanması.",
            "magic": "Sırları açığa çıkarma, sezgiyi güçlendirme, yaratıcı ritüeller.",
            "meaning": "Bilginin ve yaratıcı ateşin ışığı. İçgörü, düşünce netliği, ilham. Yaratıcı projeler başarılı olur. Öğrenme ve yaratma zamanı.",
            "name": "Kenaz",
            "reversed_meaning": "Karanlık, cehalet, yaratıcı blok. İlham kaybı. Yanlış illüzyonlar zihni bulandırır."
        },
        "laguz": {
            "as_amulet": "Sezgi gelişimi, yaratıcılık ve dişi güç için.",
            "career": "Yaratıcı meslekler. Sezgisel kararlar doğrudur.",
            "deity": "Njord",
            "health": "Böbrekler, mesane, lenf. Daha fazla su için.",
            "keyword": "Su",
            "love": "Derin duygular, romantizm. Mantığa değil, hislere güvenin.",
            "magic": "Sezgiyi güçlendirme, rüya çalışması, su ritüelleri.",
            "meaning": "Akış, sezgi, bilinçaltı. Akıntıya güvenin — su yolunu bulur. Duygular ve rüyalar önemli mesajlar taşır. Dişi bilgelik.",
            "name": "Laguz",
            "reversed_meaning": "Korku, yanılsamalar, yolu kaybetme. Duygular boğar. İlk izlenime güvenmeyin."
        },
        "mannaz": {
            "as_amulet": "Zekâ gelişimi, kendini tanıma ve toplumla uyum için.",
            "career": "Takım çalışması, rehberlik. Zekân başarının anahtarıdır.",
            "deity": "Heimdall",
            "health": "Ruh sağlığı. Meditasyon ve kendini tanıma.",
            "keyword": "İnsan",
            "love": "Karşılıklı anlayış, entelektüel bağ. Birbirinizi tanımak.",
            "magic": "Zihni güçlendirme, kendini tanıma, kolektif bilinçle bağlantı.",
            "meaning": "Kendini tanıma, akıl, toplum. Sen daha büyük bir bütünün parçasısın. İçe dönme ve sosyal etkinlik zamanı. Yardım insanlardan gelecek.",
            "name": "Mannaz",
            "reversed_meaning": "Yalnızlık, bencillik, kendini kandırma. Dünyadan kendini soyutladın. Yardımı kabul et."
        },
        "nauthiz": {
            "as_amulet": "Sabır geliştirmek ve hayatın zorluklarını aşmak için.",
            "career": "İş yerinde kısıtlamalar. Sabır ödüllendirilecek. Başladığınızı bırakmayın.",
            "deity": "Skuld",
            "health": "Kısıtlayıcı diyet faydalıdır. Sertleşme ve çilecilik güçlendirir.",
            "keyword": "İhtiyaç",
            "love": "Yalnızlık veya ilişkilerde kısıtlamalar. Ama bu, kendini keşfetme zamanı.",
            "magic": "Engelleri aşma, sabır, kısıtlamalar yoluyla koruma.",
            "meaning": "Zorunluluk ve kısıtlamalar. Sabır ana aracınızdır. İhtiyaç yoluyla gerçek arzuların anlaşılması gelir. Çilecilik zamanı.",
            "name": "Nauthiz",
            "reversed_meaning": "Sabırsızlık, tembellik, hatalardan ders almayı reddetme. Gerekli derslere direniyorsunuz."
        },
        "othala": {
            "as_amulet": "Ev koruması, klan bağlantısı ve miras edinmek için.",
            "career": "Aile işi, miras, gayrimenkul işlemleri.",
            "deity": "Odin",
            "health": "Kalıtsal hastalıklar. Aile tıbbi geçmişini inceleyin.",
            "keyword": "Miras",
            "love": "Aile değerleri, 'ruh eşi'yle karşılaşma. Ev bir kaledir.",
            "magic": "Ev koruması, atalarla bağlantı, klan gücünü aktarma.",
            "meaning": "Ev, klan, atalar mirası. Köklerle bağlantı güç verir. Gayrimenkul, miras, aile değerleri. Klan bilgeliği size rehberlik eder.",
            "name": "Othala",
            "reversed_meaning": "Ev kaybı, klanla kopuş, yabancılaşma. Evsizlik, geleneklerin reddi."
        },
        "perthro": {
            "as_amulet": "Şans, sırları açığa çıkarma ve sezgiyi güçlendirme için.",
            "career": "Gizli fırsatlar ortaya çıkar. Yarışmalarda ve piyangolarda şans.",
            "deity": "Frigg",
            "health": "Gizli rahatsızlıklar. Tıbbi bir kontrol yaptırın.",
            "keyword": "Gizem",
            "love": "Gizli duygular açığa çıkar. Beklenmedik bir karşılaşma veya itiraf.",
            "magic": "Falcılık, kehanet, sırları açığa çıkarma, kaderle çalışma.",
            "meaning": "Kader, gizli bilgi, gizem. Saklı olan bir şey ortaya çıkmak üzere. Oyunlarda ve falcılıkta şans. Kaderin akışına güven.",
            "name": "Perthro",
            "reversed_meaning": "Sırlar yanlış zamanda açığa çıkar. Durgunluk, tahminlerde hayal kırıklığı. Kaderi kontrol etmeye çalışmayın."
        },
        "raido": {
            "as_amulet": "Güvenli seyahatler ve hayatta doğru yolu bulmak için.",
            "career": "İş seyahatleri, iş için taşınma. Hareket yoluyla kariyer büyümesi.",
            "deity": "Thor",
            "health": "Aktif yaşam tarzı faydalıdır. Yürüyüşler ve seyahatler iyileştirir.",
            "keyword": "Yolculuk",
            "love": "Birlikte bir yolculuk ilişkiyi güçlendirecek. Çift için yeni bir aşama.",
            "magic": "Yolda koruma, doğru yönü bulma, ruhsal yolculuk.",
            "meaning": "Yolculuk — fiziksel veya ruhsal. İleriye doğru hareket, ilerleme, yaşam ritmi. Doğru yön seçildi — devam edin.",
            "name": "Raido",
            "reversed_meaning": "Durgunluk, yolda gecikmeler, yanlış rota. Seyahat planlarınızı yeniden gözden geçirin. İç huzursuzluk."
        },
        "sowilo": {
            "as_amulet": "Zafer, başarı ve yaşam enerjisiyle dolma için.",
            "career": "Zafer, ödüller, halkın takdiri. En parlak anınız.",
            "deity": "Baldr",
            "health": "D vitamini, güneş, enerji. Mükemmel sağlık.",
            "keyword": "Güneş",
            "love": "Parlak, neşeli bir ilişki dönemi. Aşk parlar.",
            "magic": "Karanlığa karşı zafer, şifa, güneş enerjisiyle dolma.",
            "meaning": "Güneş, zafer, yaşam gücü. Bütünlük ve başarı. Işık karanlığı dağıtır. Zafer ve enerji doluluğu zamanı.",
            "name": "Sowilo"
        },
        "thurisaz": {
            "as_amulet": "Düşmanlardan ve olumsuz etkilerden korunma. Engelleri aşma.",
            "career": "Engelleri aşarak atılım. Ancak çatışmalara karşı dikkatli olun.",
            "deity": "Thor",
            "health": "Akut durumlar. Doktor ziyaretini ertelemeyin.",
            "keyword": "Geçit",
            "love": "Tutkulu ama tehlikeli bir dönem. Partnerinize baskı yapmayın. Sınırları koruyun.",
            "magic": "Güçlü koruma, düşman etkilerini yok etme, yolları açma.",
            "meaning": "Koruma ve engelleri yıkma. Kontrol gerektiren güçlü bir güç. Bir geçidin önünde duruyorsunuz — kararınız her şeyi değiştirecek. Bilinçli hareket edin.",
            "name": "Thurisaz",
            "reversed_meaning": "Kırılganlık, acele kararlar, tehlike. Dürtüsel hareket etmeyin. Gizli düşmanlar yakında."
        },
        "tiwaz": {
            "as_amulet": "Zafer, adalet ve eril güç için.",
            "career": "Rekabet zaferi. Yasal meseleler lehinize çözülür.",
            "deity": "Tyr",
            "health": "Kollar, vücudun sağ tarafı. Erkek sağlığı.",
            "keyword": "Savaşçı",
            "love": "İlişkilerde dürüstlük. Aşk için fedakârlık. Eril enerji.",
            "magic": "Tartışmalarda zafer, adalet, savaşçı koruması.",
            "meaning": "Adalet, onur, cesaret, haklı bir davada zafer. Kanun sizden yana. Daha yüksek bir amaç için fedakârlık haklıdır.",
            "name": "Tiwaz",
            "reversed_meaning": "Adaletsizlik, yenilgi, ihanet. Fedakârlık boşuna. Yasal meseleler lehinize değil."
        },
        "uruz": {
            "as_amulet": "Sağlık, fiziksel güç ve hastalıktan iyileşme için.",
            "career": "Azimle ilerleme. Fiziksel çaba ödüllendirilir.",
            "deity": "Thor",
            "health": "Güçlü sağlık, hızlı iyileşme. Spor yapın.",
            "keyword": "Güç",
            "love": "Tutkulu, güçlü ilişkiler. Fiziksel çekim. Birlikte zorlukların üstesinden gelmek.",
            "magic": "İyileşme, beden ve ruhu güçlendirme, içsel güç kazanma.",
            "meaning": "İlkel güç ve sağlık. Fiziksel ve zihinsel dayanıklılık zirvede. Engelleri azimle aşmak. Beklemek değil, harekete geçme zamanı.",
            "name": "Uruz",
            "reversed_meaning": "Zayıflık, hastalık, kaçırılmış fırsatlar. Enerjinizi boşa harcıyorsunuz. Durun ve gücünüzü yenileyin."
        },
        "wunjo": {
            "as_amulet": "Mutluluk, neşe ve dileklerin gerçekleşmesi için.",
            "career": "İş tatmini. Meslektaşlardan takdir, hoş bir atmosfer.",
            "deity": "Odin",
            "health": "İyi hissetme. Olumlu duygular iyileştirir.",
            "keyword": "Neşe",
            "love": "İlişkilerde mutluluk. Karşılıklı sevgi, sıcak bir dönem.",
            "magic": "Mutluluğu çekme, dileklerin gerçekleşmesi, mekan uyumlaştırması.",
            "meaning": "Neşe, mutluluk, uyum. Dilekler gerçekleşir. Tatmin ve duygusal yükseliş dönemi. Anın tadını çıkarın.",
            "name": "Wunjo",
            "reversed_meaning": "Üzüntü, kriz, hayal kırıklığı. Neşe geçici olarak ulaşılamaz. Değerlerin yeniden değerlendirilmesi."
        },
        "wyrd": {
            "as_amulet": "Muska olarak kullanılmaz — bilinmeyeni kabul etmenin sembolü.",
            "career": "Belirsizlik. Sonuç size bağlı değil.",
            "deity": "Nornlar",
            "health": "Net olmayan durum. Bir şifacıya ve yüksek güçlere güvenin.",
            "keyword": "Kader",
            "love": "Kader sizin için karar verecek. Akışa güvenin.",
            "magic": "Kadere tam teslimiyet. Boşluk üzerine meditasyon. Kabul.",
            "meaning": "Boş rune — saf kader. Bilinemez, ilahi müdahale. Durum tamamen yüksek güçlerin elinde. Güven ve kabul et.",
            "name": "Wyrd"
        }
    },
    "uk": {
        "algiz": {
            "as_amulet": "Головний захисний амулет. Носити для безпеки та заступництва.",
            "career": "Захист від конкурентів та інтриг. Заступництво начальства.",
            "deity": "Геймдалль",
            "health": "Імунітет зміцнений. Організм захищає себе.",
            "keyword": "Захист",
            "love": "Захист відносин від зовнішніх загроз. Духовний зв'язок з партнером.",
            "magic": "Найпотужніший захисний знак. Щит від будь-якого негативу.",
            "meaning": "Потужний божественний захист. Інстинкт самозбереження загострений. Духовний зв'язок з вищими силами зміцнюється. Ви під захистом.",
            "name": "Альгіз",
            "reversed_meaning": "Вразливість, прихована небезпека. Ваш захист ослаблений. Будьте пильні."
        },
        "ansuz": {
            "as_amulet": "Для мудрості, удачі на іспитах, розвитку інтуїції.",
            "career": "Наставництво, переговори, публічні виступи — ваш час.",
            "deity": "Одін",
            "health": "Зверніть увагу на горло, шию, нервову систему.",
            "keyword": "Мудрість",
            "love": "Глибока розмова прояснить стосунки. Слухайте партнера уважно.",
            "magic": "Зв'язок з вищими силами, розвиток красномовства, отримання знань.",
            "meaning": "Божественне натхнення та мудрість. Ви отримаєте важливе послання — будьте уважні до знаків. Спілкування, навчання та передача знань сприятливі.",
            "name": "Ансуз",
            "reversed_meaning": "Обман, маніпуляції, нерозуміння. Хтось спотворює правду. Не довіряйте сліпо порадам."
        },
        "berkano": {
            "as_amulet": "Для вагітності, материнства та м'якого нового початку.",
            "career": "Народження нового проекту. М'який, але впевнений ріст.",
            "deity": "Фрігг",
            "health": "Жіноче здоров'я, репродуктивна система, материнство.",
            "keyword": "Береза",
            "love": "Вагітність, весілля, народження почуттів. Жіноча енергія.",
            "magic": "Родючість, материнський захист, м'яке зцілення.",
            "meaning": "Народження, ріст, родючість, жіночність. Новий початок, м'яка сила природи. Турбота про сім'ю та дітей сприятлива.",
            "name": "Беркана",
            "reversed_meaning": "Безпліддя, застій у рості, сімейні конфлікти. Турбота перетворюється на контроль."
        },
        "dagaz": {
            "as_amulet": "Для нового початку, прориву та привернення світла в життя.",
            "career": "Кардинальний поворот кар'єри. Нові горизонти відкриваються.",
            "deity": "Геймдалль",
            "health": "Одужання, покращення після кризи. Світло в кінці тунелю.",
            "keyword": "Світанок",
            "love": "Новий світанок у стосунках. Після темряви — світло. Прощення.",
            "magic": "Прорив крізь блокування, трансформація реальності, новий початок.",
            "meaning": "Прорив, світанок, трансформація. Темрява позаду — попереду світло. Кардинальна зміна на краще. Просвітлення і надія.",
            "name": "Даґаз"
        },
        "ehwaz": {
            "as_amulet": "Для швидкого просування та знаходження вірного союзника.",
            "career": "Швидке просування, зміна роботи на краще, переїзд.",
            "deity": "Фрейр",
            "health": "Ноги, стегна. Кінні прогулянки та спорт корисні.",
            "keyword": "Кінь",
            "love": "Гармонійний союз, спільний рух уперед. Довіра зміцнюється.",
            "magic": "Прискорення процесів, подорож між світами, вірний союзник.",
            "meaning": "Рух, прогрес, довіра між партнерами. Швидкі зміни на краще. Вірний супутник поруч. Командна робота.",
            "name": "Еваз",
            "reversed_meaning": "Застій, недовіра, розрив зв'язків. Рух у неправильному напрямку."
        },
        "eihwaz": {
            "as_amulet": "Для стійкості, захисту та зв'язку з предками.",
            "career": "Стійкість у складних умовах. Досвід — ваша зброя.",
            "deity": "Одін",
            "health": "Хребет, кістки. Зміцнюйте опорно-руховий апарат.",
            "keyword": "Тис",
            "love": "Глибока трансформація стосунків. Подолання кризи разом.",
            "magic": "Захист від смерті, подорож між світами, шаманські практики.",
            "meaning": "Стійкість, зв'язок світів, трансформація через випробування. Світове дерево — ваша опора. Подолання страху смерті та переродження.",
            "name": "Ейваз"
        },
        "fehu": {
            "as_amulet": "Носити для привернення грошей та матеріального благополуччя.",
            "career": "Фінансове зростання, підвищення, новий прибутковий проект. Дійте рішуче.",
            "deity": "Фрейя",
            "health": "Енергія на підйомі. Вкладайте в здоров'я — результат буде.",
            "keyword": "Багатство",
            "love": "Щедрість у стосунках приносить плоди. Спільні вкладення зміцнюють союз.",
            "magic": "Привернення багатства, посилення фінансового потоку, захист майна.",
            "meaning": "Матеріальне благополуччя та процвітання. Нові починання приносять прибуток. Енергія придбання та зростання спрямована у ваш бік. Час інвестувати зусилля.",
            "name": "Феху",
            "reversed_meaning": "Фінансові втрати, жадібність, застій. Нерозумні витрати або утримання того, що пора відпустити. Перегляньте ставлення до матеріального."
        },
        "gebo": {
            "as_amulet": "Для привернення любові та зміцнення партнерства.",
            "career": "Вигідне партнерство, підписання контрактів, виграшні угоди.",
            "deity": "Одін",
            "health": "Баланс і гармонія тіла. Парні практики корисні.",
            "keyword": "Дар",
            "love": "Ідеальний час для відносин. Взаємність і гармонія. Можливі заручини.",
            "magic": "Приворотна руна, зміцнення зв'язків, гармонізація відносин.",
            "meaning": "Дар, партнерство, рівноцінний обмін. Щедрість повертається. Гармонійні відносини, засновані на взаємній повазі. Договори та союзи сприятливі.",
            "name": "Ґебо"
        },
        "hagalaz": {
            "as_amulet": "Для захисту від стихій та руйнування негативних програм.",
            "career": "Звільнення, банкрутство, крах планів. Але це звільнення для нового.",
            "deity": "Гель",
            "health": "Загострення хронічних хвороб. Зверніть увагу на нервову систему.",
            "keyword": "Град",
            "love": "Криза у стосунках. Але через неї — оновлення або звільнення.",
            "magic": "Руйнування негативу, зняття порчі, кардинальне оновлення.",
            "meaning": "Руйнування та неминуча трансформація. Стихійні зміни поза вашим контролем. Через руйнування старого народжується нове. Прийміть та адаптуйтесь.",
            "name": "Гагалаз"
        },
        "ingwaz": {
            "as_amulet": "Для плодючості, завершення справ і чоловічої сили.",
            "career": "Проєкт завершено успішно. Заслужений відпочинок перед новим етапом.",
            "deity": "Фрейр",
            "health": "Репродуктивна система. Відпочинок і відновлення сил.",
            "keyword": "Насіння",
            "love": "Зачаття, затишний період у парі. Домашнє щастя.",
            "magic": "Плодючість, завершення ритуалів, накопичення магічної сили.",
            "meaning": "Плодючість, завершення циклу, внутрішній спокій. Насіння посаджено — дайте йому прорости. Період накопичення сил перед проривом.",
            "name": "Інґваз"
        },
        "isa": {
            "as_amulet": "Для здобуття спокою та зупинки небажаних процесів.",
            "career": "Проєкти заморожені. Використайте паузу для планування.",
            "deity": "Верданді",
            "health": "Сповільнення процесів. Відпочинок і відновлення необхідні.",
            "keyword": "Лід",
            "love": "Охолодження почуттів, пауза у стосунках. Не приймайте рішень зараз.",
            "magic": "Заморозка ситуації, зупинка ворожих дій, медитація.",
            "meaning": "Завмирання, пауза, самоаналіз. Усе зупинилося недарма — це час внутрішньої роботи. Не поспішайте події. Спокій дає ясність.",
            "name": "Іса"
        },
        "jera": {
            "as_amulet": "Для хорошого врожаю, успіху в справах та справедливого результату.",
            "career": "Заслужене підвищення, виплата бонусу, завершення проекту.",
            "deity": "Фрейр",
            "health": "Одужання, покращення після тривалого лікування.",
            "keyword": "Урожай",
            "love": "Відносини приносять плоди. Спільні зусилля винагороджені.",
            "magic": "Привернення родючості, успіх у справах, сприятливий результат.",
            "meaning": "Урожай, винагорода за працю, завершення циклу. Ви пожинаєте те, що посіяли. Справедливий результат. Цикли природи працюють на вас.",
            "name": "Йера"
        },
        "kenaz": {
            "as_amulet": "Для натхнення, розкриття талантів та ясності розуму.",
            "career": "Творчий прорив, нові ідеї, навчання приносить плоди.",
            "deity": "Фрейя",
            "health": "Запальні процеси. Увага до температури та лихоманки.",
            "keyword": "Факел",
            "love": "Пристрасть і потяг. Новий роман або відродження почуттів.",
            "magic": "Розкриття таємниць, посилення інтуїції, творчі ритуали.",
            "meaning": "Світло знання та творчого вогню. Прозріння, ясність думки, натхнення. Творчі проекти вдаються. Час вчитися і творити.",
            "name": "Кеназ",
            "reversed_meaning": "Темрява, невігластво, творчий блок. Втрата натхнення. Хибні ілюзії затьмарюють розум."
        },
        "laguz": {
            "as_amulet": "Для розвитку інтуїції, творчості та жіночої сили.",
            "career": "Творчі професії. Інтуїтивні рішення правильні.",
            "deity": "Ньйорд",
            "health": "Нирки, сечовий міхур, лімфа. Пийте більше води.",
            "keyword": "Вода",
            "love": "Глибокі емоції, романтика. Довіртеся почуттям, а не логіці.",
            "magic": "Посилення інтуїції, робота зі снами, водні ритуали.",
            "meaning": "Потік, інтуїція, підсвідомість. Довіртеся течії — вода знайде шлях. Емоції та сни несуть важливі послання. Жіноча мудрість.",
            "name": "Лагуз",
            "reversed_meaning": "Страх, ілюзії, втрата шляху. Емоції захльостують. Не довіряйте першому враженню."
        },
        "mannaz": {
            "as_amulet": "Для розвитку інтелекту, самопізнання та гармонії з суспільством.",
            "career": "Командна робота, наставництво. Ваш інтелект — ключ до успіху.",
            "deity": "Геймдалль",
            "health": "Психічне здоров'я. Медитація та самопізнання.",
            "keyword": "Людина",
            "love": "Взаєморозуміння, інтелектуальний зв'язок. Пізнання одне одного.",
            "magic": "Посилення розуму, самопізнання, зв'язок із колективною свідомістю.",
            "meaning": "Самопізнання, розум, суспільство. Ви — частина більшого цілого. Час для самоаналізу та соціальної активності. Допомога прийде від людей.",
            "name": "Манназ",
            "reversed_meaning": "Самотність, егоїзм, самообман. Ви відгородилися від світу. Прийміть допомогу."
        },
        "nauthiz": {
            "as_amulet": "Для розвитку терпіння та подолання життєвих труднощів.",
            "career": "Обмеження на роботі. Терпіння винагородиться. Не кидайте розпочате.",
            "deity": "Скульд",
            "health": "Обмежувальна дієта корисна. Загартування та аскеза зміцнюють.",
            "keyword": "Потреба",
            "love": "Самотність або обмеження в стосунках. Але це час для самопізнання.",
            "magic": "Подолання перешкод, терпіння, захист через обмеження.",
            "meaning": "Необхідність та обмеження. Терпіння — ваш головний інструмент. Через потребу приходить розуміння справжніх бажань. Час аскези.",
            "name": "Наутіз",
            "reversed_meaning": "Нетерпіння, лінь, відмова вчитися на помилках. Ви чините опір необхідним урокам."
        },
        "othala": {
            "as_amulet": "Для захисту дому, зв'язку з родом та здобуття спадщини.",
            "career": "Сімейний бізнес, спадок, угоди з нерухомістю.",
            "deity": "Одін",
            "health": "Спадкові захворювання. Вивчіть сімейну історію хвороб.",
            "keyword": "Спадщина",
            "love": "Сімейні цінності, зустріч з «родинною душею». Дім — фортеця.",
            "magic": "Захист дому, зв'язок з предками, передача родової сили.",
            "meaning": "Дім, рід, спадщина предків. Зв'язок з корінням дає силу. Нерухомість, спадок, сімейні цінності. Мудрість роду веде вас.",
            "name": "Отала",
            "reversed_meaning": "Втрата дому, розрив з родом, відчуження. Бездомність, відкидання традицій."
        },
        "perthro": {
            "as_amulet": "Для удачі, розкриття таємниць і посилення інтуїції.",
            "career": "Приховані можливості проявляються. Удача в конкурсах і лотереях.",
            "deity": "Фрігг",
            "health": "Приховані захворювання. Пройдіть обстеження.",
            "keyword": "Таємниця",
            "love": "Таємні почуття розкриваються. Несподівана зустріч або освідчення.",
            "magic": "Ворожіння, пророцтво, розкриття таємниць, робота з долею.",
            "meaning": "Доля, приховане знання, таємниця. Щось приховане ось-ось відкриється. Удача в іграх і ворожіннях. Довіряйте потоку долі.",
            "name": "Пертро",
            "reversed_meaning": "Секрети розкриваються не вчасно. Застій, розчарування в передбаченнях. Не намагайтеся контролювати долю."
        },
        "raido": {
            "as_amulet": "Для безпечних подорожей та знаходження правильного шляху в житті.",
            "career": "Відрядження, переїзд заради роботи. Кар'єрний ріст через рух.",
            "deity": "Тор",
            "health": "Активний спосіб життя корисний. Прогулянки та подорожі лікують.",
            "keyword": "Подорож",
            "love": "Спільна подорож зміцнить стосунки. Новий етап для пари.",
            "magic": "Захист у дорозі, пошук правильного напрямку, духовна мандрівка.",
            "meaning": "Подорож — фізична або духовна. Рух вперед, прогрес, ритм життя. Правильний напрямок обрано — продовжуйте.",
            "name": "Райдо",
            "reversed_meaning": "Застій, затримки в дорозі, неправильний маршрут. Перегляньте плани подорожей. Внутрішнє занепокоєння."
        },
        "sowilo": {
            "as_amulet": "Для перемоги, успіху та наповнення життєвою енергією.",
            "career": "Тріумф, нагороди, публічне визнання. Ваша зоряна година.",
            "deity": "Бальдр",
            "health": "Вітамін D, сонце, енергія. Чудове самопочуття.",
            "keyword": "Сонце",
            "love": "Яскравий, радісний період у стосунках. Любов сяє.",
            "magic": "Перемога над темрявою, зцілення, наповнення сонячною енергією.",
            "meaning": "Сонце, перемога, життєва сила. Цілісність та успіх. Світло розвіює темряву. Час тріумфу та наповненості енергією.",
            "name": "Совіло"
        },
        "thurisaz": {
            "as_amulet": "Захист від ворогів і негативних впливів. Подолання перешкод.",
            "career": "Прорив через перешкоди. Але будьте обережні з конфліктами.",
            "deity": "Тор",
            "health": "Гострі стани. Не відкладайте візит до лікаря.",
            "keyword": "Ворота",
            "love": "Пристрасний, але небезпечний період. Не тисніть на партнера. Захистіть кордони.",
            "magic": "Потужний захист, руйнування ворожих впливів, відкриття шляхів.",
            "meaning": "Захист і руйнування перешкод. Потужна сила, що потребує контролю. Ви стоїте перед воротами — рішення змінить усе. Дійте усвідомлено.",
            "name": "Турісаз",
            "reversed_meaning": "Вразливість, поспішні рішення, небезпека. Не дійте імпульсивно. Приховані вороги поруч."
        },
        "tiwaz": {
            "as_amulet": "Для перемоги, справедливості та чоловічої сили.",
            "career": "Перемога в конкурентній боротьбі. Судові справи вирішуються на вашу користь.",
            "deity": "Тюр",
            "health": "Руки, права сторона тіла. Чоловіче здоров'я.",
            "keyword": "Воїн",
            "love": "Чесність у стосунках. Жертва заради любові. Чоловіче начало.",
            "magic": "Перемога в суперечках, справедливість, захист воїна.",
            "meaning": "Справедливість, честь, мужність, перемога у правій справі. Закон на вашому боці. Жертва заради вищої мети виправдана.",
            "name": "Тіваз",
            "reversed_meaning": "Несправедливість, поразка, зрада. Жертва марна. Судові справи не на вашу користь."
        },
        "uruz": {
            "as_amulet": "Для здоров'я, фізичної сили та відновлення після хвороби.",
            "career": "Просування через наполегливість. Фізична праця винагороджується.",
            "deity": "Тор",
            "health": "Міцне здоров'я, швидке відновлення. Займіться спортом.",
            "keyword": "Сила",
            "love": "Пристрасні, сильні стосунки. Фізичний потяг. Спільне подолання труднощів.",
            "magic": "Зцілення, зміцнення тіла та духу, набуття внутрішньої сили.",
            "meaning": "Первісна сила та здоров'я. Фізична та ментальна витривалість на піку. Подолання перешкод через наполегливість. Час діяти, а не чекати.",
            "name": "Уруз",
            "reversed_meaning": "Слабкість, хвороба, втрачені можливості. Ви витрачаєте енергію марно. Зупиніться та відновіть сили."
        },
        "wunjo": {
            "as_amulet": "Для щастя, радості та виконання бажань.",
            "career": "Задоволення від роботи. Визнання колег, приємна атмосфера.",
            "deity": "Одін",
            "health": "Хороше самопочуття. Позитивні емоції лікують.",
            "keyword": "Радість",
            "love": "Щастя в стосунках. Взаємна любов, теплий період.",
            "magic": "Притягнення щастя, виконання бажань, гармонізація простору.",
            "meaning": "Радість, щастя, гармонія. Бажання здійснюються. Період задоволення та емоційного піднесення. Насолоджуйтесь моментом.",
            "name": "Вуньо",
            "reversed_meaning": "Смуток, криза, розчарування. Радість тимчасово недоступна. Переоцінка цінностей."
        },
        "wyrd": {
            "as_amulet": "Не використовується як амулет — символ прийняття невідомого.",
            "career": "Невизначеність. Результат залежить не від вас.",
            "deity": "Норни",
            "health": "Неясна ситуація. Покладіться на цілителя та вищі сили.",
            "keyword": "Доля",
            "love": "Доля вирішить за вас. Довіртеся потоку.",
            "magic": "Повна віддача долі. Медитація на порожнечу. Прийняття.",
            "meaning": "Порожня руна — чиста доля. Непізнаване, божественне втручання. Ситуація повністю в руках вищих сил. Довіртеся та прийміть.",
            "name": "Вирд"
        }
    }
}
SPREADS_RUNES_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "relationship": {
            "desc": "Tirada de pareja",
            "name": "Relación",
            "positions_0": "Tú",
            "positions_1": "Pareja",
            "positions_2": "Vínculo",
            "positions_3": "Obstáculo",
            "positions_4": "Resultado"
        },
        "rune_of_day": {
            "desc": "Una runa — el mensaje de hoy",
            "name": "Runa del día",
            "positions_0": "Mensaje del día"
        },
        "runic_cross": {
            "desc": "Análisis profundo de la situación",
            "name": "Cruz rúnica",
            "positions_0": "Situación",
            "positions_1": "Pasado",
            "positions_2": "Futuro",
            "positions_3": "Ayuda",
            "positions_4": "Obstáculo"
        },
        "three_norns": {
            "desc": "Pasado, Presente, Futuro",
            "name": "Tres Nornas",
            "positions_0": "Urd (Pasado)",
            "positions_1": "Verdandi (Presente)",
            "positions_2": "Skuld (Futuro)"
        },
        "year_spread": {
            "desc": "12 meses + runa del año",
            "name": "Tirada del año",
            "positions_0": "Enero",
            "positions_1": "Febrero",
            "positions_10": "Noviembre",
            "positions_11": "Diciembre",
            "positions_12": "Runa del año",
            "positions_2": "Marzo",
            "positions_3": "Abril",
            "positions_4": "Mayo",
            "positions_5": "Junio",
            "positions_6": "Julio",
            "positions_7": "Agosto",
            "positions_8": "Septiembre",
            "positions_9": "Octubre"
        },
        "yes_no": {
            "desc": "Respuesta a una pregunta directa",
            "name": "Sí / No",
            "positions_0": "Runa 1",
            "positions_1": "Runa 2",
            "positions_2": "Runa 3"
        },
        "yggdrasil": {
            "desc": "9 mundos del Árbol del Mundo",
            "name": "Yggdrasil",
            "positions_0": "Asgard (superior)",
            "positions_1": "Midgard (realidad)",
            "positions_2": "Helheim (oculto)",
            "positions_3": "Mente",
            "positions_4": "Corazón",
            "positions_5": "Cuerpo",
            "positions_6": "Pasado",
            "positions_7": "Presente",
            "positions_8": "Futuro"
        }
    },
    "pt": {
        "relationship": {
            "desc": "Jogo para casal",
            "name": "Relacionamento",
            "positions_0": "Você",
            "positions_1": "Parceiro",
            "positions_2": "Vínculo",
            "positions_3": "Obstáculo",
            "positions_4": "Resultado"
        },
        "rune_of_day": {
            "desc": "Uma runa — a mensagem de hoje",
            "name": "Runa do Dia",
            "positions_0": "Mensagem do Dia"
        },
        "runic_cross": {
            "desc": "Análise profunda da situação",
            "name": "Cruz Rúnica",
            "positions_0": "Situação",
            "positions_1": "Passado",
            "positions_2": "Futuro",
            "positions_3": "Ajuda",
            "positions_4": "Obstáculo"
        },
        "three_norns": {
            "desc": "Passado, Presente, Futuro",
            "name": "Três Nornes",
            "positions_0": "Urd (Passado)",
            "positions_1": "Verdandi (Presente)",
            "positions_2": "Skuld (Futuro)"
        },
        "year_spread": {
            "desc": "12 meses + runa do ano",
            "name": "Tiragem do Ano",
            "positions_0": "Janeiro",
            "positions_1": "Fevereiro",
            "positions_10": "Novembro",
            "positions_11": "Dezembro",
            "positions_12": "Runa do ano",
            "positions_2": "Março",
            "positions_3": "Abril",
            "positions_4": "Maio",
            "positions_5": "Junho",
            "positions_6": "Julho",
            "positions_7": "Agosto",
            "positions_8": "Setembro",
            "positions_9": "Outubro"
        },
        "yes_no": {
            "desc": "Resposta a uma pergunta direta",
            "name": "Sim / Não",
            "positions_0": "Runa 1",
            "positions_1": "Runa 2",
            "positions_2": "Runa 3"
        },
        "yggdrasil": {
            "desc": "9 mundos da Árvore do Mundo",
            "name": "Yggdrasil",
            "positions_0": "Asgard (superior)",
            "positions_1": "Midgard (realidade)",
            "positions_2": "Helheim (oculto)",
            "positions_3": "Mente",
            "positions_4": "Coração",
            "positions_5": "Corpo",
            "positions_6": "Passado",
            "positions_7": "Presente",
            "positions_8": "Futuro"
        }
    },
    "tr": {
        "relationship": {
            "desc": "Çift yayılımı",
            "name": "İlişki",
            "positions_0": "Sen",
            "positions_1": "Partner",
            "positions_2": "Bağ",
            "positions_3": "Engel",
            "positions_4": "Sonuç"
        },
        "rune_of_day": {
            "desc": "Bir rün — bugünün mesajı",
            "name": "Günün Rünü",
            "positions_0": "Günün mesajı"
        },
        "runic_cross": {
            "desc": "Derin durum analizi",
            "name": "Runik Haç",
            "positions_0": "Durum",
            "positions_1": "Geçmiş",
            "positions_2": "Gelecek",
            "positions_3": "Yardım",
            "positions_4": "Engel"
        },
        "three_norns": {
            "desc": "Geçmiş, Şimdi, Gelecek",
            "name": "Üç Norn",
            "positions_0": "Urd (Geçmiş)",
            "positions_1": "Verdandi (Şimdi)",
            "positions_2": "Skuld (Gelecek)"
        },
        "year_spread": {
            "desc": "12 ay + yıl runu",
            "name": "Yıl Açılımı",
            "positions_0": "Ocak",
            "positions_1": "Şubat",
            "positions_10": "Kasım",
            "positions_11": "Aralık",
            "positions_12": "Yıl runu",
            "positions_2": "Mart",
            "positions_3": "Nisan",
            "positions_4": "Mayıs",
            "positions_5": "Haziran",
            "positions_6": "Temmuz",
            "positions_7": "Ağustos",
            "positions_8": "Eylül",
            "positions_9": "Ekim"
        },
        "yes_no": {
            "desc": "Doğrudan bir soruya cevap",
            "name": "Evet / Hayır",
            "positions_0": "Rün 1",
            "positions_1": "Rün 2",
            "positions_2": "Rün 3"
        },
        "yggdrasil": {
            "desc": "9 dünya Dünya Ağacı'nın",
            "name": "Yggdrasil",
            "positions_0": "Asgard (yüksek)",
            "positions_1": "Midgard (gerçeklik)",
            "positions_2": "Helheim (gizli)",
            "positions_3": "Zihin",
            "positions_4": "Kalp",
            "positions_5": "Beden",
            "positions_6": "Geçmiş",
            "positions_7": "Şimdi",
            "positions_8": "Gelecek"
        }
    },
    "uk": {
        "relationship": {
            "desc": "Розклад на пару",
            "name": "Відносини",
            "positions_0": "Ти",
            "positions_1": "Партнер",
            "positions_2": "Зв'язок",
            "positions_3": "Перешкода",
            "positions_4": "Підсумок"
        },
        "rune_of_day": {
            "desc": "Одна руна — послання на сьогодні",
            "name": "Руна дня",
            "positions_0": "Послання дня"
        },
        "runic_cross": {
            "desc": "Глибокий аналіз ситуації",
            "name": "Рунічний хрест",
            "positions_0": "Ситуація",
            "positions_1": "Минуле",
            "positions_2": "Майбутнє",
            "positions_3": "Допомога",
            "positions_4": "Перешкода"
        },
        "three_norns": {
            "desc": "Минуле, Теперішнє, Майбутнє",
            "name": "Три Норни",
            "positions_0": "Урд (Минуле)",
            "positions_1": "Верданді (Теперішнє)",
            "positions_2": "Скульд (Майбутнє)"
        },
        "year_spread": {
            "desc": "12 місяців + руна року",
            "name": "Розклад на рік",
            "positions_0": "Січень",
            "positions_1": "Лютий",
            "positions_10": "Листопад",
            "positions_11": "Грудень",
            "positions_12": "Руна року",
            "positions_2": "Березень",
            "positions_3": "Квітень",
            "positions_4": "Травень",
            "positions_5": "Червень",
            "positions_6": "Липень",
            "positions_7": "Серпень",
            "positions_8": "Вересень",
            "positions_9": "Жовтень"
        },
        "yes_no": {
            "desc": "Відповідь на пряме запитання",
            "name": "Так / Ні",
            "positions_0": "Руна 1",
            "positions_1": "Руна 2",
            "positions_2": "Руна 3"
        },
        "yggdrasil": {
            "desc": "9 світів Світового Дерева",
            "name": "Іггдрасиль",
            "positions_0": "Асґард (вищий)",
            "positions_1": "Мідґард (реальність)",
            "positions_2": "Гельгейм (приховане)",
            "positions_3": "Розум",
            "positions_4": "Серце",
            "positions_5": "Тіло",
            "positions_6": "Минуле",
            "positions_7": "Теперішнє",
            "positions_8": "Майбутнє"
        }
    }
}
STAVES_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "clarity": {
            "description": "Ansuz otorga la sabiduría de Odín, Kenaz ilumina el camino del conocimiento, Mannaz potencia la mente y el autoconocimiento.",
            "how_to_use": "Dibújalo antes de un examen, una decisión importante o una negociación.",
            "name": "Stave de Claridad",
            "purpose": "Claridad mental y decisiones correctas"
        },
        "fertility": {
            "description": "Berkano — runa de la maternidad, Ingwaz — semilla de la vida, Jera — ciclo natural de fertilidad.",
            "how_to_use": "Dibuje en el cuerpo o coloque debajo de la almohada. Active en Luna creciente.",
            "name": "Stave de Fertilidad",
            "purpose": "Fertilidad, concepción, crecimiento"
        },
        "health": {
            "description": "Berkano proporciona una curación suave y regeneración, Uruz llena de fuerza primordial, Sowilo carga con energía vital solar.",
            "how_to_use": "Dibuja en el cuerpo (marcador seguro) en el área de preocupación. O en papel debajo de la almohada.",
            "name": "Stave de Salud",
            "purpose": "Curación y fortalecimiento de la salud"
        },
        "home_protection": {
            "description": "Othala guarda el hogar, Algiz protege los límites del hogar, Berkano protege a la familia.",
            "how_to_use": "Dibujar en el marco de la puerta o tallar en una tabla de madera en la entrada.",
            "name": "Protección del hogar",
            "purpose": "Protección del hogar y la familia"
        },
        "love": {
            "description": "Gebo crea un intercambio equitativo de energía, Wunjo trae alegría y felicidad, Kenaz enciende el fuego de la pasión.",
            "how_to_use": "Dibuje en papel rosa el viernes (día de Freya). Llévelo consigo en las citas.",
            "name": "Establo de Amor",
            "purpose": "Atraer amor y armonía en las relaciones"
        },
        "luck": {
            "description": "Sowilo ilumina el camino hacia el éxito, Fehu atrae bienes materiales, Wunjo garantiza alegría del resultado.",
            "how_to_use": "Dibuja en tu mano derecha antes de un evento importante. Visualiza el éxito.",
            "name": "Estaca de la Suerte",
            "purpose": "Atraer suerte y circunstancias favorables"
        },
        "new_beginning": {
            "description": "Dagaz abre las puertas de un nuevo amanecer, Fehu trae recursos para el inicio, Kenaz enciende el fuego de la inspiración.",
            "how_to_use": "Dibuja el día de una nueva empresa. Quema el papel con la estaca después de la activación.",
            "name": "Estaca del Nuevo Comienzo",
            "purpose": "Lanzamiento de una nueva fase de la vida"
        },
        "protection": {
            "description": "Una de las estacas protectoras más poderosas. Algiz crea un escudo divino, Tiwaz otorga fuerza de guerrero, Thurisaz destruye ataques hostiles. Juntos forman una barrera impenetrable.",
            "how_to_use": "Dibuje en papel o madera. Llévelo consigo o cuélguelo sobre la puerta principal. Actívelo con la respiración y la intención.",
            "name": "Estaca de Protección",
            "purpose": "Protección contra influencias negativas, enemigos y maldiciones"
        },
        "transformation": {
            "description": "Eihwaz conecta con el Árbol del Mundo, Hagalaz destruye lo viejo, Dagaz conduce a un nuevo amanecer. Poderosa fórmula de renacimiento.",
            "how_to_use": "Medita en la vara durante la Luna llena. Prepárate para cambios radicales.",
            "name": "Vara de Transformación",
            "purpose": "Transformación profunda y renacimiento"
        },
        "travel": {
            "description": "Raido asegura el camino correcto, Algiz protege en el camino, Ehwaz proporciona velocidad y compañ",
            "how_to_use": "Dibuje en el equipaje o en el pasaporte. Active antes de la salida.",
            "name": "Estaca de Viaje",
            "purpose": "Viajes seguros y suerte en el camino"
        },
        "victory": {
            "description": "Tiwaz da rectitud y justicia, Sowilo asegura el triunfo, Uruz llena de fuerza para la lucha.",
            "how_to_use": "Dibuje en la mano derecha antes de la competencia o el tribunal.",
            "name": "Estaca de la Victoria",
            "purpose": "Victoria en la competencia y asuntos legales"
        },
        "wealth": {
            "description": "Fehu abre el canal financiero, Sowilo llena con energía de éxito, Jera garantiza una cosecha justa. Fórmula clásica de prosperidad.",
            "how_to_use": "Dibújelo en su cartera o tarjeta bancaria. Renueve cada luna nueva.",
            "name": "Stave de la Riqueza",
            "purpose": "Atraer dinero y flujo financiero"
        }
    },
    "pt": {
        "clarity": {
            "description": "Ansuz concede a sabedoria de Odin, Kenaz ilumina o caminho do conhecimento, Mannaz aprimora a mente e o autoconhecimento.",
            "how_to_use": "Desenhe antes de um exame, decisão importante ou negociações.",
            "name": "Estaca da Clareza",
            "purpose": "Clareza mental e decisões corretas"
        },
        "fertility": {
            "description": "Berkano — runa da maternidade, Ingwaz — semente da vida, Jera — ciclo natural de fertilidade.",
            "how_to_use": "Desenhe no corpo ou coloque debaixo do travesseiro. Ative na Lua crescente.",
            "name": "Stave da Fertilidade",
            "purpose": "Fertilidade, concepção, crescimento"
        },
        "health": {
            "description": "Berkano proporciona cura suave e regeneração, Uruz preenche com força primordial, Sowilo carrega com energia solar da vida.",
            "how_to_use": "Desenhe no corpo (marcador seguro) na área de preocupação. Ou em papel debaixo do travesseiro.",
            "name": "Estave de Saúde",
            "purpose": "Cura e fortalecimento da saúde"
        },
        "home_protection": {
            "description": "Othala guarda o lar, Algiz escuda as fronteiras da casa, Berkano protege a família.",
            "how_to_use": "Desenhe no batente da porta ou entalhe em uma placa de madeira na entrada.",
            "name": "Proteção do Lar",
            "purpose": "Proteção do lar e da família"
        },
        "love": {
            "description": "Gebo cria uma troca igual de energia, Wunjo traz alegria e felicidade, Kenaz acende o fogo da paixão.",
            "how_to_use": "Desenhe em papel rosa na sexta-feira (dia de Freya). Carregue consigo em encontros.",
            "name": "Stave do Amor",
            "purpose": "Atrair amor e harmonia nos relacionamentos"
        },
        "luck": {
            "description": "Sowilo ilumina o caminho para o sucesso, Fehu atrai bens materiais, Wunjo garante alegria pelo resultado.",
            "how_to_use": "Desenhe na mão direita antes de um evento importante. Visualize o sucesso.",
            "name": "Став da Sorte",
            "purpose": "Atrair sorte e circunstâncias favoráveis"
        },
        "new_beginning": {
            "description": "Dagaz abre os portões de um novo amanhecer, Fehu traz recursos para o início, Kenaz acende o fogo da inspiração.",
            "how_to_use": "Desenhe no dia de um novo empreendimento. Queime o papel com o stave após a ativação.",
            "name": "Stave de Novo Começo",
            "purpose": "Lançando uma nova fase da vida"
        },
        "protection": {
            "description": "Um dos estaves de proteção mais poderosos. Algiz cria um escudo divino, Tiwaz dá força de guerreiro, Thurisaz destrói ataques hostis. Juntos formam uma barreira impenetrável.",
            "how_to_use": "Desenhe em papel ou madeira. Carregue consigo ou pendure acima da porta de entrada. Ative com respiração e intenção.",
            "name": "Estave de Proteção",
            "purpose": "Proteção contra influências negativas, inimigos e maldições"
        },
        "transformation": {
            "description": "Eihwaz conecta com a Árvore do Mundo, Hagalaz destrói o velho, Dagaz leva a um novo amanhecer. Poderosa fórmula de renascimento.",
            "how_to_use": "Medite no bastão durante a Lua cheia. Esteja preparado para mudanças radicais.",
            "name": "Bastão da Transformação",
            "purpose": "Transformação profunda e renascimento"
        },
        "travel": {
            "description": "Raido garante o caminho certo, Algiz protege na estrada, Ehwaz proporciona velocidade e companheiros leais.",
            "how_to_use": "Desenhe na bagagem ou no passaporte. Ative antes da partida.",
            "name": "Bastão de Viagem",
            "purpose": "Viagens seguras e sorte na estrada"
        },
        "victory": {
            "description": "Tiwaz concede retidão e justiça, Sowilo assegura o triunfo, Uruz preenche com força para a batalha.",
            "how_to_use": "Desenhe na mão direita antes de uma competição ou tribunal.",
            "name": "Bastão da Vitória",
            "purpose": "Vitória em competição e questões legais"
        },
        "wealth": {
            "description": "Fehu abre o canal financeiro, Sowilo preenche com energia de sucesso, Jera garante colheita justa. Fórmula clássica de prosperidade.",
            "how_to_use": "Desenhe em sua carteira ou cartão bancário. Renove a cada lua nova.",
            "name": "Estaca da Riqueza",
            "purpose": "Atrair dinheiro e fluxo financeiro"
        }
    },
    "tr": {
        "clarity": {
            "description": "Ansuz, Odin'in bilgeliğini bahşeder, Kenaz bilgi yolunu aydınlatır, Mannaz zihni ve öz-bilgiyi güçlendirir.",
            "how_to_use": "Bir sınav, önemli bir karar veya müzakerelerden önce çizin.",
            "name": "Netlik Stave",
            "purpose": "Zihinsel netlik ve doğru kararlar"
        },
        "fertility": {
            "description": "Berkano — annelik runesi, Ingwaz — yaşam tohumu, Jera — doğal bereket döngüsü.",
            "how_to_use": "Vücuda çizin veya yastığın altına koyun. Büyüyen Ay'da etkinleştirin.",
            "name": "Bereket Asası",
            "purpose": "Bereket, gebe kalma, büyüme"
        },
        "health": {
            "description": "Berkano nazik iyileştirme ve yenilenme sağlar, Uruz ilkel güçle doldurur, Sowilo güneş yaşam enerjisiyle yükler.",
            "how_to_use": "Vücuda (güvenli bir kalemle) sorunlu bölgeye çizin. Veya yastığın altına koymak üzere kağıda çizin.",
            "name": "Sağlık Stavesi",
            "purpose": "İyileştirme ve sağlığı güçlendirme"
        },
        "home_protection": {
            "description": "Othala ocağı korur, Algiz evin sınırlarını kalkanla korur, Berkano aileyi korur.",
            "how_to_use": "Kapı pervazına çizin veya girişteki tahta bir levhaya oyun.",
            "name": "Ev Koruması",
            "purpose": "Ev ve ailenin korunması"
        },
        "love": {
            "description": "Gebo eşit enerji alışverişi yaratır, Wunjo neşe ve mutluluk getirir, Kenaz tutku ateşini yakar.",
            "how_to_use": "Cuma günü (Freya'nın günü) pembe kağıda çizin. Randevularda yanınızda taşıyın.",
            "name": "Aşk Runası",
            "purpose": "İlişkilerde aşk ve uyum çekmek"
        },
        "luck": {
            "description": "Sowilo başarıya giden yolu aydınlatır, Fehu maddi kazançları çeker, Wunjo sonuçtan duyulan sevinci garanti eder.",
            "how_to_use": "Önemli bir olaydan önce sağ elinize çizin. Başarıyı görselleştirin.",
            "name": "Став Удачи",
            "purpose": "Şans ve olumlu koşulları çekmek"
        },
        "new_beginning": {
            "description": "Dagaz yeni bir şafağın kapılarını açar, Fehu başlangıç için kaynakları getirir, Kenaz ilham ateşini yakar.",
            "how_to_use": "Yeni bir girişimin gününde çizin. Aktivasyonun ardından stave bulunan kağıdı yakın.",
            "name": "Yeni Başlangıç Stave",
            "purpose": "Yeni bir yaşam evresini başlatma"
        },
        "protection": {
            "description": "En güçlü koruyucu stavlardan biri. Algiz ilahi bir kalkan oluşturur, Tiwaz savaşçı gücü verir, Thurisaz düşmanca saldırıları yok eder. Birlikte geçilmez bir bariyer oluştururlar.",
            "how_to_use": "Kağıda veya tahtaya çizin. Yanınızda taşıyın veya ön kapının üstüne asın. Nefes ve niyetle etkinleştirin.",
            "name": "Koruma Stavesi",
            "purpose": "Kötü etkilerden, düşmanlardan ve büyülerden korunma"
        },
        "transformation": {
            "description": "Eihwaz, Dünya Ağacı ile bağlantı kurar, Hagalaz eskiyi yok eder, Dagaz yeni şafağa yönlendirir. Güçlü yeniden doğuş formülü.",
            "how_to_use": "Dolunayda stav üzerinde meditasyon yapın. Radikal değişikliklere hazır olun.",
            "name": "Dönüşüm Stavı",
            "purpose": "Derin dönüşüm ve yeniden doğuş"
        },
        "travel": {
            "description": "Raido doğru yolu sağlar, Algiz yolda korur, Ehwaz hız ve sadık yol arkadaşları verir.",
            "how_to_use": "Bavulun üzerine veya pasaporta çizin. Yola çıkmadan önce etkinleştirin.",
            "name": "Seyahat Asası",
            "purpose": "Güvenli seyahatler ve yolda şans"
        },
        "victory": {
            "description": "Tiwaz haklılık ve adalet verir, Sowilo zaferi sağlar, Uruz savaş için güç doldurur.",
            "how_to_use": "Yarışma veya mahkeme öncesinde sağ ele çizin.",
            "name": "Zafer Asası",
            "purpose": "Rekabet ve hukuki meselelerde zafer"
        },
        "wealth": {
            "description": "Fehu finansal kanalı açar, Sowilo başarı enerjisiyle doldurur, Jera adil hasadı garanti eder. Klasik refah formülü.",
            "how_to_use": "Cüzdanınıza veya banka kartınıza çizin. Her yeni ayda yenileyin.",
            "name": "Zenginlik Runası",
            "purpose": "Para ve finansal akışı çekmek"
        }
    },
    "uk": {
        "clarity": {
            "description": "Ансуз дарує мудрість Одіна, Кеназ освітлює шлях знання, Манназ посилює розум і самопізнання.",
            "how_to_use": "Намалюйте перед іспитом, важливим рішенням або переговорами.",
            "name": "Став Ясності",
            "purpose": "Ясність розуму та правильні рішення"
        },
        "fertility": {
            "description": "Беркана — руна материнства, Інґуз — насіння життя, Єра — природний цикл родючості.",
            "how_to_use": "Намалюйте на тілі або покладіть під подушку. Активуйте на зростаючому Місяці.",
            "name": "Став Родючості",
            "purpose": "Родючість, зачаття, ріст"
        },
        "health": {
            "description": "Беркана дає м'яке зцілення та регенерацію, Уруз наповнює первісною силою, Совіло заряджає сонячною енергією життя.",
            "how_to_use": "Намалюйте на тілі (безпечним маркером) в області занепокоєння. Або на папері під подушку.",
            "name": "Став Здоров'я",
            "purpose": "Зцілення та зміцнення здоров'я"
        },
        "home_protection": {
            "description": "Отала охороняє домашнє вогнище, Альгіз ставить щит на межах дому, Беркана оберігає сім'ю.",
            "how_to_use": "Намалюйте на дверному косяку або виріжте на дерев'яній дощечці біля входу.",
            "name": "Захист дому",
            "purpose": "Захист житла та сім'ї"
        },
        "love": {
            "description": "Гебо створює рівноцінний обмін енергією, Вуньо приносить радість і щастя, Кеназ запалює вогонь пристрасті.",
            "how_to_use": "Намалюйте на рожевому папері в п'ятницю (день Фрейї). Носіть із собою на побаченнях.",
            "name": "Став Любові",
            "purpose": "Привернення любові та гармонії у стосунках"
        },
        "luck": {
            "description": "Совіло освітлює шлях до успіху, Феху притягує матеріальні блага, Вуньо гарантує радість від результату.",
            "how_to_use": "Намалюйте на правій руці перед важливою подією. Візуалізуйте успіх.",
            "name": "Руна Удачі",
            "purpose": "Привернення удачі та сприятливих обставин"
        },
        "new_beginning": {
            "description": "Даґаз відкриває ворота нового світанку, Феху приносить ресурси для старту, Кеназ запалює вогонь натхнення.",
            "how_to_use": "Намалюйте в день нового починання. Спаліть папір зі ставом після активації.",
            "name": "Став Нового початку",
            "purpose": "Запуск нового етапу життя"
        },
        "protection": {
            "description": "Один із найпотужніших захисних ставів. Альгіз створює божественний щит, Тіваз дає силу воїна, Турісаз руйнує ворожі атаки. Разом вони формують непробивний бар'єр.",
            "how_to_use": "Намалюйте на папері або дереві. Носіть при собі або повісьте над вхідними дверима. Активуйте диханням та наміром.",
            "name": "Став Захисту",
            "purpose": "Захист від негативних впливів, ворогів та псування"
        },
        "transformation": {
            "description": "Ейваз пов'язує зі Світовим Древом, Хагалаз руйнує старе, Дагаз веде до нового світанку. Потужна формула переродження.",
            "how_to_use": "Медитуйте на став при повному Місяці. Будьте готові до кардинальних змін.",
            "name": "Став Трансформації",
            "purpose": "Глибока трансформація та переродження"
        },
        "travel": {
            "description": "Райдо забезпечує правильний шлях, Альгіз захищає в дорозі, Еваз дає швидкість і вірних супутників.",
            "how_to_use": "Намалюйте на чемодані або в паспорті. Активуйте перед виїздом.",
            "name": "Став Подорожі",
            "purpose": "Безпечні подорожі та удача в дорозі"
        },
        "victory": {
            "description": "Тіваз дає правоту та справедливість, Совіло забезпечує тріумф, Уруз наповнює силою для боротьби.",
            "how_to_use": "Намалюйте на правій руці перед змаганням або судом.",
            "name": "Став Перемоги",
            "purpose": "Перемога в конкуренції та судових справах"
        },
        "wealth": {
            "description": "Феху відкриває фінансовий канал, Совіло наповнює енергією успіху, Єра гарантує справедливий врожай. Класична формула процвітання.",
            "how_to_use": "Намалюйте на гаманці або банківській картці. Оновлюйте кожного молодика.",
            "name": "Став Багатства",
            "purpose": "Привернення грошей і фінансового потоку"
        }
    }
}
