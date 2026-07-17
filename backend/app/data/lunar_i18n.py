"""ES/PT/TR/UK content for lunar_days.py / moon_signs.py / api/v1/lunar.py
(TZ-080) — the biggest of the 6 sections (~640 translatable strings).

Shape: {lang: {key: {field: value}}} — see app.core.structural_i18n.
- LUNAR_DAYS_I18N: key is str(1-30); fields are symbol, title, desc, health,
  beauty, money, love, work, spiritual, dreams, stones, and indexed list
  items favorable_0.., unfavorable_0...
- MOON_SIGNS_I18N: key is the English sign name (e.g. "Aries"); fields are
  desc, work, love, health, beauty, and indexed list items favorable_0..,
  unfavorable_0... The sign *name* itself is NOT duplicated here — it's the
  same 12 zodiac names already covered by natal_i18n.SIGNS_I18N, reused via
  app.data.natal_i18n to avoid translating the same word twice.
- EVENT_DATA_I18N: key is the event type (e.g. "new_moon"); fields are
  title, desc.
- PHASE_NAMES_I18N: key is str(0-7); field is "name".

Generated in batches by scripts/generate_structural_translations.py
--section lunar (all fields of one day/sign/event in a single API call —
see BATCHED_SECTIONS). Empty until that runs; pick()/pick_list() fall back
to English for any language not present here yet.
"""

































































































































































































































LUNAR_DAYS_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "1": {
            "beauty": "Corte de pelo — no. Mascarillas faciales — sí.",
            "desc": "Inicio del ciclo lunar. Sienta las bases para nuevos proyectos, establece metas mensuales. La energía es mínima — no te esfuerces demasiado, solo planifica.",
            "dreams": "Proféticos. Recuérdalos y escríbelos.",
            "favorable_0": "Planificación",
            "favorable_1": "Establecimiento de metas",
            "favorable_2": "Meditación",
            "health": "La cabeza y el cerebro son vulnerables. Bebe agua, descansa.",
            "love": "Noche tranquila en pareja. Evita confrontaciones.",
            "money": "No pidas prestado. Planifica tu presupuesto.",
            "spiritual": "Meditación de intenciones. Escribe tus deseos.",
            "stones": "Piedra lunar, cristal de roca",
            "symbol": "Lámpara",
            "title": "Día de intenciones",
            "unfavorable_0": "Trabajo pesado",
            "unfavorable_1": "Conflictos",
            "unfavorable_2": "Decisiones arriesgadas",
            "work": "Haz un plan, no actúes aún."
        },
        "10": {
            "beauty": "Spa en casa — sí.",
            "desc": "Día de la familia. Recuerda tus raíces, llama a tus padres, cuida el hogar. Poderosa energía ancestral.",
            "dreams": "Sobre la familia — proféticos.",
            "favorable_0": "Asuntos familiares",
            "favorable_1": "Reparación del hogar",
            "favorable_2": "Tradiciones",
            "health": "Huesos y articulaciones. Calcio.",
            "love": "Fortalece la familia. Actividades conjuntas.",
            "money": "Inversiones familiares.",
            "spiritual": "Meditación ancestral, altar de los ancestros.",
            "stones": "Ámbar, coral",
            "symbol": "Fuente",
            "title": "Día de la Familia",
            "unfavorable_0": "Soledad",
            "unfavorable_1": "Egoísmo",
            "unfavorable_2": "Mudanza",
            "work": "Negocio familiar. Herencia."
        },
        "11": {
            "beauty": "Corte de pelo: el cabello será poderoso.",
            "desc": "El día lunar más poderoso. Energía al máximo. Se pueden mover montañas. El ayuno amplifica el poder.",
            "dreams": "Poderosos, fatídicos.",
            "favorable_0": "Tareas desafiantes",
            "favorable_1": "Deportes",
            "favorable_2": "Ayuno",
            "health": "Columna vertebral. Fuerza máxima.",
            "love": "Sentimientos fuertes. Propuestas de matrimonio.",
            "money": "Grandes negocios: ¡sí!",
            "spiritual": "Kundalini, prácticas energéticas.",
            "stones": "Diamante, cristal de roca",
            "symbol": "Corona",
            "title": "Día de Poder",
            "unfavorable_0": "Alcohol",
            "unfavorable_1": "Carne",
            "unfavorable_2": "Conflictos",
            "work": "Proyectos a gran escala, liderazgo."
        },
        "12": {
            "beauty": "Tratamientos hidratantes.",
            "desc": "Día de compasión y ayuda a los demás. Las oraciones se cumplen. No rechaces a quienes piden.",
            "dreams": "Sueños sagrados. Recuerda las imágenes.",
            "favorable_0": "Caridad",
            "favorable_1": "Oración",
            "favorable_2": "Perdón",
            "health": "Corazón. Cardio suave.",
            "love": "Amor desinteresado.",
            "money": "Da limosna — regresa el doble.",
            "spiritual": "Oración, iglesia, templo.",
            "stones": "Amatista, perla",
            "symbol": "Santo Grial",
            "title": "Día de la Misericordia",
            "unfavorable_0": "Grosería",
            "unfavorable_1": "Avaricia",
            "unfavorable_2": "Insultos",
            "work": "Ayuda a los colegas."
        },
        "13": {
            "beauty": "Corte de pelo — neutral. Manicura — sí.",
            "desc": "La información se absorbe fácilmente. Estudia, toma cursos, lee. El trabajo en grupo es efectivo.",
            "dreams": "Sobre el pasado — vacíos.",
            "favorable_0": "Aprendizaje",
            "favorable_1": "Trabajo en grupo",
            "favorable_2": "Viajes",
            "health": "Piel. Hidratación.",
            "love": "Aprender juntos acerca.",
            "money": "Neutral.",
            "spiritual": "Estudia esoterismo, astrología.",
            "stones": "Malaquita, hematita",
            "symbol": "Rueda",
            "title": "Día de Aprendizaje",
            "unfavorable_0": "Soledad",
            "unfavorable_1": "Pereza",
            "unfavorable_2": "Terquedad",
            "work": "Capacitaciones, desarrollo de habilidades."
        },
        "14": {
            "beauty": "Cuidado de la piel del contorno de ojos.",
            "desc": "La información del día es importante — lee las señales. No empieces cosas nuevas, sigue el llamado. Minimiza la carga visual.",
            "dreams": "Sueños que llaman — sigue.",
            "favorable_0": "Lectura de señales",
            "favorable_1": "Silencio",
            "favorable_2": "Paseos",
            "health": "Ojos. Reduce el tiempo de pantalla.",
            "love": "Silencio juntos.",
            "money": "No cierres tratos.",
            "spiritual": "Silencio, vipassana.",
            "stones": "Jacinto, citrino",
            "symbol": "Trompeta",
            "title": "Día del Llamado",
            "unfavorable_0": "Luz brillante",
            "unfavorable_1": "Demasiada información",
            "unfavorable_2": "Ruido",
            "work": "Mínimo de tareas. Reflexión."
        },
        "15": {
            "beauty": "Evita tratamientos.",
            "desc": "⚠️ Luna llena. Segundo día de Hécate. Tentaciones al máximo — controla emociones y apetito.",
            "dreams": "Pueden ser provocativos.",
            "favorable_0": "Ayuno",
            "favorable_1": "Meditación",
            "favorable_2": "Lucha contra hábitos",
            "health": "Páncreas. Ayuno obligatorio.",
            "love": "¡No discutas!",
            "money": "¡No gastes! Tentaciones.",
            "spiritual": "Ayuno, silencio, protección.",
            "stones": "Ágata negra, obsidiana",
            "symbol": "Serpiente",
            "title": "Día de Hécate",
            "unfavorable_0": "Alcohol",
            "unfavorable_1": "Comer en exceso",
            "unfavorable_2": "Peleas",
            "unfavorable_3": "Magia",
            "work": "Rutina, mínimo de decisiones."
        },
        "16": {
            "beauty": "Cuidado corporal — sí.",
            "desc": "Día tranquilo y armonioso. Equilibrio en todo. Evita los extremos, disfruta de las cosas simples.",
            "dreams": "Ligeros, agradables.",
            "favorable_0": "Armonía",
            "favorable_1": "Música",
            "favorable_2": "Naturaleza",
            "health": "Riñones. Bebe agua.",
            "love": "Ligereza y alegría.",
            "money": "Neutral.",
            "spiritual": "Mantras, canto.",
            "stones": "Cuarzo rosa, rodonita",
            "symbol": "Mariposa",
            "title": "Día de Armonía",
            "unfavorable_0": "Extremos",
            "unfavorable_1": "Agresión",
            "unfavorable_2": "Carne",
            "work": "Creatividad, diseño."
        },
        "17": {
            "beauty": "¡Todo favorable! Corte de pelo — sí.",
            "desc": "Celebración, diversión, socialización. Uno de los mejores días para bodas y romance. Energía femenina.",
            "dreams": "Eróticos — a la felicidad.",
            "favorable_0": "Boda",
            "favorable_1": "Fiestas",
            "favorable_2": "Romance",
            "health": "Sistema reproductivo. El sexo es beneficioso.",
            "love": "¡Mejor día para citas!",
            "money": "Gastos de fiesta — ok.",
            "spiritual": "Círculos de mujeres, baile.",
            "stones": "Granate, rubí",
            "symbol": "Racimo de uvas",
            "title": "Día de la Libertad",
            "unfavorable_0": "Soledad",
            "unfavorable_1": "Tristeza",
            "unfavorable_2": "Ascetismo",
            "work": "Eventos en equipo."
        },
        "18": {
            "beauty": "Exfoliantes, peelings — sí.",
            "desc": "Trabajo con la sombra. El día muestra tus defectos — acéptalos. No critiques a los demás.",
            "dreams": "Muestran el lado sombrío.",
            "favorable_0": "Autoanálisis",
            "favorable_1": "Trabajo con la sombra",
            "favorable_2": "Modestia",
            "health": "Piel. Purificación.",
            "love": "Acepta a tu pareja tal como es.",
            "money": "Neutral.",
            "spiritual": "Trabajo con el espejo, sombra.",
            "stones": "Cuarzo ahumado, morión",
            "symbol": "Espejo",
            "title": "Día de Reflexión",
            "unfavorable_0": "Vanidad",
            "unfavorable_1": "Crítica",
            "unfavorable_2": "Enojo",
            "work": "Retroalimentación, revisiones."
        },
        "19": {
            "beauty": "Evita cambios radicales.",
            "desc": "Día peligroso. Cuidado con ilusiones, engaños, manipulaciones. Purifica el espacio y los pensamientos.",
            "dreams": "Engañosos.",
            "favorable_0": "Limpieza del hogar",
            "favorable_1": "Ruptura de vínculos dañinos",
            "favorable_2": "Ayuno",
            "health": "Sistema nervioso. Descanso obligatorio.",
            "love": "Pueden surgir engaños.",
            "money": "¡No pidas prestado ni prestes!",
            "spiritual": "Purificación, protección, sal.",
            "stones": "Turmalina negra",
            "symbol": "Araña",
            "title": "Día de Purificación",
            "unfavorable_0": "Nuevos conocidos",
            "unfavorable_1": "Contratos",
            "unfavorable_2": "Inversiones",
            "work": "Verifica la información dos veces."
        },
        "2": {
            "beauty": "Cuidado de la piel — sí. Corte de pelo — neutro.",
            "desc": "La energía está creciendo. Bueno para ahorros, compras, inversiones. Ábrete a lo nuevo.",
            "dreams": "Sobre lo material — pueden hacerse realidad.",
            "favorable_0": "Compras",
            "favorable_1": "Iniciar proyectos",
            "favorable_2": "Actividad física",
            "health": "Boca y dientes. Bueno para empezar una dieta.",
            "love": "Regalos para la pareja. La generosidad regresa.",
            "money": "Bueno para compras e inversiones.",
            "spiritual": "Trabajo de abundancia. Gratitud.",
            "stones": "Ágata, calcedonia",
            "symbol": "Cuerno de la abundancia",
            "title": "Día de la adquisición",
            "unfavorable_0": "Avaricia",
            "unfavorable_1": "Comer en exceso",
            "unfavorable_2": "Ira",
            "work": "Inicia proyectos. La energía apoya."
        },
        "20": {
            "beauty": "Minimalismo. Natural.",
            "desc": "Elevación espiritual. Las meditaciones son profundas, las oraciones son fuertes. Supera lo terrenal, aspira hacia arriba.",
            "dreams": "Proféticos, ¡recuérdalos!",
            "favorable_0": "Prácticas espirituales",
            "favorable_1": "Ayuno",
            "favorable_2": "Ascenso",
            "health": "Sangre. La desintoxicación es beneficiosa.",
            "love": "Conexión espiritual.",
            "money": "Inversiones espirituales.",
            "spiritual": "Meditación profunda, oración.",
            "stones": "Amatista, labradorita",
            "symbol": "Águila",
            "title": "Día del Espíritu",
            "unfavorable_0": "Pasiones bajas",
            "unfavorable_1": "Alcohol",
            "unfavorable_2": "Pereza",
            "work": "Estrategia, visión."
        },
        "21": {
            "beauty": "Corte de pelo — sí, por coraje.",
            "desc": "El coraje y la honestidad son las claves. Defiende la verdad, protege a los débiles. El karma se acelera.",
            "dreams": "Heroicos — hacia la victoria.",
            "favorable_0": "Verdad",
            "favorable_1": "Deportes",
            "favorable_2": "Justicia",
            "health": "Hígado. Hierbas coleréticas.",
            "love": "Conversación honesta sobre sentimientos.",
            "money": "Tratos honestos — suerte.",
            "spiritual": "Templo, rituales de fuego.",
            "stones": "Rubí, jaspe rojo",
            "symbol": "Templo",
            "title": "Día de la Justicia",
            "unfavorable_0": "Cobardía",
            "unfavorable_1": "Mentira",
            "unfavorable_2": "Pereza",
            "work": "Liderazgo, toma de decisiones."
        },
        "22": {
            "beauty": "Neutral.",
            "desc": "Aprende y transmite conocimientos. La sabiduría llega a través de la experiencia y los libros. Comparte generosamente.",
            "dreams": "Sabios, simbólicos.",
            "favorable_0": "Aprendizaje",
            "favorable_1": "Escritura",
            "favorable_2": "Mentoría",
            "health": "Caderas y pelvis. Estiramiento.",
            "love": "Sabiduría en las relaciones.",
            "money": "Inversiones en educación.",
            "spiritual": "Estudio de textos sagrados.",
            "stones": "Lapislázuli, ojo de halcón",
            "symbol": "Elefante",
            "title": "Día de la Sabiduría",
            "unfavorable_0": "Acaparamiento de conocimiento",
            "unfavorable_1": "Aislamiento",
            "unfavorable_2": "Prisa",
            "work": "Planificación estratégica."
        },
        "23": {
            "beauty": "No hagas nada.",
            "desc": "⚠️ Tercer día de Hécate. Energía sanguinaria. Protégete, no empieces cosas nuevas, ten cuidado.",
            "dreams": "Posibles pesadillas.",
            "favorable_0": "Protección",
            "favorable_1": "Defensa",
            "favorable_2": "Ayuno",
            "health": "Sangre. Evita cortes.",
            "love": "Silencio. No provoques.",
            "money": "¡No arriesgues!",
            "spiritual": "Amuletos, círculos protectores.",
            "stones": "Shungita, ágata negra",
            "symbol": "Cocodrilo",
            "title": "Día de Hécate",
            "unfavorable_0": "Empezar cosas nuevas",
            "unfavorable_1": "Viajes",
            "unfavorable_2": "Cirugía",
            "work": "Mínimo de acciones."
        },
        "24": {
            "beauty": "Mascarillas para el cabello con aceites.",
            "desc": "Fuerza de la naturaleza. Energía masculina, creación, construcción. Sienta las bases.",
            "dreams": "Sobre la naturaleza — favorables.",
            "favorable_0": "Construcción",
            "favorable_1": "Jardinería",
            "favorable_2": "Sexo",
            "health": "Músculos. Entrenamiento de fuerza — sí.",
            "love": "Pasión y creación.",
            "money": "Compras grandes — sí.",
            "spiritual": "Conexión con la naturaleza, bosque.",
            "stones": "Ojo de tigre, jaspe",
            "symbol": "Oso",
            "title": "Día del Despertar",
            "unfavorable_0": "Agresión",
            "unfavorable_1": "Destrucción",
            "unfavorable_2": "Pereza",
            "work": "Trabajo pesado, construcción."
        },
        "25": {
            "beauty": "Tratamientos mínimos.",
            "desc": "Reduce la velocidad. Observa, no actúes. Sabiduría del silencio. Bueno para la meditación y la soledad.",
            "dreams": "Tranquilos, simbólicos.",
            "favorable_0": "Meditación",
            "favorable_1": "Descanso",
            "favorable_2": "Reflexión",
            "health": "Oídos, audición. El silencio sana.",
            "love": "Intimidad tranquila.",
            "money": "No te apresures en las decisiones.",
            "spiritual": "Vipassana, silencio.",
            "stones": "Piedra lunar, selenita",
            "symbol": "Tortuga",
            "title": "Día de contemplación",
            "unfavorable_0": "Apresuramiento",
            "unfavorable_1": "Alboroto",
            "unfavorable_2": "Demasiada socialización",
            "work": "Análisis, no acción."
        },
        "26": {
            "beauty": "Neutral.",
            "desc": "La locuacidad es la enemiga. Calla, no alardees, no prometas. Cualquier palabra de más se convierte en un problema.",
            "dreams": "Sobre el dinero — lo contrario.",
            "favorable_0": "Silencio",
            "favorable_1": "Economía",
            "favorable_2": "Ayuno",
            "health": "Piernas. Masaje de pies.",
            "love": "Calla sobre tus sentimientos.",
            "money": "¡Ahorra! No gastes de más.",
            "spiritual": "Práctica del silencio.",
            "stones": "Ónice, azabache",
            "symbol": "Sapo",
            "title": "Día de Obstáculos",
            "unfavorable_0": "Cháchara",
            "unfavorable_1": "Jactancia",
            "unfavorable_2": "Derroche",
            "work": "Trabajo silencioso, sin presentaciones."
        },
        "27": {
            "beauty": "Hidratación, sauna, piscina.",
            "desc": "El elemento agua es fuerte. Intuición, sueños, subconsciente. Viajes cerca del agua. Bebe más agua.",
            "dreams": "¡Proféticos! Especialmente sobre el agua.",
            "favorable_0": "Procedimientos acuáticos",
            "favorable_1": "Viajes",
            "favorable_2": "Intuición",
            "health": "Riñones, vejiga. ¡Agua!",
            "love": "Romance cerca del agua.",
            "money": "Neutral, sigue la intuición.",
            "spiritual": "Meditación en el agua, purificación.",
            "stones": "Aguamarina, perla",
            "symbol": "Tridente",
            "title": "Día del Agua",
            "unfavorable_0": "Alcohol",
            "unfavorable_1": "Decisiones difíciles",
            "unfavorable_2": "Fuego",
            "work": "Creatividad, decisiones intuitivas."
        },
        "28": {
            "beauty": "¡Todo favorable!",
            "desc": "Uno de los mejores días lunares. Alegría, armonía, claridad. Todo encaja fácilmente.",
            "dreams": "Favorables, se cumplen.",
            "favorable_0": "¡Todo!",
            "favorable_1": "Nuevos comienzos",
            "favorable_2": "Alegría",
            "health": "Ojos, visión. Ejercicios para los ojos.",
            "love": "Ideal para conocer gente y citas.",
            "money": "¡Suerte financiera!",
            "spiritual": "Meditación del loto, mantras.",
            "stones": "Cuarzo rosa, ópalo",
            "symbol": "Loto",
            "title": "Día de la Armonía",
            "unfavorable_0": "Prácticamente nada",
            "unfavorable_1": "Solo ira",
            "work": "Cualquier proyecto: éxito."
        },
        "29": {
            "beauty": "No hagas nada.",
            "desc": "⚠️ Cuarto día de Hécate. El día más oscuro. Purifica, termina, suelta. No empieces nada.",
            "dreams": "Oscuros, no tengas miedo.",
            "favorable_0": "Purificación",
            "favorable_1": "Terminar tareas",
            "favorable_2": "Ayuno",
            "health": "Bazo. Descanso completo.",
            "love": "No inicies relaciones.",
            "money": "Ni gastes ni ganes.",
            "spiritual": "Arrepentimiento, perdón, soltar.",
            "stones": "Ónice negro, morión",
            "symbol": "Pulpo",
            "title": "Día de Hécate",
            "unfavorable_0": "Todo lo nuevo",
            "unfavorable_1": "Tratos",
            "unfavorable_2": "Viajes",
            "work": "Solo terminar tareas."
        },
        "3": {
            "beauty": "Corte de pelo — sí, el cabello se volverá más espeso.",
            "desc": "Día de acciones activas y lucha. La energía es agresiva — canalízala hacia el deporte o la defensa de tus intereses.",
            "dreams": "Sueños de combate — símbolo de lucha interna.",
            "favorable_0": "Deportes",
            "favorable_1": "Defensa personal",
            "favorable_2": "Reparaciones",
            "health": "Oídos y nuca. Bueno para deportes activos.",
            "love": "¡Pasión! Pero no provoques celos.",
            "money": "Neutral. No arriesgues a lo grande.",
            "spiritual": "Trabajo con la ira. Transformación.",
            "stones": "Rubí, jaspe",
            "symbol": "Leopardo",
            "title": "Día del Guerrero",
            "unfavorable_0": "Peleas",
            "unfavorable_1": "Pereza",
            "unfavorable_2": "Empezar proyectos largos",
            "work": "Tareas activas, negociaciones."
        },
        "30": {
            "beauty": "Tratamientos finales — mascarillas.",
            "desc": "Fin de ciclo. Haz un resumen, agradece, perdona, deja ir. Preparación para la luna nueva.",
            "dreams": "Resumen, poner un límite.",
            "favorable_0": "Resumir",
            "favorable_1": "Gratitud",
            "favorable_2": "Perdón",
            "health": "Pies. Masaje, caminar descalzo.",
            "love": "Agradecimiento a la pareja.",
            "money": "Resume tus finanzas.",
            "spiritual": "Meditación de gratitud.",
            "stones": "Perla, piedra lunar",
            "symbol": "Cisne Dorado",
            "title": "Día de Resultados",
            "unfavorable_0": "Empezar cosas nuevas",
            "unfavorable_1": "Compras grandes",
            "unfavorable_2": "Alboroto",
            "work": "Informes, finalización de proyectos."
        },
        "4": {
            "beauty": "Mascarillas para el cabello — sí.",
            "desc": "Aprende, lee, explora. Bueno para trabajar con información y genealogía.",
            "dreams": "Vacíos, no les prestes atención.",
            "favorable_0": "Aprendizaje",
            "favorable_1": "Lectura",
            "favorable_2": "Trabajo de archivo",
            "health": "Cuello y garganta. Canta, haz ejercicios de respiración.",
            "love": "Charlas de corazón a corazón. Conózcanse mutuamente.",
            "money": "Neutral.",
            "spiritual": "Estudio de la ascendencia, meditación con el árbol.",
            "stones": "Esmeralda, jade",
            "symbol": "Árbol del Conocimiento",
            "title": "Día del Conocimiento",
            "unfavorable_0": "Cortar árboles",
            "unfavorable_1": "Mudanza",
            "unfavorable_2": "Reuniones ruidosas",
            "work": "Analítica, investigación, formación."
        },
        "5": {
            "beauty": "Mascarillas nutritivas — sí.",
            "desc": "La nutrición define la energía del día. Come conscientemente, cocina con amor. Día de lealtad a los principios.",
            "dreams": "Proféticos, especialmente sobre la comida.",
            "favorable_0": "Cocinar",
            "favorable_1": "Alimentación consciente",
            "favorable_2": "Lealtad",
            "health": "Estómago. La nutrición adecuada es especialmente importante.",
            "love": "Cena romántica. Aliméntense el uno al otro.",
            "money": "Bueno para gastar en comida y hogar.",
            "spiritual": "Gratitud por la comida. Oración antes de las comidas.",
            "stones": "Ojo de tigre, cornalina",
            "symbol": "Unicornio",
            "title": "Día de la Lealtad",
            "unfavorable_0": "Ayuno",
            "unfavorable_1": "Engaño",
            "unfavorable_2": "Traición",
            "work": "Trabajo en equipo, asociaciones."
        },
        "6": {
            "beauty": "Tratamientos aromáticos — sí.",
            "desc": "Se fortalecen la intuición y la previsión. Favorable para la sanación y las prácticas respiratorias.",
            "dreams": "Proféticos, a menudo se cumplen.",
            "favorable_0": "Meditación",
            "favorable_1": "Aromaterapia",
            "favorable_2": "Paseos",
            "health": "Pulmones y bronquios. Respira más hondo.",
            "love": "Ternura y cuidado.",
            "money": "Neutral.",
            "spiritual": "Pranayama, trabajo con la respiración.",
            "stones": "Turquesa, aguamarina",
            "symbol": "Grulla",
            "title": "Día de la Intuición",
            "unfavorable_0": "Cirugía",
            "unfavorable_1": "Conflictos",
            "unfavorable_2": "Mentira",
            "work": "Tareas creativas, negociaciones."
        },
        "7": {
            "beauty": "Neutral.",
            "desc": "Las palabras tienen un poder especial. Cuida tu habla, solo haz promesas que puedas cumplir.",
            "dreams": "Si lo cuentas — no se cumplirán.",
            "favorable_0": "Hablar en público",
            "favorable_1": "Negociaciones",
            "favorable_2": "Enseñanza",
            "health": "Órganos del habla. Bebe bebidas calientes.",
            "love": "Confesiones de amor. Las palabras serán recordadas.",
            "money": "Bueno para firmar contratos.",
            "spiritual": "Mantras, afirmaciones.",
            "stones": "Zafiro, lapislázuli",
            "symbol": "Rosa de los vientos",
            "title": "Día de la Palabra",
            "unfavorable_0": "Promesas vacías",
            "unfavorable_1": "Chismes",
            "unfavorable_2": "Maldiciones",
            "work": "Presentaciones, publicaciones."
        },
        "8": {
            "beauty": "Exfoliación, renovación — sí.",
            "desc": "Poderosa energía de renovación. Quema lo viejo — hábitos, cosas, rencores. Rituales de fuego.",
            "dreams": "Sobre la limpieza — síguelos.",
            "favorable_0": "Limpieza",
            "favorable_1": "Ayuno",
            "favorable_2": "Rituales de fuego",
            "health": "Estómago, metabolismo. El ayuno ligero es beneficioso.",
            "love": "Transformación de relaciones. Perdón.",
            "money": "Alquimia del dinero. Revisa las finanzas.",
            "spiritual": "Meditaciones de fuego, velas.",
            "stones": "Obsidiana, granate",
            "symbol": "Fénix",
            "title": "Día de Transformación",
            "unfavorable_0": "Cirugía",
            "unfavorable_1": "Iniciar un negocio",
            "unfavorable_2": "Pereza",
            "work": "Reestructuración, optimización."
        },
        "9": {
            "beauty": "Evita tratamientos.",
            "desc": "⚠️ Día lunar satánico. Peligroso, pesado. Posibles pesadillas. Ten cuidado con las personas y las decisiones.",
            "dreams": "Pesadillas. No las tomes literalmente.",
            "favorable_0": "Lucha contra las ilusiones",
            "favorable_1": "Limpieza",
            "favorable_2": "Oración",
            "health": "Máxima precaución. La inmunidad está baja.",
            "love": "No aclares las cosas. Silencio.",
            "money": "¡No gastes ni pidas prestado!",
            "spiritual": "Prácticas protectoras. Limpieza del hogar.",
            "stones": "Turmalina negra, ónice",
            "symbol": "Murciélago",
            "title": "Día de Hécate",
            "unfavorable_0": "Espejos",
            "unfavorable_1": "Empezar cosas nuevas",
            "unfavorable_2": "Viajes arriesgados",
            "work": "Rutina. No tomes decisiones importantes."
        }
    },
    "pt": {
        "1": {
            "beauty": "Corte de cabelo — não. Máscaras faciais — sim.",
            "desc": "Início do ciclo lunar. Lance as bases para novos projetos, defina metas mensais. A energia é mínima — não se sobrecarregue, apenas planeje.",
            "dreams": "Proféticos. Lembre-se e anote.",
            "favorable_0": "Planejamento",
            "favorable_1": "Definição de metas",
            "favorable_2": "Meditação",
            "health": "Cabeça e cérebro são vulneráveis. Mantenha-se hidratado, descanse.",
            "love": "Noite tranquila a dois. Evite confrontos.",
            "money": "Não pegue emprestado. Planeje seu orçamento.",
            "spiritual": "Meditação nas intenções. Anote os desejos.",
            "stones": "Pedra da lua, cristal de rocha",
            "symbol": "Lâmpada",
            "title": "Dia das Intenções",
            "unfavorable_0": "Trabalho pesado",
            "unfavorable_1": "Conflitos",
            "unfavorable_2": "Decisões arriscadas",
            "work": "Faça um plano, não aja ainda."
        },
        "10": {
            "beauty": "Spa em casa — sim.",
            "desc": "Dia em família. Lembre-se das suas raízes, ligue para os pais, cuide do lar. Poderosa energia ancestral.",
            "dreams": "Sobre a família — proféticos.",
            "favorable_0": "Assuntos familiares",
            "favorable_1": "Reforma da casa",
            "favorable_2": "Tradições",
            "health": "Ossos e articulações. Cálcio.",
            "love": "Fortaleça a família. Atividades conjuntas.",
            "money": "Investimentos familiares.",
            "spiritual": "Meditação sobre a linhagem, altar dos ancestrais.",
            "stones": "Âmbar, coral",
            "symbol": "Fonte",
            "title": "Dia da Família",
            "unfavorable_0": "Solidão",
            "unfavorable_1": "Egoísmo",
            "unfavorable_2": "Mudança",
            "work": "Negócio familiar. Herança."
        },
        "11": {
            "beauty": "Corte de cabelo — o cabelo ficará poderoso.",
            "desc": "Dia lunar mais poderoso. Energia no máximo. Pode mover montanhas. Jejum amplifica o poder.",
            "dreams": "Poderosos, fatídicos.",
            "favorable_0": "Tarefas desafiadoras",
            "favorable_1": "Esportes",
            "favorable_2": "Jejum",
            "health": "Coluna vertebral. Força máxima.",
            "love": "Sentimentos fortes. Propostas de casamento.",
            "money": "Grandes negócios — sim!",
            "spiritual": "Kundalini, práticas energéticas.",
            "stones": "Diamante, cristal de rocha",
            "symbol": "Coroa",
            "title": "Dia do Poder",
            "unfavorable_0": "Álcool",
            "unfavorable_1": "Carne",
            "unfavorable_2": "Conflitos",
            "work": "Projetos de grande escala, liderança."
        },
        "12": {
            "beauty": "Tratamentos hidratantes.",
            "desc": "Dia de compaixão e ajuda ao próximo. Orações são atendidas. Não negue a quem pede.",
            "dreams": "Sonhos sagrados. Lembre-se das imagens.",
            "favorable_0": "Caridade",
            "favorable_1": "Oração",
            "favorable_2": "Perdão",
            "health": "Coração. Cardio leve.",
            "love": "Amor altruísta.",
            "money": "Dê esmola — retorna em dobro.",
            "spiritual": "Oração, igreja, templo.",
            "stones": "Ametista, pérola",
            "symbol": "Santo Graal",
            "title": "Dia da Misericórdia",
            "unfavorable_0": "Grosseria",
            "unfavorable_1": "Avareza",
            "unfavorable_2": "Palavrão",
            "work": "Ajude colegas."
        },
        "13": {
            "beauty": "Corte de cabelo — neutro. Manicure — sim.",
            "desc": "A informação é absorvida facilmente. Estude, faça cursos, leia. O trabalho em grupo é eficaz.",
            "dreams": "Sobre o passado — vazios.",
            "favorable_0": "Aprendizado",
            "favorable_1": "Trabalho em grupo",
            "favorable_2": "Viagens",
            "health": "Pele. Hidratação.",
            "love": "Aprender juntos aproxima.",
            "money": "Neutro.",
            "spiritual": "Estude esoterismo, astrologia.",
            "stones": "Malaquita, hematita",
            "symbol": "Roda",
            "title": "Dia de Aprendizado",
            "unfavorable_0": "Solidão",
            "unfavorable_1": "Preguiça",
            "unfavorable_2": "Teimosia",
            "work": "Treinamentos, aperfeiçoamento profissional."
        },
        "14": {
            "beauty": "Cuidados com a pele ao redor dos olhos.",
            "desc": "A informação de hoje é importante — leia os sinais. Não comece coisas novas, siga o chamado. Minimize a carga visual.",
            "dreams": "Sonhos chamando — siga.",
            "favorable_0": "Leitura de sinais",
            "favorable_1": "Silêncio",
            "favorable_2": "Caminhadas",
            "health": "Olhos. Reduza o tempo de tela.",
            "love": "Silêncio juntos.",
            "money": "Não feche negócios.",
            "spiritual": "Silêncio, vipassana.",
            "stones": "Jacinto, citrino",
            "symbol": "Trompete",
            "title": "Dia do Chamado",
            "unfavorable_0": "Luz forte",
            "unfavorable_1": "Muita informação",
            "unfavorable_2": "Ruído",
            "work": "Tarefas mínimas. Reflexão."
        },
        "15": {
            "beauty": "Evite procedimentos.",
            "desc": "⚠️ Lua Cheia. Segundo dia de Hécate. Tentações no máximo — controle as emoções e o apetite.",
            "dreams": "Podem ser provocativos.",
            "favorable_0": "Jejum",
            "favorable_1": "Meditação",
            "favorable_2": "Luta contra hábitos",
            "health": "Pâncreas. Jejum obrigatório.",
            "love": "Não resolva questões!",
            "money": "Não gaste! Tentações.",
            "spiritual": "Jejum, silêncio, proteção.",
            "stones": "Ágata negra, obsidiana",
            "symbol": "Serpente",
            "title": "Dia de Hécate",
            "unfavorable_0": "Álcool",
            "unfavorable_1": "Comer em excesso",
            "unfavorable_2": "Discussões",
            "unfavorable_3": "Magia",
            "work": "Rotina, mínimo de decisões."
        },
        "16": {
            "beauty": "Cuidados com o corpo — sim.",
            "desc": "Dia harmonioso e tranquilo. Equilíbrio em tudo. Evite extremos, aproveite as coisas simples.",
            "dreams": "Leves, agradáveis.",
            "favorable_0": "Harmonia",
            "favorable_1": "Música",
            "favorable_2": "Natureza",
            "health": "Rins. Beba água.",
            "love": "Leveza e alegria.",
            "money": "Neutro.",
            "spiritual": "Mantras, canto.",
            "stones": "Quartzo rosa, rodonita",
            "symbol": "Borboleta",
            "title": "Dia da Harmonia",
            "unfavorable_0": "Extremos",
            "unfavorable_1": "Agressão",
            "unfavorable_2": "Carne",
            "work": "Criatividade, design."
        },
        "17": {
            "beauty": "Tudo favorável! Corte de cabelo — sim.",
            "desc": "Celebração, diversão, socialização. Um dos melhores dias para casamentos e romance. Energia feminina.",
            "dreams": "Eróticos — para a felicidade.",
            "favorable_0": "Casamento",
            "favorable_1": "Festas",
            "favorable_2": "Romance",
            "health": "Sistema reprodutivo. Sexo é benéfico.",
            "love": "Melhor dia para encontros!",
            "money": "Gastos com festa — ok.",
            "spiritual": "Círculos femininos, danças.",
            "stones": "Granada, rubi",
            "symbol": "Cacho de Uvas",
            "title": "Dia da Liberdade",
            "unfavorable_0": "Solidão",
            "unfavorable_1": "Tristeza",
            "unfavorable_2": "Ascetismo",
            "work": "Eventos em equipe."
        },
        "18": {
            "beauty": "Esfoliantes, peelings — sim.",
            "desc": "Trabalho com a sombra. O dia mostra suas falhas — aceite-as. Não critique os outros.",
            "dreams": "Mostram o lado sombrio.",
            "favorable_0": "Autoanálise",
            "favorable_1": "Trabalho com a sombra",
            "favorable_2": "Modéstia",
            "health": "Pele. Limpeza.",
            "love": "Aceite o parceiro como ele é.",
            "money": "Neutro.",
            "spiritual": "Trabalho com espelho, sombra.",
            "stones": "Quartzo fumê, morion",
            "symbol": "Espelho",
            "title": "Dia da Reflexão",
            "unfavorable_0": "Vaidade",
            "unfavorable_1": "Crítica",
            "unfavorable_2": "Raiva",
            "work": "Feedback, revisões."
        },
        "19": {
            "beauty": "Evite mudanças radicais.",
            "desc": "Dia perigoso. Cuidado com ilusões, enganos, manipulações. Limpe o espaço e os pensamentos.",
            "dreams": "Enganosos.",
            "favorable_0": "Limpeza da casa",
            "favorable_1": "Romper laços prejudiciais",
            "favorable_2": "Jejum",
            "health": "Sistema nervoso. Descanso obrigatório.",
            "love": "Enganos podem surgir.",
            "money": "Não peça emprestado nem empreste!",
            "spiritual": "Limpeza, proteção, sal.",
            "stones": "Turmalina preta.",
            "symbol": "Aranha",
            "title": "Dia de Limpeza",
            "unfavorable_0": "Novos conhecidos",
            "unfavorable_1": "Contratos",
            "unfavorable_2": "Investimentos",
            "work": "Verifique a informação duas vezes."
        },
        "2": {
            "beauty": "Cuidados com a pele — sim. Corte de cabelo — neutro.",
            "desc": "A energia está crescendo. Bom para economias, compras, investimentos. Abra-se para o novo.",
            "dreams": "Sobre coisas materiais — podem se realizar.",
            "favorable_0": "Compras",
            "favorable_1": "Iniciar projetos",
            "favorable_2": "Atividade física",
            "health": "Boca e dentes. Bom para começar uma dieta.",
            "love": "Presentes para o parceiro. A generosidade retorna.",
            "money": "Bom para compras e investimentos.",
            "spiritual": "Trabalho de abundância. Gratidão.",
            "stones": "Ágata, calcedônia",
            "symbol": "Corno da Abundância",
            "title": "Dia da Aquisição",
            "unfavorable_0": "Ganância",
            "unfavorable_1": "Comer em excesso",
            "unfavorable_2": "Raiva",
            "work": "Comece projetos. A energia apoia."
        },
        "20": {
            "beauty": "Minimalismo. Natural.",
            "desc": "Ascensão espiritual. Meditações são profundas, orações são fortes. Supere o terreno, aspire para o alto.",
            "dreams": "Proféticos, lembre-se!",
            "favorable_0": "Práticas espirituais",
            "favorable_1": "Jejum",
            "favorable_2": "Escalada",
            "health": "Sangue. Detox é benéfico.",
            "love": "Conexão espiritual.",
            "money": "Investimentos espirituais.",
            "spiritual": "Meditação profunda, oração.",
            "stones": "Ametista, labradorita",
            "symbol": "Águia",
            "title": "Dia do Espírito",
            "unfavorable_0": "Paixões baixas",
            "unfavorable_1": "Álcool",
            "unfavorable_2": "Preguiça",
            "work": "Estratégia, visão."
        },
        "21": {
            "beauty": "Corte de cabelo — sim, para coragem.",
            "desc": "Coragem e honestidade são as chaves. Defenda a verdade, proteja os fracos. O Karma acelera.",
            "dreams": "Heróicos — para a vitória.",
            "favorable_0": "Verdade",
            "favorable_1": "Esportes",
            "favorable_2": "Justiça",
            "health": "Fígado. Ervas coleréticas.",
            "love": "Conversa honesta sobre sentimentos.",
            "money": "Negócios honestos — sorte.",
            "spiritual": "Templo, rituais de fogo.",
            "stones": "Rubi, jaspe vermelho",
            "symbol": "Templo",
            "title": "Dia da Justiça",
            "unfavorable_0": "Covardia",
            "unfavorable_1": "Mentira",
            "unfavorable_2": "Preguiça",
            "work": "Liderança, tomada de decisões."
        },
        "22": {
            "beauty": "Neutro.",
            "desc": "Aprenda e transmita conhecimento. A sabedoria vem através da experiência e dos livros. Compartilhe generosamente.",
            "dreams": "Sábios, simbólicos.",
            "favorable_0": "Aprendizado",
            "favorable_1": "Escrita",
            "favorable_2": "Mentoria",
            "health": "Quadris e pelve. Alongamento.",
            "love": "Sabedoria nos relacionamentos.",
            "money": "Investimentos em educação.",
            "spiritual": "Estudo de textos sagrados.",
            "stones": "Lápis-lazúli, olho de falcão",
            "symbol": "Elefante",
            "title": "Dia da Sabedoria",
            "unfavorable_0": "Acumulação de conhecimento",
            "unfavorable_1": "Isolamento",
            "unfavorable_2": "Pressa",
            "work": "Planejamento estratégico."
        },
        "23": {
            "beauty": "Não faça nada.",
            "desc": "⚠️ Terceiro dia de Hécate. Energia sanguinária. Proteja-se, não comece nada novo, tenha cuidado.",
            "dreams": "Possíveis pesadelos.",
            "favorable_0": "Proteção",
            "favorable_1": "Defesa",
            "favorable_2": "Jejum",
            "health": "Sangue. Evite cortes.",
            "love": "Silêncio. Não provoque.",
            "money": "Não arrisque!",
            "spiritual": "Amuletos, círculos de proteção.",
            "stones": "Shungita, ágata negra",
            "symbol": "Crocodilo",
            "title": "Dia de Hécate",
            "unfavorable_0": "Começar coisas novas",
            "unfavorable_1": "Viagens",
            "unfavorable_2": "Cirurgias",
            "work": "Mínimo de ações."
        },
        "24": {
            "beauty": "Máscaras de cabelo com óleos.",
            "desc": "Força da natureza. Energia masculina, criação, construção. Estabeleça fundações.",
            "dreams": "Sobre a natureza — favoráveis.",
            "favorable_0": "Construção",
            "favorable_1": "Jardinagem",
            "favorable_2": "Sexo",
            "health": "Músculos. Treinamento de força — sim.",
            "love": "Paixão e criação.",
            "money": "Grandes compras — sim.",
            "spiritual": "Conexão com a natureza, floresta.",
            "stones": "Olho de tigre, jaspe",
            "symbol": "Urso",
            "title": "Dia do Despertar",
            "unfavorable_0": "Agressão",
            "unfavorable_1": "Destruição",
            "unfavorable_2": "Preguiça",
            "work": "Trabalho pesado, construção."
        },
        "25": {
            "beauty": "Mínimos tratamentos.",
            "desc": "Desacelere. Observe, não aja. Sabedoria do silêncio. Bom para meditação e solidão.",
            "dreams": "Silenciosos, simbólicos.",
            "favorable_0": "Meditação",
            "favorable_1": "Descanso",
            "favorable_2": "Reflexão",
            "health": "Ouvidos, audição. O silêncio cura.",
            "love": "Intimidade silenciosa.",
            "money": "Não apresse decisões.",
            "spiritual": "Vipassana, silêncio.",
            "stones": "Pedra da lua, selenita",
            "symbol": "Tartaruga",
            "title": "Dia de Contemplação",
            "unfavorable_0": "Pressa",
            "unfavorable_1": "Agitação",
            "unfavorable_2": "Muita socialização",
            "work": "Análise, não ação."
        },
        "26": {
            "beauty": "Neutro.",
            "desc": "A tagarelice é a inimiga. Fique em silêncio, não se gabe, não prometa. Qualquer palavra extra se torna um problema.",
            "dreams": "Sobre dinheiro — o oposto.",
            "favorable_0": "Silêncio",
            "favorable_1": "Economia",
            "favorable_2": "Jejum",
            "health": "Pernas. Massagem nos pés.",
            "love": "Fique em silêncio sobre seus sentimentos.",
            "money": "Economize! Não gaste demais.",
            "spiritual": "Prática de silêncio.",
            "stones": "Ônix, azeviche",
            "symbol": "Sapo",
            "title": "Dia dos Obstáculos",
            "unfavorable_0": "Tagarelice",
            "unfavorable_1": "Vanglória",
            "unfavorable_2": "Esbanjamento",
            "work": "Trabalho silencioso, sem apresentações."
        },
        "27": {
            "beauty": "Hidratação, sauna, piscina.",
            "desc": "O elemento água é forte. Intuição, sonhos, subconsciente. Viagens perto da água. Beba mais água.",
            "dreams": "Proféticos! Especialmente sobre água.",
            "favorable_0": "Procedimentos aquáticos",
            "favorable_1": "Viagens",
            "favorable_2": "Intuição",
            "health": "Rins, bexiga. Água!",
            "love": "Romance perto da água.",
            "money": "Neutro, siga a intuição.",
            "spiritual": "Meditação na água, limpeza.",
            "stones": "Água-marinha, pérola",
            "symbol": "Tridente",
            "title": "Dia da Água",
            "unfavorable_0": "Álcool",
            "unfavorable_1": "Decisões difíceis",
            "unfavorable_2": "Fogo",
            "work": "Criatividade, decisões intuitivas."
        },
        "28": {
            "beauty": "Tudo favorável!",
            "desc": "Um dos melhores dias lunares. Alegria, harmonia, clareza. Tudo se encaixa facilmente.",
            "dreams": "Favoráveis, realizam-se.",
            "favorable_0": "Tudo!",
            "favorable_1": "Novos começos",
            "favorable_2": "Alegria",
            "health": "Olhos, visão. Exercícios para os olhos.",
            "love": "Perfeito para conhecer pessoas e encontros.",
            "money": "Sorte financeira!",
            "spiritual": "Meditação do lótus, mantras.",
            "stones": "Quartzo rosa, opala",
            "symbol": "Lótus",
            "title": "Dia da Harmonia",
            "unfavorable_0": "Praticamente nada",
            "unfavorable_1": "Apenas raiva",
            "work": "Qualquer projeto — sucesso."
        },
        "29": {
            "beauty": "Não faça nada.",
            "desc": "⚠️ Quarto dia de Hécate. O dia mais escuro. Purifique, finalize, solte. Não comece nada.",
            "dreams": "Escuros, não tenha medo.",
            "favorable_0": "Purificação",
            "favorable_1": "Finalizar tarefas",
            "favorable_2": "Jejum",
            "health": "Baço. Descanso completo.",
            "love": "Não comece relacionamentos.",
            "money": "Nem gaste, nem ganhe.",
            "spiritual": "Arrependimento, perdão, desapego.",
            "stones": "Ônix preto, morion",
            "symbol": "Polvo",
            "title": "Dia de Hécate",
            "unfavorable_0": "Tudo novo",
            "unfavorable_1": "Negócios",
            "unfavorable_2": "Viagens",
            "work": "Apenas finalizar tarefas."
        },
        "3": {
            "beauty": "Corte de cabelo — sim, o cabelo ficará mais espesso.",
            "desc": "Dia de ações ativas e luta. A energia é agressiva — direcione-a para o esporte ou para a defesa de seus interesses.",
            "dreams": "Sonhos de batalha — símbolo de luta interna.",
            "favorable_0": "Esportes",
            "favorable_1": "Defesa de interesses",
            "favorable_2": "Reparos",
            "health": "Ouvidos e nuca. Bom para esportes ativos.",
            "love": "Paixão! Mas não provoque ciúmes.",
            "money": "Neutro. Não arrisque grande coisa.",
            "spiritual": "Trabalho com a raiva. Transformação.",
            "stones": "Rubi, jaspe",
            "symbol": "Leopardo",
            "title": "Dia do Guerreiro",
            "unfavorable_0": "Discussões",
            "unfavorable_1": "Preguiça",
            "unfavorable_2": "Iniciar projetos longos",
            "work": "Tarefas ativas, negociações."
        },
        "30": {
            "beauty": "Tratamentos finais — máscaras.",
            "desc": "Fim do ciclo. Faça um balanço, agradeça, perdoe, deixe ir. Preparação para a lua nova.",
            "dreams": "Resumo, traçando a linha.",
            "favorable_0": "Fazendo um balanço",
            "favorable_1": "Gratidão",
            "favorable_2": "Perdão",
            "health": "Pés. Massagem, caminhada descalço.",
            "love": "Gratidão ao parceiro.",
            "money": "Faça um balanço financeiro.",
            "spiritual": "Meditação de gratidão.",
            "stones": "Pérola, pedra da lua",
            "symbol": "Cisne Dourado",
            "title": "Dia dos Resultados",
            "unfavorable_0": "Começar coisas novas",
            "unfavorable_1": "Grandes compras",
            "unfavorable_2": "Agitação",
            "work": "Relatórios, finalização de projetos."
        },
        "4": {
            "beauty": "Máscaras para cabelo — sim.",
            "desc": "Aprenda, leia, explore. Bom para trabalhar com informações e genealogia.",
            "dreams": "Vazios, não dê atenção.",
            "favorable_0": "Aprendizado",
            "favorable_1": "Leitura",
            "favorable_2": "Trabalho com arquivos",
            "health": "Pescoço e garganta. Cante, faça exercícios respiratórios.",
            "love": "Conversas sinceras. Conheçam-se mutuamente.",
            "money": "Neutro.",
            "spiritual": "Estudo da ancestralidade, meditação na árvore.",
            "stones": "Esmeralda, jade",
            "symbol": "Árvore do Conhecimento",
            "title": "Dia do Conhecimento",
            "unfavorable_0": "Corte de árvores",
            "unfavorable_1": "Mudança",
            "unfavorable_2": "Reuniões barulhentas",
            "work": "Análise, pesquisa, treinamento."
        },
        "5": {
            "beauty": "Máscaras nutritivas — sim.",
            "desc": "A nutrição define a energia do dia. Coma conscientemente, cozinhe com amor. Dia de lealdade aos princípios.",
            "dreams": "Proféticos, especialmente sobre comida.",
            "favorable_0": "Cozinhar",
            "favorable_1": "Alimentação consciente",
            "favorable_2": "Lealdade",
            "health": "Estômago. A nutrição adequada é especialmente importante.",
            "love": "Jantar romântico. Alimentem-se mutuamente.",
            "money": "Bom para gastar com comida e lar.",
            "spiritual": "Gratidão pela comida. Oração antes das refeições.",
            "stones": "Olho de tigre, cornalina",
            "symbol": "Unicórnio",
            "title": "Dia da Lealdade",
            "unfavorable_0": "Jejum",
            "unfavorable_1": "Engano",
            "unfavorable_2": "Traição",
            "work": "Trabalho em equipe, parcerias."
        },
        "6": {
            "beauty": "Tratamentos aromáticos — sim.",
            "desc": "Intuição e previsão se fortalecem. Bom para cura e práticas respiratórias.",
            "dreams": "Proféticos, frequentemente se realizam.",
            "favorable_0": "Meditação",
            "favorable_1": "Aromaterapia",
            "favorable_2": "Caminhadas",
            "health": "Pulmões e brônquios. Respire mais fundo.",
            "love": "Ternura e cuidado.",
            "money": "Neutro.",
            "spiritual": "Pranayama, trabalho respiratório.",
            "stones": "Turquesa, água-marinha",
            "symbol": "Grou",
            "title": "Dia da Intuição",
            "unfavorable_0": "Cirurgia",
            "unfavorable_1": "Conflitos",
            "unfavorable_2": "Mentira",
            "work": "Tarefas criativas, negociações."
        },
        "7": {
            "beauty": "Neutro.",
            "desc": "As palavras têm um poder especial. Cuide do seu discurso, faça apenas promessas que você possa cumprir.",
            "dreams": "Se você contar, eles não se realizarão.",
            "favorable_0": "Falar em público",
            "favorable_1": "Negociações",
            "favorable_2": "Ensino",
            "health": "Órgãos da fala. Beba bebidas quentes.",
            "love": "Confissões de amor. As palavras serão lembradas.",
            "money": "Bom para assinar contratos.",
            "spiritual": "Mantras, afirmações.",
            "stones": "Safira, lápis-lazúli",
            "symbol": "Rosa dos Ventos",
            "title": "Dia da Palavra",
            "unfavorable_0": "Promessas vazias",
            "unfavorable_1": "Fofoca",
            "unfavorable_2": "Palavrões",
            "work": "Apresentações, publicações."
        },
        "8": {
            "beauty": "Peeling, renovação — sim.",
            "desc": "Energia poderosa de renovação. Queime o velho — hábitos, coisas, ressentimentos. Rituais de fogo.",
            "dreams": "Sobre purificação — siga-os.",
            "favorable_0": "Purificação",
            "favorable_1": "Jejum",
            "favorable_2": "Rituais de fogo",
            "health": "Estômago, metabolismo. Jejum leve é benéfico.",
            "love": "Transformação de relacionamento. Perdão.",
            "money": "Alquimia do dinheiro. Revise as finanças.",
            "spiritual": "Meditações de fogo, velas.",
            "stones": "Obsidiana, granada",
            "symbol": "Fênix",
            "title": "Dia da Transformação",
            "unfavorable_0": "Cirurgia",
            "unfavorable_1": "Iniciar negócio",
            "unfavorable_2": "Preguiça",
            "work": "Reestruturação, otimização."
        },
        "9": {
            "beauty": "Evite procedimentos.",
            "desc": "⚠️ Dia lunar satânico. Perigoso, pesado. Podem ocorrer pesadelos. Tenha cuidado com pessoas e decisões.",
            "dreams": "Pesadelos. Não leve ao pé da letra.",
            "favorable_0": "Lutar contra ilusões",
            "favorable_1": "Purificação",
            "favorable_2": "Oração",
            "health": "Cuidado máximo. Imunidade baixa.",
            "love": "Não resolva questões. Silêncio.",
            "money": "Não gaste nem peça emprestado!",
            "spiritual": "Práticas de proteção. Limpeza da casa.",
            "stones": "Turmalina negra, ônix",
            "symbol": "Morcego",
            "title": "Dia de Hécate",
            "unfavorable_0": "Espelhos",
            "unfavorable_1": "Começar coisas novas",
            "unfavorable_2": "Viagens arriscadas",
            "work": "Rotina. Não tome decisões importantes."
        }
    },
    "tr": {
        "1": {
            "beauty": "Saç kesimi — hayır. Yüz maskeleri — evet.",
            "desc": "Ay döngüsünün başlangıcı. Yeni işlerin temelini at, ay için hedefler belirle. Enerji minimum düzeyde — aşırı zorlama, sadece plan yap.",
            "dreams": "Kehanet niteliğinde. Hatırla ve yaz.",
            "favorable_0": "Planlama",
            "favorable_1": "Hedef belirleme",
            "favorable_2": "Meditasyon",
            "health": "Baş ve beyin hassas. Su iç, dinlen.",
            "love": "Birlikte sessiz bir akşam. Tartışmadan kaçının.",
            "money": "Borç alma. Bütçeni planla.",
            "spiritual": "Niyet meditasyonu. Dileklerini yaz.",
            "stones": "Ay taşı, kaya kristali",
            "symbol": "Lamba",
            "title": "Niyetler Günü",
            "unfavorable_0": "Ağır iş",
            "unfavorable_1": "Çatışmalar",
            "unfavorable_2": "Riskli kararlar",
            "work": "Bir plan yap, henüz harekete geçme."
        },
        "10": {
            "beauty": "Ev spa'sı — evet.",
            "desc": "Aile günü. Köklerini hatırla, anne babana ara, evle ilgilen. Güçlü soy enerjisi.",
            "dreams": "Aile hakkında — kehanet niteliğinde.",
            "favorable_0": "Aile meseleleri",
            "favorable_1": "Ev tamiri",
            "favorable_2": "Gelenekler",
            "health": "Kemikler ve eklemler. Kalsiyum.",
            "love": "Aileyi güçlendir. Ortak faaliyetler.",
            "money": "Aile yatırımları.",
            "spiritual": "Ata meditasyonu, ata sunağı.",
            "stones": "Kehribar, mercan",
            "symbol": "Çeşme",
            "title": "Aile Günü",
            "unfavorable_0": "Yalnızlık",
            "unfavorable_1": "Bencillik",
            "unfavorable_2": "Taşınma",
            "work": "Aile işi. Miras."
        },
        "11": {
            "beauty": "Saç kesimi — saçlar güçlü olacak.",
            "desc": "En güçlü ay günü. Enerji maksimumda. Dağları yerinden oynatabilir. Oruç gücü artırır.",
            "dreams": "Güçlü, kader belirleyici.",
            "favorable_0": "Zorlu görevler",
            "favorable_1": "Spor",
            "favorable_2": "Oruç",
            "health": "Omurga. Maksimum güç.",
            "love": "Güçlü duygular. Evlilik teklifleri.",
            "money": "Büyük anlaşmalar — evet!",
            "spiritual": "Kundalini, enerji pratikleri.",
            "stones": "Elmas, kaya kristali",
            "symbol": "Taç",
            "title": "Güç Günü",
            "unfavorable_0": "Alkol",
            "unfavorable_1": "Et",
            "unfavorable_2": "Çatışmalar",
            "work": "Büyük ölçekli projeler, liderlik."
        },
        "12": {
            "beauty": "Nemlendirici bakımlar.",
            "desc": "Merhamet ve başkalarına yardım günü. Dualar kabul olur. İsteyenleri geri çevirme.",
            "dreams": "Kutsal rüyalar. Görüntüleri hatırla.",
            "favorable_0": "Hayırseverlik",
            "favorable_1": "Dua",
            "favorable_2": "Bağışlama",
            "health": "Kalp. Hafif kardiyo.",
            "love": "Fedakâr aşk",
            "money": "Sadaka ver — iki kat geri döner.",
            "spiritual": "Dua, kilise, tapınak.",
            "stones": "Ametist, inci",
            "symbol": "Kutsal Kase",
            "title": "Merhamet Günü",
            "unfavorable_0": "Kabalık",
            "unfavorable_1": "Açgözlülük",
            "unfavorable_2": "Küfür",
            "work": "Meslektaşlara yardım et."
        },
        "13": {
            "beauty": "Saç kesimi — nötr. Manikür — evet.",
            "desc": "Bilgi kolayca emilir. Çalış, kurslara katıl, oku. Grup çalışması etkilidir.",
            "dreams": "Geçmişle ilgili — boş.",
            "favorable_0": "Öğrenme",
            "favorable_1": "Grup çalışması",
            "favorable_2": "Seyahat",
            "health": "Cilt. Nemlendirme.",
            "love": "Birlikte öğrenmek yakınlaştırır.",
            "money": "Nötr.",
            "spiritual": "Ezoterik, astroloji çalış.",
            "stones": "Malakit, hematit",
            "symbol": "Tekerlek",
            "title": "Öğrenme Günü",
            "unfavorable_0": "Yalnızlık",
            "unfavorable_1": "Tembellik",
            "unfavorable_2": "İnatçılık",
            "work": "Eğitimler, beceri geliştirme."
        },
        "14": {
            "beauty": "Göz çevresi cilt bakımı.",
            "desc": "Bugünün bilgisi önemlidir — işaretleri oku. Yeni şeylere başlama, çağrıyı takip et. Görsel yükü en aza indir.",
            "dreams": "Çağıran rüyalar — takip et.",
            "favorable_0": "İşaret okuma",
            "favorable_1": "Sessizlik",
            "favorable_2": "Yürüyüşler",
            "health": "Gözler. Ekran süresini azalt.",
            "love": "Birlikte sessizlik.",
            "money": "Anlaşma yapma.",
            "spiritual": "Sessizlik, vipassana.",
            "stones": "Sümbül taşı, sitrin",
            "symbol": "Trompet",
            "title": "Çağrı Günü",
            "unfavorable_0": "Parlak ışık",
            "unfavorable_1": "Çok fazla bilgi",
            "unfavorable_2": "Gürültü",
            "work": "Minimum görev. Düşünme."
        },
        "15": {
            "beauty": "Tedavilerden kaçın.",
            "desc": "⚠️ Dolunay. İkinci Hekate günü. Baştan çıkarmalar maksimumda — duyguları ve iştahı kontrol et.",
            "dreams": "Kışkırtıcı olabilir.",
            "favorable_0": "Oruç",
            "favorable_1": "Meditasyon",
            "favorable_2": "Alışkanlıklarla mücadele",
            "health": "Pankreas. Oruç zorunlu.",
            "love": "Hesaplaşma!",
            "money": "Harcama! Baştan çıkarmalar.",
            "spiritual": "Oruç, sessizlik, koruma.",
            "stones": "Siyah akik, obsidyen",
            "symbol": "Yılan",
            "title": "Hekate Günü",
            "unfavorable_0": "Alkol",
            "unfavorable_1": "Aşırı yemek",
            "unfavorable_2": "Kavgalar",
            "unfavorable_3": "Büyü",
            "work": "Rutin, minimum karar."
        },
        "16": {
            "beauty": "Vücut bakımı — evet.",
            "desc": "Sessiz uyumlu bir gün. Her şeyde denge. Aşırılıklardan kaçının, basit şeylerin tadını çıkarın.",
            "dreams": "Hafif, hoş.",
            "favorable_0": "Uyum",
            "favorable_1": "Müzik",
            "favorable_2": "Doğa",
            "health": "Böbrekler. Su için.",
            "love": "Hafiflik ve neşe.",
            "money": "Nötr.",
            "spiritual": "Mantralar, şarkı söyleme.",
            "stones": "Pembe kuvars, rodonit",
            "symbol": "Kelebek",
            "title": "Uyum Günü",
            "unfavorable_0": "Aşırılıklar",
            "unfavorable_1": "Saldırganlık",
            "unfavorable_2": "Et",
            "work": "Yaratıcılık, tasarım."
        },
        "17": {
            "beauty": "Her şey olumlu! Saç kesimi — evet.",
            "desc": "Kutlama, eğlence, sosyalleşme. Düğün ve romantizm için en iyi günlerden biri. Kadınsı enerji.",
            "dreams": "Erotik — mutluluğa.",
            "favorable_0": "Düğün",
            "favorable_1": "Partiler",
            "favorable_2": "Romantizm",
            "health": "Üreme sistemi. Seks faydalıdır.",
            "love": "Randevular için en iyi gün!",
            "money": "Parti harcamaları — tamam.",
            "spiritual": "Kadın çemberleri, dans.",
            "stones": "Nar, yakut",
            "symbol": "Üzüm Salkımı",
            "title": "Özgürlük Günü",
            "unfavorable_0": "Yalnızlık",
            "unfavorable_1": "Üzüntü",
            "unfavorable_2": "Çilecilik",
            "work": "Takım etkinlikleri."
        },
        "18": {
            "beauty": "Fırçalama, peeling — evet.",
            "desc": "Gölge çalışması. Gün, kusurlarını gösterir — onları kabul et. Başkalarını eleştirme.",
            "dreams": "Gölge tarafı gösterir.",
            "favorable_0": "Öz analiz",
            "favorable_1": "Gölge çalışması",
            "favorable_2": "Alçakgönüllülük",
            "health": "Cilt. Temizlik.",
            "love": "Partnerini olduğu gibi kabul et.",
            "money": "Nötr.",
            "spiritual": "Ayna çalışması, gölge.",
            "stones": "Dumanlı kuvars, morion",
            "symbol": "Ayna",
            "title": "Yansıma Günü",
            "unfavorable_0": "Kibir",
            "unfavorable_1": "Eleştiri",
            "unfavorable_2": "Öfke",
            "work": "Geri bildirim, değerlendirmeler."
        },
        "19": {
            "beauty": "Radikal değişikliklerden kaçının.",
            "desc": "Tehlikeli bir gün. Yanılsamalara, aldatmacalara, manipülasyonlara dikkat edin. Alanı ve düşünceleri temizleyin.",
            "dreams": "Aldatıcı.",
            "favorable_0": "Ev temizliği",
            "favorable_1": "Zararlı bağları koparmak",
            "favorable_2": "Oruç",
            "health": "Sinir sistemi. Dinlenme zorunludur.",
            "love": "Aldatmacalar ortaya çıkabilir.",
            "money": "Borç alma ve borç verme!",
            "spiritual": "Arınma, koruma, tuz.",
            "stones": "Siyah turmalin",
            "symbol": "Örümcek",
            "title": "Arınma Günü",
            "unfavorable_0": "Yeni tanıdıklar",
            "unfavorable_1": "Sözleşmeler",
            "unfavorable_2": "Yatırımlar",
            "work": "Bilgileri iki kez kontrol edin."
        },
        "2": {
            "beauty": "Cilt bakımı — evet. Saç kesimi — nötr.",
            "desc": "Enerji artıyor. Tasarruf, alışveriş, yatırım başlangıçları için uygun. Kendini yeniye aç.",
            "dreams": "Maddi şeyler hakkında — gerçekleşebilir.",
            "favorable_0": "Alışveriş",
            "favorable_1": "İşlere başlama",
            "favorable_2": "Fiziksel aktivite",
            "health": "Ağız ve dişler. Diyete başlamak için iyi.",
            "love": "Partnere hediyeler. Cömertlik geri döner.",
            "money": "Alışveriş ve yatırımlar için iyi.",
            "spiritual": "Bolluk çalışması. Şükran.",
            "stones": "Akik, kalsedon",
            "symbol": "Bereket Boynuzu",
            "title": "Kazanç Günü",
            "unfavorable_0": "Açgözlülük",
            "unfavorable_1": "Aşırı yeme",
            "unfavorable_2": "Öfke",
            "work": "Projelere başla. Enerji destekliyor."
        },
        "20": {
            "beauty": "Minimalizm. Doğal.",
            "desc": "Ruhsal yükseliş. Meditasyonlar derin, dualar güçlüdür. Dünyevi olanı aş, yukarıya doğru çabala.",
            "dreams": "Peygamberane, hatırla!",
            "favorable_0": "Ruhsal uygulamalar",
            "favorable_1": "Oruç",
            "favorable_2": "Tırmanış",
            "health": "Kan. Detoks faydalıdır.",
            "love": "Ruhsal bağlantı.",
            "money": "Ruhsal yatırımlar.",
            "spiritual": "Derin meditasyon, dua.",
            "stones": "Ametist, labradorit",
            "symbol": "Kartal",
            "title": "Ruh Günü",
            "unfavorable_0": "Bayağı tutkular",
            "unfavorable_1": "Alkol",
            "unfavorable_2": "Tembellik",
            "work": "Strateji, vizyon."
        },
        "21": {
            "beauty": "Saç kesimi — evet, cesaret için.",
            "desc": "Cesaret ve dürüstlük anahtarlardır. Gerçeğin arkasında dur, zayıfları koru. Karma hızlanır.",
            "dreams": "Kahramanca — zafere.",
            "favorable_0": "Gerçek",
            "favorable_1": "Spor",
            "favorable_2": "Adalet",
            "health": "Karaciğer. Safra söktürücü otlar.",
            "love": "Duygular hakkında dürüst konuşma.",
            "money": "Dürüst anlaşmalar — şans.",
            "spiritual": "Tapınak, ateş ritüelleri.",
            "stones": "Yakut, kırmızı jasper",
            "symbol": "Tapınak",
            "title": "Adalet Günü",
            "unfavorable_0": "Korkaklık",
            "unfavorable_1": "Yalan söyleme",
            "unfavorable_2": "Tembellik",
            "work": "Liderlik, karar verme."
        },
        "22": {
            "beauty": "Nötr.",
            "desc": "Öğren ve bilgiyi aktar. Bilgelik deneyim ve kitaplarla gelir. Cömertçe paylaş.",
            "dreams": "Bilgece, sembolik.",
            "favorable_0": "Öğrenme",
            "favorable_1": "Yazma",
            "favorable_2": "Mentorluk",
            "health": "Kalçalar ve pelvis. Esneme.",
            "love": "İlişkilerde bilgelik.",
            "money": "Eğitim yatırımları.",
            "spiritual": "Kutsal metinleri incelemek.",
            "stones": "Lapis lazuli, şahin gözü",
            "symbol": "Fil",
            "title": "Bilgelik Günü",
            "unfavorable_0": "Bilgi istifçiliği",
            "unfavorable_1": "İzolasyon",
            "unfavorable_2": "Acelecilik",
            "work": "Stratejik planlama."
        },
        "23": {
            "beauty": "Hiçbir şey yapma.",
            "desc": "⚠️ Üçüncü Hekate günü. Kana susamış enerji. Kendini koru, yeni şeylere başlama, dikkatli ol.",
            "dreams": "Kâbuslar mümkün.",
            "favorable_0": "Koruma",
            "favorable_1": "Savunma",
            "favorable_2": "Oruç",
            "health": "Kan. Kesiklerden kaçın.",
            "love": "Sessizlik. Kışkırtma.",
            "money": "Risk alma!",
            "spiritual": "Muskalar, koruyucu çemberler.",
            "stones": "Şungit, siyah akik",
            "symbol": "Timsah",
            "title": "Hekate Günü",
            "unfavorable_0": "Yeni şeylere başlamak",
            "unfavorable_1": "Seyahat",
            "unfavorable_2": "Ameliyat",
            "work": "Minimum eylem."
        },
        "24": {
            "beauty": "Yağlı saç maskeleri.",
            "desc": "Doğanın gücü. Eril enerji, yaratma, inşa etme. Temelleri at.",
            "dreams": "Doğayla ilgili — olumlu.",
            "favorable_0": "İnşaat",
            "favorable_1": "Bahçecilik",
            "favorable_2": "Seks",
            "health": "Kaslar. Kuvvet antrenmanları — evet.",
            "love": "Tutku ve yaratma.",
            "money": "Büyük alışverişler — evet.",
            "spiritual": "Doğayla bağlantı, orman.",
            "stones": "Kaplan gözü, jasper",
            "symbol": "Ayı",
            "title": "Uyanış Günü",
            "unfavorable_0": "Saldırganlık",
            "unfavorable_1": "Yıkım",
            "unfavorable_2": "Tembellik",
            "work": "Ağır iş, inşaat."
        },
        "25": {
            "beauty": "Minimum bakım.",
            "desc": "Yavaşla. Gözlemle, harekete geçme. Sessizliğin bilgeliği. Meditasyon ve yalnızlık için iyidir.",
            "dreams": "Sessiz, sembolik.",
            "favorable_0": "Meditasyon",
            "favorable_1": "Dinlenme",
            "favorable_2": "Düşünce",
            "health": "Kulaklar, işitme. Sessizlik iyileştirir.",
            "love": "Sessiz yakınlık.",
            "money": "Kararlarda acele etme.",
            "spiritual": "Vipassana, sessizlik.",
            "stones": "Ay taşı, selenit",
            "symbol": "Kaplumbağa",
            "title": "Tefekkür Günü",
            "unfavorable_0": "Acele",
            "unfavorable_1": "Telaş",
            "unfavorable_2": "Çok fazla sosyalleşme",
            "work": "Analiz, eylem değil."
        },
        "26": {
            "beauty": "Nötr.",
            "desc": "Gevezelik düşmandır. Sus, övünme, söz verme. Her gereksiz söz bir soruna dönüşür.",
            "dreams": "Para hakkında — tam tersi.",
            "favorable_0": "Sessizlik",
            "favorable_1": "Tasarruf",
            "favorable_2": "Oruç",
            "health": "Bacaklar. Ayak masajı.",
            "love": "Duyguların hakkında sus.",
            "money": "Tasarruf et! Gereksiz harcama yapma.",
            "spiritual": "Sessizlik pratiği.",
            "stones": "Oniks, jet",
            "symbol": "Kurbağa",
            "title": "Engeller Günü",
            "unfavorable_0": "Gevezelik",
            "unfavorable_1": "Övünme",
            "unfavorable_2": "Savurganlık",
            "work": "Sessiz çalışma, sunum yok."
        },
        "27": {
            "beauty": "Nemlendirme, sauna, havuz.",
            "desc": "Su elementi güçlüdür. Sezgi, rüyalar, bilinçaltı. Su kenarında seyahat. Daha fazla su iç.",
            "dreams": "Kehanet! Özellikle su hakkında.",
            "favorable_0": "Su tedavileri",
            "favorable_1": "Seyahat",
            "favorable_2": "Sezgi",
            "health": "Böbrekler, mesane. Su!",
            "love": "Su kenarında romantizm.",
            "money": "Nötr, sezgini takip et.",
            "spiritual": "Su meditasyonu, arınma.",
            "stones": "Akuamarin, inci",
            "symbol": "Üç dişli",
            "title": "Su Günü",
            "unfavorable_0": "Alkol",
            "unfavorable_1": "Zor kararlar",
            "unfavorable_2": "Ateş",
            "work": "Yaratıcılık, sezgisel kararlar."
        },
        "28": {
            "beauty": "Her şey olumlu!",
            "desc": "En iyi ay günlerinden biri. Neşe, uyum, berraklık. Her şey kolayca yoluna girer.",
            "dreams": "Olumlu, gerçekleşir.",
            "favorable_0": "Her şey!",
            "favorable_1": "Yeni başlangıçlar",
            "favorable_2": "Neşe",
            "health": "Gözler, görme. Göz egzersizleri.",
            "love": "Tanışmalar ve randevular için ideal.",
            "money": "Finansta şans!",
            "spiritual": "Lotus meditasyonu, mantralar.",
            "stones": "Pembe kuvars, opal",
            "symbol": "Lotus",
            "title": "Uyum Günü",
            "unfavorable_0": "Neredeyse hiçbir şey",
            "unfavorable_1": "Sadece öfke",
            "work": "Herhangi bir proje — başarı."
        },
        "29": {
            "beauty": "Hiçbir şey yapma.",
            "desc": "⚠️ Dördüncü Hekate günü. En karanlık gün. Arındır, bitir, bırak. Hiçbir şeye başlama.",
            "dreams": "Karanlık, korkma.",
            "favorable_0": "Arınma",
            "favorable_1": "İşleri bitirme",
            "favorable_2": "Oruç",
            "health": "Dalak. Tam dinlenme.",
            "love": "İlişki başlatma.",
            "money": "Ne harca ne kazan.",
            "spiritual": "Tövbe, affetme, bırakma.",
            "stones": "Siyah oniks, morion",
            "symbol": "Ahtapot",
            "title": "Hekate Günü",
            "unfavorable_0": "Her şey yeni",
            "unfavorable_1": "Anlaşmalar",
            "unfavorable_2": "Seyahatler",
            "work": "Sadece işleri bitirme."
        },
        "3": {
            "beauty": "Saç kesimi — evet, saçlar daha gürleşecek.",
            "desc": "Aktif eylemler ve mücadele günü. Enerji agresif — onu spora veya çıkarlarınızı savunmaya yönlendirin.",
            "dreams": "Savaş rüyaları — içsel mücadelenin sembolü.",
            "favorable_0": "Spor",
            "favorable_1": "Kendini savunma",
            "favorable_2": "Tamirat",
            "health": "Kulaklar ve ense. Aktif sporlar için iyi.",
            "love": "Tutku! Ama kıskançlık kışkırtma.",
            "money": "Nötr. Büyük risk alma.",
            "spiritual": "Öfke ile çalışma. Dönüşüm.",
            "stones": "Yakut, jasper",
            "symbol": "Leopar",
            "title": "Savaşçının Günü",
            "unfavorable_0": "Kavgalar",
            "unfavorable_1": "Tembellik",
            "unfavorable_2": "Uzun projelere başlamak",
            "work": "Aktif görevler, müzakereler."
        },
        "30": {
            "beauty": "Bitirme işlemleri — maskeler.",
            "desc": "Döngünün sonu. Özetle, minnettar ol, affet, bırak. Yeni aya hazırlık.",
            "dreams": "Özet, çizgi çekme.",
            "favorable_0": "Özetleme",
            "favorable_1": "Şükran",
            "favorable_2": "Affetme",
            "health": "Ayaklar. Masaj, çıplak ayakla yürüyüş.",
            "love": "Partnere şükran.",
            "money": "Mali durumu özetle.",
            "spiritual": "Şükran meditasyonu.",
            "stones": "İnci, ay taşı",
            "symbol": "Altın Kuğu",
            "title": "Sonuç Günü",
            "unfavorable_0": "Yeni şeylere başlamak",
            "unfavorable_1": "Büyük alışverişler",
            "unfavorable_2": "Telaş",
            "work": "Raporlar, projeleri bitirme."
        },
        "4": {
            "beauty": "Saç maskeleri — evet.",
            "desc": "Öğren, oku, keşfet. Bilgi ve soyağacı ile çalışmak için uygun.",
            "dreams": "Boş, aldırma.",
            "favorable_0": "Öğrenme",
            "favorable_1": "Okuma",
            "favorable_2": "Arşiv çalışması",
            "health": "Boyun ve boğaz. Şarkı söyle, nefes egzersizleri yap.",
            "love": "Samimi sohbetler. Birbirinizi tanıyın.",
            "money": "Nötr.",
            "spiritual": "Soy araştırması, ağaç meditasyonu.",
            "stones": "Zümrüt, yeşim",
            "symbol": "Bilgi Ağacı",
            "title": "Bilgi Günü",
            "unfavorable_0": "Ağaç kesme",
            "unfavorable_1": "Taşınma",
            "unfavorable_2": "Gürültülü toplantılar",
            "work": "Analitik, araştırma, eğitim."
        },
        "5": {
            "beauty": "Besleyici maskeler — evet.",
            "desc": "Beslenme günün enerjisini belirler. Bilinçli ye, sevgiyle pişir. İlkelere sadakat günü.",
            "dreams": "Kehanet niteliğinde, özellikle yemekle ilgili.",
            "favorable_0": "Yemek pişirme",
            "favorable_1": "Bilinçli yeme",
            "favorable_2": "Sadakat",
            "health": "Mide. Doğru beslenme özellikle önemlidir.",
            "love": "Romantik akşam yemeği. Birbirinizi besleyin.",
            "money": "Yemek ve ev harcamaları için uygun.",
            "spiritual": "Yemek için şükran. Yemek öncesi dua.",
            "stones": "Kaplan gözü, karnelyan",
            "symbol": "Tek boynuzlu at",
            "title": "Sadakat Günü",
            "unfavorable_0": "Oruç",
            "unfavorable_1": "Aldatma",
            "unfavorable_2": "İhanet",
            "work": "Takım çalışması, ortaklıklar."
        },
        "6": {
            "beauty": "Aromatik tedaviler — evet.",
            "desc": "Sezgi ve öngörü güçlenir. Şifa ve nefes çalışmaları için iyidir.",
            "dreams": "Kehanet niteliğinde, sık sık gerçekleşir.",
            "favorable_0": "Meditasyon",
            "favorable_1": "Aromaterapi",
            "favorable_2": "Yürüyüşler",
            "health": "Akciğerler ve bronşlar. Daha derin nefes al.",
            "love": "Şefkat ve ilgi.",
            "money": "Nötr.",
            "spiritual": "Pranayama, nefes çalışması.",
            "stones": "Turkuaz, akuamarin",
            "symbol": "Turna",
            "title": "Sezgi Günü",
            "unfavorable_0": "Cerrahi",
            "unfavorable_1": "Çatışmalar",
            "unfavorable_2": "Yalan",
            "work": "Yaratıcı görevler, müzakereler."
        },
        "7": {
            "beauty": "Nötr.",
            "desc": "Sözlerin özel bir gücü vardır. Konuşmana dikkat et, yalnızca tutabileceğin sözler ver.",
            "dreams": "Anlatırsan gerçekleşmez.",
            "favorable_0": "Topluluk önünde konuşma",
            "favorable_1": "Müzakereler",
            "favorable_2": "Öğretim",
            "health": "Konuşma organları. Ilık içecekler iç.",
            "love": "Aşk itirafları. Sözler hatırlanacak.",
            "money": "Sözleşme imzalamak için iyi.",
            "spiritual": "Mantralar, olumlamalar.",
            "stones": "Safir, lapis lazuli",
            "symbol": "Rüzgar Gülü",
            "title": "Sözün Günü",
            "unfavorable_0": "Boş vaatler",
            "unfavorable_1": "Dedikodu",
            "unfavorable_2": "Küfür",
            "work": "Sunumlar, yayınlar."
        },
        "8": {
            "beauty": "Peeling, yenilenme — evet.",
            "desc": "Güçlü yenilenme enerjisi. Eskiyi yak — alışkanlıkları, eşyaları, kırgınlıkları. Ateş ritüelleri.",
            "dreams": "Arınma hakkında — onları takip et.",
            "favorable_0": "Arınma",
            "favorable_1": "Oruç",
            "favorable_2": "Ateş ritüelleri",
            "health": "Mide, metabolizma. Hafif oruç faydalıdır.",
            "love": "İlişki dönüşümü. Affetme.",
            "money": "Para simyası. Finansları gözden geçir.",
            "spiritual": "Ateş meditasyonları, mumlar.",
            "stones": "Obsidiyen, granat",
            "symbol": "Anka",
            "title": "Dönüşüm Günü",
            "unfavorable_0": "Cerrahi",
            "unfavorable_1": "İş kurmak",
            "unfavorable_2": "Tembellik",
            "work": "Yeniden yapılanma, optimizasyon."
        },
        "9": {
            "beauty": "Prosedürlerden kaçının.",
            "desc": "⚠️ Şeytani ay günü. Tehlikeli, ağır. Kâbuslar görebilirsin. İnsanlara ve kararlara karşı dikkatli ol.",
            "dreams": "Kâbuslar. Gerçek anlamda yorumlama.",
            "favorable_0": "Yanılsamalarla mücadele",
            "favorable_1": "Arınma",
            "favorable_2": "Dua",
            "health": "Azami dikkat. Bağışıklık düşük.",
            "love": "İlişkileri düzeltme. Sessizlik.",
            "money": "Harcama ve borç alma!",
            "spiritual": "Koruyucu uygulamalar. Ev temizliği.",
            "stones": "Siyah turmalin, oniks",
            "symbol": "Yarasa",
            "title": "Hekate Günü",
            "unfavorable_0": "Aynalar",
            "unfavorable_1": "Yeni şeylere başlamak",
            "unfavorable_2": "Riskli yolculuklar",
            "work": "Rutin. Önemli kararlar alma."
        }
    },
    "uk": {
        "1": {
            "beauty": "Стрижка — ні. Маски для обличчя — так.",
            "desc": "Початок місячного циклу. Закладай фундамент нових справ, став цілі на місяць. Енергія мінімальна — не перенапружуйся, плануй.",
            "dreams": "Віщі. Запам'ятай і запиши.",
            "favorable_0": "Планування",
            "favorable_1": "Постановка цілей",
            "favorable_2": "Медитація",
            "health": "Голова і мозок вразливі. Пий воду, відпочивай.",
            "love": "Тихий вечір удвох. Не з'ясовуй стосунки.",
            "money": "Не бери в борг. Плануй бюджет.",
            "spiritual": "Медитація на наміри. Запиши бажання.",
            "stones": "Місячний камінь, гірський кришталь",
            "symbol": "Лампада",
            "title": "День намірів",
            "unfavorable_0": "Важка праця",
            "unfavorable_1": "Конфлікти",
            "unfavorable_2": "Ризиковані рішення",
            "work": "Склади план, не дій."
        },
        "10": {
            "beauty": "Домашній спа — так.",
            "desc": "Сімейний день. Згадай про коріння, зателефонуй батькам, займися домом. Потужна енергія роду.",
            "dreams": "Про сім'ю — віщі.",
            "favorable_0": "Сімейні справи",
            "favorable_1": "Ремонт вдома",
            "favorable_2": "Традиції",
            "health": "Кістки та суглоби. Кальцій.",
            "love": "Зміцнюй сім'ю. Спільні справи.",
            "money": "Сімейні інвестиції.",
            "spiritual": "Медитація на рід, вівтар предків.",
            "stones": "Бурштин, корал",
            "symbol": "Фонтан",
            "title": "День сім'ї",
            "unfavorable_0": "Самотність",
            "unfavorable_1": "Егоїзм",
            "unfavorable_2": "Переїзд",
            "work": "Сімейний бізнес. Спадщина."
        },
        "11": {
            "beauty": "Стрижка — волосся буде потужним.",
            "desc": "Найпотужніший місячний день. Енергія на максимумі. Можна звернути гори. Піст посилює силу.",
            "dreams": "Потужні, доленосні.",
            "favorable_0": "Складні завдання",
            "favorable_1": "Спорт",
            "favorable_2": "Голодування",
            "health": "Хребет. Максимальна сила.",
            "love": "Сильні почуття. Пропозиції руки.",
            "money": "Великі угоди — так!",
            "spiritual": "Кундаліні, енергетичні практики.",
            "stones": "Алмаз, гірський кришталь",
            "symbol": "Корона",
            "title": "День сили",
            "unfavorable_0": "Алкоголь",
            "unfavorable_1": "М'ясо",
            "unfavorable_2": "Конфлікти",
            "work": "Масштабні проекти, лідерство."
        },
        "12": {
            "beauty": "Зволожувальні процедури.",
            "desc": "День співчуття та допомоги іншим. Молитви виконуються. Не відмовляй тим, хто просить.",
            "dreams": "Святі сни. Запам'ятай образи.",
            "favorable_0": "Благодійність",
            "favorable_1": "Молитва",
            "favorable_2": "Прощення",
            "health": "Серце. Легкі кардіонавантаження.",
            "love": "Безкорисливе кохання.",
            "money": "Подавай милостиню — повернеться вдвічі.",
            "spiritual": "Молитва, церква, храм.",
            "stones": "Аметист, перлина",
            "symbol": "Святий Грааль",
            "title": "День милосердя",
            "unfavorable_0": "Грубість",
            "unfavorable_1": "Жадібність",
            "unfavorable_2": "Лайка",
            "work": "Допомагай колегам."
        },
        "13": {
            "beauty": "Стрижка — нейтрально. Манікюр — так.",
            "desc": "Інформація засвоюється легко. Вчися, проходь курси, читай. Групова робота ефективна.",
            "dreams": "Про минуле — порожні.",
            "favorable_0": "Навчання",
            "favorable_1": "Групова робота",
            "favorable_2": "Подорожі",
            "health": "Шкіра. Зволоження.",
            "love": "Спільне навчання зближує.",
            "money": "Нейтрально.",
            "spiritual": "Вивчай езотерику, астрологію.",
            "stones": "Малахіт, гематит",
            "symbol": "Колесо",
            "title": "День навчання",
            "unfavorable_0": "Самотність",
            "unfavorable_1": "Лінь",
            "unfavorable_2": "Впертість",
            "work": "Тренінги, підвищення кваліфікації."
        },
        "14": {
            "beauty": "Догляд за шкірою навколо очей.",
            "desc": "Інформація дня важлива — читай знаки. Не починай нового, слідуй поклику. Мінімум візуального навантаження.",
            "dreams": "Призиваючі сни — слідуй.",
            "favorable_0": "Читання знаків",
            "favorable_1": "Тиша",
            "favorable_2": "Прогулянки",
            "health": "Очі. Зменши екранний час.",
            "love": "Тиша вдвох.",
            "money": "Не укладай угод.",
            "spiritual": "Мовчання, віпассана.",
            "stones": "Гіацинт, цитрин",
            "symbol": "Труба",
            "title": "День призову",
            "unfavorable_0": "Яскраве світло",
            "unfavorable_1": "Багато інформації",
            "unfavorable_2": "Шум",
            "work": "Мінімум завдань. Рефлексія."
        },
        "15": {
            "beauty": "Уникай процедур.",
            "desc": "⚠️ Повний місяць. Другий день Гекати. Спокуси максимальні — контролюй емоції та апетит.",
            "dreams": "Можуть бути провокаційними.",
            "favorable_0": "Піст",
            "favorable_1": "Медитація",
            "favorable_2": "Боротьба зі звичками",
            "health": "Підшлункова. Піст обов'язковий.",
            "love": "Не з'ясовуй стосунки!",
            "money": "Не витрачай! Спокуси.",
            "spiritual": "Піст, мовчання, захист.",
            "stones": "Чорний агат, обсидіан",
            "symbol": "Змій",
            "title": "День Гекати",
            "unfavorable_0": "Алкоголь",
            "unfavorable_1": "Переїдання",
            "unfavorable_2": "Сварки",
            "unfavorable_3": "Магія",
            "work": "Рутина, мінімум рішень."
        },
        "16": {
            "beauty": "краса — Догляд за тілом — так.",
            "desc": "опис — Тихий гармонійний день. Баланс у всьому. Уникай крайнощів, насолоджуйся простими речами.",
            "dreams": "сни — Легкі, приємні.",
            "favorable_0": "сприятливе_0 — Гармонія",
            "favorable_1": "сприятливе_1 — Музика",
            "favorable_2": "сприятливе_2 — Природа",
            "health": "здоров'я — Нирки. Пийте воду.",
            "love": "любов — Легкість і радість.",
            "money": "гроші — Нейтрально.",
            "spiritual": "духовне — Мантри, спів.",
            "stones": "камені — Рожевий кварц, родоніт",
            "symbol": "символ — Метелик",
            "title": "назва — День гармонії",
            "unfavorable_0": "несприятливе_0 — Крайнощі",
            "unfavorable_1": "несприятливе_1 — Агресія",
            "unfavorable_2": "несприятливе_2 — М'ясо",
            "work": "робота — Творчість, дизайн."
        },
        "17": {
            "beauty": "Все сприятливо! Стрижка — так.",
            "desc": "Свято, веселощі, спілкування. Один із найкращих днів для весілля та романтики. Жіноча енергія.",
            "dreams": "Еротичні — на щастя.",
            "favorable_0": "Весілля",
            "favorable_1": "Вечірки",
            "favorable_2": "Романтика",
            "health": "Репродуктивна система. Секс корисний.",
            "love": "Найкращий день для побачень!",
            "money": "Витрати на свято — ок.",
            "spiritual": "Жіночі кола, танці.",
            "stones": "Гранат, рубін",
            "symbol": "Виноградне гроно",
            "title": "День свободи",
            "unfavorable_0": "Самотність",
            "unfavorable_1": "Смуток",
            "unfavorable_2": "Аскетизм",
            "work": "Командні заходи."
        },
        "18": {
            "beauty": "Скраби, пілінги — так.",
            "desc": "Робота з тінню. День показує твої недоліки — прийми їх. Не критикуй інших.",
            "dreams": "Показують тіньову сторону.",
            "favorable_0": "Самоаналіз",
            "favorable_1": "Робота з тінню",
            "favorable_2": "Скромність",
            "health": "Шкіра. Очищення.",
            "love": "Прийми партнера таким, який він є.",
            "money": "Нейтрально.",
            "spiritual": "Робота з дзеркалом, тінь.",
            "stones": "Раухтопаз, моріон",
            "symbol": "Дзеркало",
            "title": "День відображення",
            "unfavorable_0": "Марнославство",
            "unfavorable_1": "Критика",
            "unfavorable_2": "Злість",
            "work": "Зворотний зв'язок, рев'ю."
        },
        "19": {
            "beauty": "Уникай радикальних змін.",
            "desc": "Небезпечний день. Стережися ілюзій, обманів, маніпуляцій. Очищай простір і думки.",
            "dreams": "Оманливі.",
            "favorable_0": "Очищення дому",
            "favorable_1": "Розрив шкідливих зв'язків",
            "favorable_2": "Піст",
            "health": "Нервова система. Відпочинок обов'язковий.",
            "love": "Можуть викритися обмани.",
            "money": "Не позичай і не давай у борг!",
            "spiritual": "Очищення, захист, сіль.",
            "stones": "Чорний турмалін",
            "symbol": "Павук",
            "title": "День очищення",
            "unfavorable_0": "Нові знайомства",
            "unfavorable_1": "Договори",
            "unfavorable_2": "Вкладення",
            "work": "Перевіряй інформацію двічі."
        },
        "2": {
            "beauty": "Догляд за шкірою — так. Стрижка — нейтрально.",
            "desc": "Енергія зростає. Сприятливий для початку накопичень, шопінгу, інвестицій. Відкрий себе новому.",
            "dreams": "Про матеріальне — можуть здійснитися.",
            "favorable_0": "Покупки",
            "favorable_1": "Початок справ",
            "favorable_2": "Фізична активність",
            "health": "Рот і зуби. Добре починати дієту.",
            "love": "Подарунки партнеру. Щедрість повернеться.",
            "money": "Добре для покупок і вкладень.",
            "spiritual": "Робота з достатком. Вдячність.",
            "stones": "Агат, халцедон",
            "symbol": "Ріг достатку",
            "title": "День придбань",
            "unfavorable_0": "Жадібність",
            "unfavorable_1": "Переїдання",
            "unfavorable_2": "Гнів",
            "work": "Починай проекти. Енергія підтримує."
        },
        "20": {
            "beauty": "Мінімалізм. Натуральне.",
            "desc": "Духовний підйом. Медитації глибокі, молитви сильні. Перемагай земне, прагни вгору.",
            "dreams": "Пророчі, запам'ятай!",
            "favorable_0": "Духовні практики",
            "favorable_1": "Голодування",
            "favorable_2": "Сходження",
            "health": "Кров. Детокс корисний.",
            "love": "Духовний зв'язок.",
            "money": "Духовні інвестиції.",
            "spiritual": "Глибока медитація, молитва.",
            "stones": "Аметист, лабрадорит",
            "symbol": "Орел",
            "title": "День духу",
            "unfavorable_0": "Низькі пристрасті",
            "unfavorable_1": "Алкоголь",
            "unfavorable_2": "Лінь",
            "work": "Стратегія, бачення."
        },
        "21": {
            "beauty": "Стрижка — так, для сміливості.",
            "desc": "Хоробрість і чесність — ключі дня. Стій за правду, захищай слабких. Карма прискорюється.",
            "dreams": "Героїчні — до перемоги.",
            "favorable_0": "Правда",
            "favorable_1": "Спорт",
            "favorable_2": "Справедливість",
            "health": "Печінка. Жовчогінні трави.",
            "love": "Чесна розмова про почуття.",
            "money": "Чесні угоди — удача.",
            "spiritual": "Храм, вогняні ритуали.",
            "stones": "Рубін, червона яшма",
            "symbol": "Храм",
            "title": "День справедливості",
            "unfavorable_0": "Боягузтво",
            "unfavorable_1": "Брехня",
            "unfavorable_2": "Лінь",
            "work": "Лідерство, прийняття рішень."
        },
        "22": {
            "beauty": "Нейтрально.",
            "desc": "Вчися та передавай знання. Мудрість приходить через досвід і книги. Щедро ділися.",
            "dreams": "Мудрі, символічні.",
            "favorable_0": "Навчання",
            "favorable_1": "Написання",
            "favorable_2": "Наставництво",
            "health": "Стегна і таз. Розтяжка.",
            "love": "Мудрість у стосунках.",
            "money": "Інвестиції в освіту.",
            "spiritual": "Вивчення священних текстів.",
            "stones": "Лазурит, соколине око",
            "symbol": "Слон",
            "title": "День мудрості",
            "unfavorable_0": "Жадібність до знань",
            "unfavorable_1": "Ізоляція",
            "unfavorable_2": "Поспіх",
            "work": "Стратегічне планування."
        },
        "23": {
            "beauty": "Нічого не роби.",
            "desc": "⚠️ Третій день Гекати. Кровожерна енергія. Захищайся, не починай нового, будь обережним.",
            "dreams": "Кошмари можливі.",
            "favorable_0": "Захист",
            "favorable_1": "Оборона",
            "favorable_2": "Піст",
            "health": "Кров. Уникай порізів.",
            "love": "Тиша. Не провокуй.",
            "money": "Не ризикуй!",
            "spiritual": "Обереги, захисні кола.",
            "stones": "Шунгіт, чорний агат",
            "symbol": "Крокодил",
            "title": "День Гекати",
            "unfavorable_0": "Починати нове",
            "unfavorable_1": "Подорожі",
            "unfavorable_2": "Операції",
            "work": "Мінімум дій."
        },
        "24": {
            "beauty": "Маски для волосся з оліями.",
            "desc": "Сила природи. Чоловіча енергія, творення, будівництво. Закладай фундаменти.",
            "dreams": "Про природу — сприятливі.",
            "favorable_0": "Будівництво",
            "favorable_1": "Садівництво",
            "favorable_2": "Секс",
            "health": "М'язи. Силові тренування — так.",
            "love": "Пристрасть та творення.",
            "money": "Великі покупки — так.",
            "spiritual": "Зв'язок з природою, ліс.",
            "stones": "Тигрове око, яшма",
            "symbol": "Ведмідь",
            "title": "День пробудження",
            "unfavorable_0": "Агресія",
            "unfavorable_1": "Руйнування",
            "unfavorable_2": "Лінь",
            "work": "Важка робота, будівництво."
        },
        "25": {
            "beauty": "Мінімум процедур.",
            "desc": "Сповільнись. Спостерігай, не дій. Мудрість тиші. Добре для медитації та усамітнення.",
            "dreams": "Тихі, символічні.",
            "favorable_0": "Медитація",
            "favorable_1": "Відпочинок",
            "favorable_2": "Роздуми",
            "health": "Вуха, слух. Тиша лікує.",
            "love": "Тиха близькість.",
            "money": "Не поспішай з рішеннями.",
            "spiritual": "Віпассана, мовчання.",
            "stones": "Місячний камінь, селеніт",
            "symbol": "Черепаха",
            "title": "День споглядання",
            "unfavorable_0": "Поспіх",
            "unfavorable_1": "Метушня",
            "unfavorable_2": "Багато спілкування",
            "work": "Аналіз, не дія."
        },
        "26": {
            "beauty": "Нейтрально.",
            "desc": "Балакучість — ворог. Мовчи, не хвастайся, не обіцяй. Будь-яке зайве слово обернеться проблемою.",
            "dreams": "Про гроші — навпаки.",
            "favorable_0": "Мовчання",
            "favorable_1": "Економія",
            "favorable_2": "Піст",
            "health": "Ноги. Масаж стоп.",
            "love": "Мовчи про свої почуття.",
            "money": "Економ! Не витрачай зайвого.",
            "spiritual": "Практика мовчання.",
            "stones": "Онікс, гагат",
            "symbol": "Ропуха",
            "title": "День перешкод",
            "unfavorable_0": "Балаканина",
            "unfavorable_1": "Хвальба",
            "unfavorable_2": "Марнотратство",
            "work": "Тиха робота, без презентацій."
        },
        "27": {
            "beauty": "Зволоження, лазня, басейн.",
            "desc": "Водна стихія сильна. Інтуїція, сни, підсвідомість. Подорожі біля води. Пий більше води.",
            "dreams": "Віщі! Особливо про воду.",
            "favorable_0": "Водні процедури",
            "favorable_1": "Подорожі",
            "favorable_2": "Інтуїція",
            "health": "Нирки, сечовий міхур. Вода!",
            "love": "Романтика біля води.",
            "money": "Нейтрально, слідуй інтуїції.",
            "spiritual": "Медитація біля води, очищення.",
            "stones": "Аквамарин, перлина",
            "symbol": "Тризуб",
            "title": "День води",
            "unfavorable_0": "Алкоголь",
            "unfavorable_1": "Жорсткі рішення",
            "unfavorable_2": "Вогонь",
            "work": "Творчість, інтуїтивні рішення."
        },
        "28": {
            "beauty": "Все сприятливо!",
            "desc": "Один із найкращих місячних днів. Радість, гармонія, ясність. Все складається легко.",
            "dreams": "Сприятливі, збуваються.",
            "favorable_0": "Все!",
            "favorable_1": "Нові починання",
            "favorable_2": "Радість",
            "health": "Очі, зір. Гімнастика для очей.",
            "love": "Ідеально для знайомств і побачень.",
            "money": "Удача в фінансах!",
            "spiritual": "Медитація лотоса, мантри.",
            "stones": "Рожевий кварц, опал",
            "symbol": "Лотос",
            "title": "День гармонії",
            "unfavorable_0": "Практично нічого",
            "unfavorable_1": "Тільки злість",
            "work": "Будь-які проекти — успіх."
        },
        "29": {
            "beauty": "Нічого не роби.",
            "desc": "⚠️ Четвертий день Гекати. Найтемніший день. Очищай, завершуй, відпускай. Не починай нічого.",
            "dreams": "Темні, не лякайся.",
            "favorable_0": "Очищення",
            "favorable_1": "Завершення справ",
            "favorable_2": "Піст",
            "health": "Селезінка. Повний відпочинок.",
            "love": "Не починай стосунків.",
            "money": "Ні витрачай, ні заробляй.",
            "spiritual": "Покаяння, прощення, відпускання.",
            "stones": "Чорний онікс, моріон",
            "symbol": "Восьминіг",
            "title": "День Гекати",
            "unfavorable_0": "Все нове",
            "unfavorable_1": "Угоди",
            "unfavorable_2": "Подорожі",
            "work": "Тільки завершення справ."
        },
        "3": {
            "beauty": "Стрижка — так, волосся стане густішим.",
            "desc": "День активних дій і боротьби. Енергія агресивна — спрямуй її у спорт або захист своїх інтересів.",
            "dreams": "Бойові сни — символ внутрішньої боротьби.",
            "favorable_0": "Спорт",
            "favorable_1": "Захист інтересів",
            "favorable_2": "Ремонт",
            "health": "Вуха та потилиця. Добре для активного спорту.",
            "love": "Пристрасть! Але не провокуй ревнощі.",
            "money": "Нейтрально. Не ризикуй крупно.",
            "spiritual": "Робота з гнівом. Трансформація.",
            "stones": "Рубін, яшма",
            "symbol": "Барс",
            "title": "День воїна",
            "unfavorable_0": "Ссори",
            "unfavorable_1": "Лінь",
            "unfavorable_2": "Починати довгі справи",
            "work": "Активні завдання, переговори."
        },
        "30": {
            "beauty": "Завершальні процедури — маски.",
            "desc": "Завершення циклу. Підведи підсумки, подякуй, пробач, відпусти. Підготовка до молодика.",
            "dreams": "Підсумкові, підводять риску.",
            "favorable_0": "Підсумки",
            "favorable_1": "Вдячність",
            "favorable_2": "Прощення",
            "health": "Стопи. Масаж, ходьба босоніж.",
            "love": "Вдячність партнеру.",
            "money": "Підведи фінансові підсумки.",
            "spiritual": "Вдячна медитація.",
            "stones": "Перлина, місячний камінь",
            "symbol": "Золотий лебідь",
            "title": "День підсумків",
            "unfavorable_0": "Починати нове",
            "unfavorable_1": "Великі покупки",
            "unfavorable_2": "Метушня",
            "work": "Звіти, завершення проєктів."
        },
        "4": {
            "beauty": "Маски для волосся — так.",
            "desc": "Вчися, читай, досліджуй. День підходить для роботи з інформацією та генеалогією.",
            "dreams": "Порожні, не надавай значення.",
            "favorable_0": "Навчання",
            "favorable_1": "Читання",
            "favorable_2": "Робота з архівами",
            "health": "Шия та горло. Співай, роби дихальні практики.",
            "love": "Розмови по душах. Пізнавайте один одного.",
            "money": "Нейтрально.",
            "spiritual": "Вивчення роду, медитація біля дерева.",
            "stones": "Смарагд, нефрит",
            "symbol": "Дерево пізнання",
            "title": "День знань",
            "unfavorable_0": "Вирубка дерев",
            "unfavorable_1": "Переїзд",
            "unfavorable_2": "Шумні компанії",
            "work": "Аналітика, дослідження, навчання."
        },
        "5": {
            "beauty": "Поживні маски — так.",
            "desc": "Харчування визначає енергію дня. Їжте свідомо, готуйте з любов'ю. День відданості принципам.",
            "dreams": "Віщі, особливо про їжу.",
            "favorable_0": "Готування",
            "favorable_1": "Свідоме харчування",
            "favorable_2": "Відданість",
            "health": "Шлунок. Правильне харчування особливо важливе.",
            "love": "Романтична вечеря. Годуйте один одного.",
            "money": "Сприятливо для витрат на їжу та дім.",
            "spiritual": "Вдячність за їжу. Молитва перед їжею.",
            "stones": "Тигрове око, сердолік",
            "symbol": "Єдиноріг",
            "title": "День відданості",
            "unfavorable_0": "Голодування",
            "unfavorable_1": "Обман",
            "unfavorable_2": "Зрада",
            "work": "Командна робота, партнерства."
        },
        "6": {
            "beauty": "Ароматичні процедури — так.",
            "desc": "Посилюється інтуїція та передбачення. Сприятливий для цілительства та дихальних практик.",
            "dreams": "Віщі, часто збуваються.",
            "favorable_0": "Медитація",
            "favorable_1": "Ароматерапія",
            "favorable_2": "Прогулянки",
            "health": "Легені та бронхи. Дихай глибше.",
            "love": "Ніжність та турбота.",
            "money": "Нейтрально.",
            "spiritual": "Пранаяма, робота з диханням.",
            "stones": "Бірюза, аквамарин",
            "symbol": "Журавель",
            "title": "День інтуїції",
            "unfavorable_0": "Хірургія",
            "unfavorable_1": "Конфлікти",
            "unfavorable_2": "Брехня",
            "work": "Творчі завдання, переговори."
        },
        "7": {
            "beauty": "Нейтрально.",
            "desc": "Слова мають особливу силу. Слідкуй за мовленням, давай обіцянки тільки ті, що виконаєш.",
            "dreams": "Якщо розкажеш — не здійсняться.",
            "favorable_0": "Публічні виступи",
            "favorable_1": "Переговори",
            "favorable_2": "Навчання",
            "health": "Мовний апарат. Пий тепле.",
            "love": "Освідчення в коханні. Слова запам'ятаються.",
            "money": "Добре для укладання договорів.",
            "spiritual": "Мантри, афірмації.",
            "stones": "Сапфір, лазурит",
            "symbol": "Роза вітрів",
            "title": "День слова",
            "unfavorable_0": "Порожні обіцянки",
            "unfavorable_1": "Плітки",
            "unfavorable_2": "Лайка",
            "work": "Презентації, публікації."
        },
        "8": {
            "beauty": "Пілінг, оновлення — так.",
            "desc": "Потужна енергія оновлення. Спалюй старе — звички, речі, образи. Вогняні ритуали.",
            "dreams": "Про очищення — слідуй їм.",
            "favorable_0": "Очищення",
            "favorable_1": "Голодування",
            "favorable_2": "Вогняні ритуали",
            "health": "Шлунок, метаболізм. Легке голодування корисне.",
            "love": "Трансформація стосунків. Прощення.",
            "money": "Алхімія грошей. Переглянь фінанси.",
            "spiritual": "Вогняні медитації, свічки.",
            "stones": "Обсидіан, гранат",
            "symbol": "Фенікс",
            "title": "День трансформації",
            "unfavorable_0": "Хірургія",
            "unfavorable_1": "Починати бізнес",
            "unfavorable_2": "Лінь",
            "work": "Реструктуризація, оптимізація."
        },
        "9": {
            "beauty": "Уникай процедур.",
            "desc": "⚠️ Сатанинський місячний день. Небезпечний, важкий. Можуть снитися кошмари. Будь обережний з людьми та рішеннями.",
            "dreams": "Кошмари. Не сприймай буквально.",
            "favorable_0": "Боротьба з ілюзіями",
            "favorable_1": "Очищення",
            "favorable_2": "Молитва",
            "health": "Максимальна обережність. Імунітет знижений.",
            "love": "Не з'ясовуй стосунки. Тиша.",
            "money": "Не витрачай і не позичай!",
            "spiritual": "Захисні практики. Очищення дому.",
            "stones": "Чорний турмалін, онікс",
            "symbol": "Кажан",
            "title": "День Гекати",
            "unfavorable_0": "Дзеркала",
            "unfavorable_1": "Починати нове",
            "unfavorable_2": "Ризиковані поїздки",
            "work": "Рутина. Не приймай важливих рішень."
        }
    }
}
MOON_SIGNS_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "Aquarius": {
            "beauty": "Experimentos de imagen — ¡sí!",
            "desc": "Luna en Acuario — libertad, originalidad, tecnología. Tiempo para experimentos y amistad.",
            "favorable_0": "Tecnología",
            "favorable_1": "Amistad",
            "favorable_2": "Innovación",
            "health": "Espinillas, vasos. Estiramiento.",
            "love": "Amistad sobre pasión.",
            "unfavorable_0": "Tradiciones",
            "unfavorable_1": "Rutina",
            "work": "TI, startups, networking."
        },
        "Aries": {
            "beauty": "No te cortes el cabello — crecerá áspero.",
            "desc": "Luna en Aries — impulsividad, sed de acción. Bueno para comenzar cosas, no para la paciencia.",
            "favorable_0": "Deportes",
            "favorable_1": "Nuevos comienzos",
            "favorable_2": "Competencias",
            "health": "Cabeza, cara. Evita el sobrecalentamiento.",
            "love": "Pasión, pero no largas conversaciones.",
            "unfavorable_0": "Paciencia",
            "unfavorable_1": "Negociaciones largas",
            "work": "Decisiones rápidas, lanzamientos de proyectos."
        },
        "Cancer": {
            "beauty": "Hidratación, cuidado del cabello — ¡sí!",
            "desc": "Luna en Cáncer — hogar, familia, emociones. El momento más acogedor. Cocina, limpia, cuida.",
            "favorable_0": "Hogar",
            "favorable_1": "Familia",
            "favorable_2": "Cuidado del cuerpo",
            "health": "Pecho, estómago. Comida ligera.",
            "love": "Emociones profundas, cuidado.",
            "unfavorable_0": "Ambiciones profesionales",
            "unfavorable_1": "Proyectos arriesgados",
            "work": "Oficina en casa, atención al cliente."
        },
        "Capricorn": {
            "beauty": "Manicura — las uñas estarán fuertes.",
            "desc": "Luna en Capricornio — disciplina, carrera, responsabilidad. Tiempo serio para asuntos serios.",
            "favorable_0": "Carrera",
            "favorable_1": "Planificación",
            "favorable_2": "Disciplina",
            "health": "Huesos, rodillas, dientes.",
            "love": "Charlas serias sobre el futuro.",
            "unfavorable_0": "Diversión",
            "unfavorable_1": "Gastos arriesgados",
            "work": "Movimientos profesionales, currículums, entrevistas."
        },
        "Gemini": {
            "beauty": "Manicura — ¡gran momento!",
            "desc": "Luna en Géminis — comunicación, información, movimiento. Muchos contactos, poca profundidad.",
            "favorable_0": "Negociaciones",
            "favorable_1": "Viajes",
            "favorable_2": "Socializar",
            "health": "Brazos, pulmones, sistema nervioso.",
            "love": "Coqueteo, ligereza, mensajes.",
            "unfavorable_0": "Análisis profundo",
            "unfavorable_1": "Decisiones serias",
            "work": "Correos, llamadas, reuniones."
        },
        "Leo": {
            "beauty": "Corte de pelo — el cabello estará lujoso.",
            "desc": "Luna en Leo — creatividad, celebración, generosidad. Sé una estrella, brilla, ¡crea!",
            "favorable_0": "Creatividad",
            "favorable_1": "Celebraciones",
            "favorable_2": "Publicidad",
            "health": "Corazón, espalda. Cardio.",
            "love": "Da, sorprende, ¡admira!",
            "unfavorable_0": "Modestia",
            "unfavorable_1": "Economía",
            "work": "Presentaciones, discursos."
        },
        "Libra": {
            "beauty": "¡Todo para la belleza — sí!",
            "desc": "Luna en Libra — armonía, belleza, asociación. Tiempo para la estética y el equilibrio.",
            "favorable_0": "Belleza",
            "favorable_1": "Asociaciones",
            "favorable_2": "Arte",
            "health": "Riñones, zona lumbar. Equilibrio.",
            "love": "¡Perfecto para citas!",
            "unfavorable_0": "Soledad",
            "unfavorable_1": "Conflictos",
            "work": "Diseño, negociaciones, contratos."
        },
        "Pisces": {
            "beauty": "Hidratación — esencial.",
            "desc": "Luna en Piscis — sueños, intuición, compasión. Sensibilidad fina, creatividad, retiro.",
            "favorable_0": "Creatividad",
            "favorable_1": "Meditación",
            "favorable_2": "Procedimientos acuáticos",
            "health": "Pies, linfa. Sauna, baño.",
            "love": "Romance, soñar juntos.",
            "unfavorable_0": "Alcohol",
            "unfavorable_1": "Decisiones importantes",
            "unfavorable_2": "Asuntos legales",
            "work": "Creatividad, música, fotografía."
        },
        "Sagittarius": {
            "beauty": "Corte de pelo — sí, el pelo crece rápido.",
            "desc": "Luna en Sagitario — optimismo, viajes, filosofía. Expande tus horizontes.",
            "favorable_0": "Viajes",
            "favorable_1": "Deportes",
            "favorable_2": "Educación",
            "health": "Caderas, hígado. Ocio activo.",
            "love": "Aventuras juntos.",
            "unfavorable_0": "Rutina",
            "unfavorable_1": "Detalles",
            "unfavorable_2": "Asuntos legales",
            "work": "Grandes planes, educación."
        },
        "Scorpio": {
            "beauty": "¡No te cortes! El cabello estará rebelde.",
            "desc": "Luna en Escorpio — profundidad, transformación, pasión. Emociones poderosas y deseo de control.",
            "favorable_0": "Investigación",
            "favorable_1": "Transformación",
            "favorable_2": "Sexo",
            "health": "Sistema reproductivo.",
            "love": "Pasión profunda, pero celos.",
            "unfavorable_0": "Cirugía",
            "unfavorable_1": "Comenzar cosas nuevas",
            "work": "Investigaciones, finanzas, estrategia."
        },
        "Taurus": {
            "beauty": "Corte de pelo — ¡sí! El cabello crece espeso.",
            "desc": "Luna en Tauro — estabilidad, comodidad, placeres. Mejor momento para la belleza y la cocina.",
            "favorable_0": "Cocina",
            "favorable_1": "Belleza",
            "favorable_2": "Finanzas",
            "health": "Garganta, glándula tiroides.",
            "love": "Cena romántica, regalos.",
            "unfavorable_0": "Cambios",
            "unfavorable_1": "Riesgo",
            "work": "Asuntos financieros, tareas estables."
        },
        "Virgo": {
            "beauty": "Manicura y pedicura — ¡perfecto!",
            "desc": "Luna en Virgo — orden, análisis, salud. Pon orden, ve al médico, detalla.",
            "favorable_0": "Limpieza",
            "favorable_1": "Salud",
            "favorable_2": "Análisis",
            "health": "Intestinos. Diagnóstico.",
            "love": "No es el mejor momento para el romance.",
            "unfavorable_0": "Pereza",
            "unfavorable_1": "Caos",
            "unfavorable_2": "Romance",
            "work": "Trabajo detallado, informes."
        }
    },
    "pt": {
        "Aquarius": {
            "beauty": "Experimentos com a imagem — sim!",
            "desc": "Lua em Aquário — liberdade, originalidade, tecnologia. Tempo para experimentos e amizade.",
            "favorable_0": "Tecnologia",
            "favorable_1": "Amizade",
            "favorable_2": "Inovação",
            "health": "Canelas, vasos. Alongamento.",
            "love": "Amizade acima da paixão.",
            "unfavorable_0": "Tradições",
            "unfavorable_1": "Rotina",
            "work": "TI, startups, networking."
        },
        "Aries": {
            "beauty": "Não corte o cabelo — ele crescerá áspero.",
            "desc": "Lua em Áries — impulsividade, sede de ação. Bom para começar coisas, não para paciência.",
            "favorable_0": "Esportes",
            "favorable_1": "Novos começos",
            "favorable_2": "Competições",
            "health": "Cabeça, rosto. Evite superaquecimento.",
            "love": "Paixão, mas não conversas longas.",
            "unfavorable_0": "Paciência",
            "unfavorable_1": "Negociações longas",
            "work": "Decisões rápidas, início de projetos."
        },
        "Cancer": {
            "beauty": "Hidratação, cuidados com o cabelo — sim!",
            "desc": "Lua em Câncer — lar, família, emoções. A época mais aconchegante. Cozinhe, limpe, cuide.",
            "favorable_0": "Lar",
            "favorable_1": "Família",
            "favorable_2": "Cuidados com o corpo",
            "health": "Peito, estômago. Comida leve.",
            "love": "Emoções profundas, cuidado.",
            "unfavorable_0": "Ambições profissionais",
            "unfavorable_1": "Projetos arriscados",
            "work": "Escritório em casa, atendimento ao cliente."
        },
        "Capricorn": {
            "beauty": "Manicure — as unhas ficarão fortes.",
            "desc": "Lua em Capricórnio — disciplina, carreira, responsabilidade. Tempo sério para assuntos sérios.",
            "favorable_0": "Carreira",
            "favorable_1": "Planejamento",
            "favorable_2": "Disciplina",
            "health": "Ossos, joelhos, dentes.",
            "love": "Conversas sérias sobre o futuro.",
            "unfavorable_0": "Diversão",
            "unfavorable_1": "Gastos arriscados",
            "work": "Movimentos de carreira, currículos, entrevistas."
        },
        "Gemini": {
            "beauty": "Manicure — ótima hora!",
            "desc": "Lua em Gêmeos — comunicação, informação, movimento. Muitos contatos, pouca profundidade.",
            "favorable_0": "Negociações",
            "favorable_1": "Viagens",
            "favorable_2": "Socialização",
            "health": "Braços, pulmões, sistema nervoso.",
            "love": "Flertes, leveza, mensagens de texto.",
            "unfavorable_0": "Análise profunda",
            "unfavorable_1": "Decisões sérias",
            "work": "E-mails, ligações, reuniões."
        },
        "Leo": {
            "beauty": "Corte de cabelo — o cabelo ficará luxuoso.",
            "desc": "Lua em Leão — criatividade, celebração, generosidade. Seja uma estrela, brilhe, crie!",
            "favorable_0": "Criatividade",
            "favorable_1": "Celebrações",
            "favorable_2": "Publicidade",
            "health": "Coração, costas. Cardio.",
            "love": "Dê, surpreenda, admire!",
            "unfavorable_0": "Modéstia",
            "unfavorable_1": "Economia",
            "work": "Apresentações, discursos."
        },
        "Libra": {
            "beauty": "Tudo para a beleza — sim!",
            "desc": "Lua em Libra — harmonia, beleza, parceria. Tempo para estética e equilíbrio.",
            "favorable_0": "Beleza",
            "favorable_1": "Parcerias",
            "favorable_2": "Arte",
            "health": "Rins, lombar. Equilíbrio.",
            "love": "Perfeito para encontros!",
            "unfavorable_0": "Solidão",
            "unfavorable_1": "Conflitos",
            "work": "Design, negociações, contratos."
        },
        "Pisces": {
            "beauty": "Hidratação — essencial.",
            "desc": "Lua em Peixes — sonhos, intuição, compaixão. Sensibilidade sutil, criatividade, retraimento.",
            "favorable_0": "Criatividade",
            "favorable_1": "Meditação",
            "favorable_2": "Procedimentos aquáticos",
            "health": "Pés, linfa. Sauna, banho.",
            "love": "Romance, sonhar juntos.",
            "unfavorable_0": "Álcool",
            "unfavorable_1": "Decisões importantes",
            "unfavorable_2": "Assuntos jurídicos",
            "work": "Criatividade, música, fotografia."
        },
        "Sagittarius": {
            "beauty": "Corte de cabelo — sim, o cabelo cresce rápido.",
            "desc": "Lua em Sagitário — otimismo, viagens, filosofia. Expanda seus horizontes.",
            "favorable_0": "Viagens",
            "favorable_1": "Esportes",
            "favorable_2": "Educação",
            "health": "Quadris, fígado. Lazer ativo.",
            "love": "Aventuras juntos.",
            "unfavorable_0": "Rotina",
            "unfavorable_1": "Detalhes",
            "unfavorable_2": "Assuntos jurídicos",
            "work": "Grandes planos, educação."
        },
        "Scorpio": {
            "beauty": "Não corte! O cabelo ficará rebelde. (Don't cut! Hair will be unruly.)",
            "desc": "Lua em Escorpião — profundidade, transformação, paixão. Emoções poderosas e desejo de controle. (Moon in Scorpio — depth, transformation, passion. Powerful emotions and desire for control.)",
            "favorable_0": "Pesquisa (Research)",
            "favorable_1": "Transformação (Transformation)",
            "favorable_2": "Sexo (Sex)",
            "health": "Sistema reprodutivo. (Reproductive system.)",
            "love": "Paixão profunda, mas ciúme. (Deep passion, but jealousy.)",
            "unfavorable_0": "Cirurgia (Surgery)",
            "unfavorable_1": "Começar coisas novas (Starting new things)",
            "work": "Investigações, finanças, estratégia. (Investigations, finance, strategy.)"
        },
        "Taurus": {
            "beauty": "Corte de cabelo — sim! O cabelo cresce espesso.",
            "desc": "Lua em Touro — estabilidade, conforto, prazeres. Melhor momento para beleza e culinária.",
            "favorable_0": "Culinária",
            "favorable_1": "Beleza",
            "favorable_2": "Finanças",
            "health": "Garganta, glândula tireoide.",
            "love": "Jantar romântico, presentes.",
            "unfavorable_0": "Mudanças",
            "unfavorable_1": "Risco",
            "work": "Assuntos financeiros, tarefas estáveis."
        },
        "Virgo": {
            "beauty": "Manicure e pedicure — perfeito!",
            "desc": "Lua em Virgem — ordem, análise, saúde. Arrume, vá ao médico, detalhe.",
            "favorable_0": "Limpeza",
            "favorable_1": "Saúde",
            "favorable_2": "Análise",
            "health": "Intestinos. Diagnósticos.",
            "love": "Não é o melhor momento para romance.",
            "unfavorable_0": "Preguiça",
            "unfavorable_1": "Caos",
            "unfavorable_2": "Romance",
            "work": "Trabalho detalhado, relatórios."
        }
    },
    "tr": {
        "Aquarius": {
            "beauty": "İmaj deneyleri — evet!",
            "desc": "Kova burcunda Ay — özgürlük, özgünlük, teknoloji. Deneyler ve arkadaşlık zamanı.",
            "favorable_0": "Teknoloji",
            "favorable_1": "Arkadaşlık",
            "favorable_2": "İnovasyon",
            "health": "İncikler, damarlar. Esneme.",
            "love": "Arkadaşlık tutkudan önce.",
            "unfavorable_0": "Gelenekler",
            "unfavorable_1": "Rutin",
            "work": "IT, startuplar, networking."
        },
        "Aries": {
            "beauty": "Saçını kesme — sertleşir.",
            "desc": "Koç Burcunda Ay — dürtüsellik, eylem susuzluğu. Bir şeylere başlamak için iyi, sabır için değil.",
            "favorable_0": "Spor",
            "favorable_1": "Yeni başlangıçlar",
            "favorable_2": "Yarışmalar",
            "health": "Baş, yüz. Aşırı ısınmadan kaçının.",
            "love": "Tutku, ama uzun konuşmalar değil.",
            "unfavorable_0": "Sabır",
            "unfavorable_1": "Uzun müzakereler",
            "work": "Hızlı kararlar, proje başlangıçları."
        },
        "Cancer": {
            "beauty": "Nemlendirme, saç bakımı — evet!",
            "desc": "Yengeç'te Ay — ev, aile, duygular. En rahat zaman. Pişir, temizle, ilgilen.",
            "favorable_0": "Ev",
            "favorable_1": "Aile",
            "favorable_2": "Vücut bakımı",
            "health": "Göğüs, mide. Hafif yiyecek.",
            "love": "Derin duygular, ilgi.",
            "unfavorable_0": "Kariyer hırsları",
            "unfavorable_1": "Riskli projeler",
            "work": "Ev ofisi, müşteri bakımı."
        },
        "Capricorn": {
            "beauty": "Manikür — tırnaklar güçlü olacak.",
            "desc": "Oğlak burcunda Ay — disiplin, kariyer, sorumluluk. Ciddi meseleler için ciddi zaman.",
            "favorable_0": "Kariyer",
            "favorable_1": "Planlama",
            "favorable_2": "Disiplin",
            "health": "Kemikler, dizler, dişler.",
            "love": "Gelecek hakkında ciddi konuşmalar.",
            "unfavorable_0": "Eğlence",
            "unfavorable_1": "Riskli harcamalar",
            "work": "Kariyer adımları, özgeçmişler, mülakatlar."
        },
        "Gemini": {
            "beauty": "Manikür — harika zaman!",
            "desc": "İkizler'de Ay — iletişim, bilgi, hareket. Çok temas, az derinlik.",
            "favorable_0": "Müzakereler",
            "favorable_1": "Seyahatler",
            "favorable_2": "Sosyalleşme",
            "health": "Kollar, akciğerler, sinir sistemi.",
            "love": "Flört, hafiflik, mesajlaşma.",
            "unfavorable_0": "Derin analiz",
            "unfavorable_1": "Ciddi kararlar",
            "work": "E-postalar, aramalar, toplantılar."
        },
        "Leo": {
            "beauty": "Saç kesimi — saçlar lüks olacak.",
            "desc": "Aslan burcunda Ay — yaratıcılık, kutlama, cömertlik. Bir yıldız ol, parla, yarat!",
            "favorable_0": "Yaratıcılık",
            "favorable_1": "Kutlamalar",
            "favorable_2": "Publisite",
            "health": "Kalp, sırt. Kardiyo.",
            "love": "Ver, şaşırt, hayran ol!",
            "unfavorable_0": "Mütevazılık",
            "unfavorable_1": "Tasarruf",
            "work": "Sunumlar, konuşmalar."
        },
        "Libra": {
            "beauty": "Güzellik için her şey — evet!",
            "desc": "Terazi'de Ay — uyum, güzellik, ortaklık. Estetik ve denge zamanı.",
            "favorable_0": "Güzellik",
            "favorable_1": "Ortaklıklar",
            "favorable_2": "Sanat",
            "health": "Böbrekler, bel. Denge.",
            "love": "Randevular için mükemmel!",
            "unfavorable_0": "Yalnızlık",
            "unfavorable_1": "Çatışmalar",
            "work": "Tasarım, müzakereler, sözleşmeler."
        },
        "Pisces": {
            "beauty": "Nemlendirme — zorunlu.",
            "desc": "Balık Burcunda Ay — hayaller, sezgi, şefkat. İnce duyarlılık, yaratıcılık, içe kapanma.",
            "favorable_0": "Yaratıcılık",
            "favorable_1": "Meditasyon",
            "favorable_2": "Su tedavileri",
            "health": "Ayaklar, lenf. Sauna, banyo.",
            "love": "Romantizm, birlikte hayal kurmak.",
            "unfavorable_0": "Alkol",
            "unfavorable_1": "Önemli kararlar",
            "unfavorable_2": "Hukuki işler",
            "work": "Yaratıcılık, müzik, fotoğrafçılık."
        },
        "Sagittarius": {
            "beauty": "Saç kesimi — evet, saç hızlı uzar.",
            "desc": "Yay burcunda Ay — iyimserlik, seyahat, felsefe. Ufkunu genişlet.",
            "favorable_0": "Seyahat",
            "favorable_1": "Spor",
            "favorable_2": "Eğitim",
            "health": "Kalçalar, karaciğer. Aktif dinlenme.",
            "love": "Birlikte maceralar.",
            "unfavorable_0": "Rutin",
            "unfavorable_1": "Detaylar",
            "unfavorable_2": "Hukuki işler",
            "work": "Büyük planlar, eğitim."
        },
        "Scorpio": {
            "beauty": "Kesme! Saçlar asi olacak.",
            "desc": "Ay Akrep'te — derinlik, dönüşüm, tutku. Güçlü duygular ve kontrol arzusu.",
            "favorable_0": "Araştırma",
            "favorable_1": "Dönüşüm",
            "favorable_2": "Seks",
            "health": "Üreme sistemi.",
            "love": "Derin tutku, ama kıskançlık.",
            "unfavorable_0": "Ameliyatlar",
            "unfavorable_1": "Yeni şeylere başlamak",
            "work": "Soruşturmalar, finans, strateji."
        },
        "Taurus": {
            "beauty": "Saç kesimi — evet! Saçlar gür çıkar.",
            "desc": "Boğa burcunda Ay — istikrar, rahatlık, zevkler. Güzellik ve yemek pişirme için en iyi zaman.",
            "favorable_0": "Yemek pişirme",
            "favorable_1": "Güzellik",
            "favorable_2": "Finans",
            "health": "Boğaz, tiroid bezi.",
            "love": "Romantik akşam yemeği, hediyeler.",
            "unfavorable_0": "Değişiklikler",
            "unfavorable_1": "Risk",
            "work": "Mali işler, istikrarlı görevler."
        },
        "Virgo": {
            "beauty": "Manikür ve pedikür — mükemmel!",
            "desc": "Başak burcunda Ay — düzen, analiz, sağlık. Düzenle, doktora git, detaylandır.",
            "favorable_0": "Temizlik",
            "favorable_1": "Sağlık",
            "favorable_2": "Analiz",
            "health": "Bağırsaklar. Teşhis.",
            "love": "Romantizm için en iyi zaman değil.",
            "unfavorable_0": "Tembellik",
            "unfavorable_1": "Kaos",
            "unfavorable_2": "Romantizm",
            "work": "Detaylı çalışma, raporlar."
        }
    },
    "uk": {
        "Aquarius": {
            "beauty": "Експерименти з образом — так!",
            "desc": "Місяць у Водолії — свобода, оригінальність, технології. Час для експериментів і дружби.",
            "favorable_0": "Технології",
            "favorable_1": "Дружба",
            "favorable_2": "Інновації",
            "health": "Гомілки, судини. Розтяжка.",
            "love": "Дружба важливіша за пристрасть.",
            "unfavorable_0": "Традиції",
            "unfavorable_1": "Рутина",
            "work": "IT, стартапи, нетворкінг."
        },
        "Aries": {
            "beauty": "Не стрижіть волосся — воно стане жорстким.",
            "desc": "Місяць в Овні — імпульсивність, спрага дій. Добре для початку справ, але не для терпіння.",
            "favorable_0": "Спорт",
            "favorable_1": "Нові починання",
            "favorable_2": "Змагання",
            "health": "Голова, обличчя. Уникайте перегріву.",
            "love": "Пристрасть, але не довгі розмови.",
            "unfavorable_0": "Терпіння",
            "unfavorable_1": "Довгі переговори",
            "work": "Швидкі рішення, запуск проєктів."
        },
        "Cancer": {
            "beauty": "Зволоження, догляд за волоссям — так!",
            "desc": "Місяць у Раку — дім, родина, емоції. Найзатишніший час. Готуй, прибирай, піклуйся.",
            "favorable_0": "Дім",
            "favorable_1": "Родина",
            "favorable_2": "Догляд за тілом",
            "health": "Груди, шлунок. Легка їжа.",
            "love": "Глибокі емоції, турбота.",
            "unfavorable_0": "Кар'єрні амбіції",
            "unfavorable_1": "Ризиковані проєкти",
            "work": "Домашній офіс, турбота про клієнтів."
        },
        "Capricorn": {
            "beauty": "Манікюр — нігті будуть міцні.",
            "desc": "Місяць у Козерозі — дисципліна, кар'єра, відповідальність. Серйозний час для серйозних справ.",
            "favorable_0": "Кар'єра",
            "favorable_1": "Планування",
            "favorable_2": "Дисципліна",
            "health": "Кістки, коліна, зуби.",
            "love": "Серйозні розмови про майбутнє.",
            "unfavorable_0": "Веселощі",
            "unfavorable_1": "Ризиковані витрати",
            "work": "Кар'єрні кроки, резюме, співбесіди."
        },
        "Gemini": {
            "beauty": "Манікюр — чудовий час!",
            "desc": "Місяць у Близнюках — спілкування, інформація, рух. Багато контактів, мало глибини.",
            "favorable_0": "Переговори",
            "favorable_1": "Поїздки",
            "favorable_2": "Спілкування",
            "health": "Руки, легені, нервова система.",
            "love": "Флірт, легкість, переписки.",
            "unfavorable_0": "Глибокий аналіз",
            "unfavorable_1": "Серйозні рішення",
            "work": "Переписки, дзвінки, зустрічі."
        },
        "Leo": {
            "beauty": "Стрижка — волосся буде розкішне.",
            "desc": "Місяць у Леві — творчість, свято, щедрість. Будь зіркою, сяй, твори!",
            "favorable_0": "Творчість",
            "favorable_1": "Свята",
            "favorable_2": "Публічність",
            "health": "Серце, спина. Кардіо.",
            "love": "Даруй, дивуй, захоплюй!",
            "unfavorable_0": "Скромність",
            "unfavorable_1": "Економія",
            "work": "Презентації, виступи."
        },
        "Libra": {
            "beauty": "Все для краси — так!",
            "desc": "Місяць у Терезах — гармонія, краса, партнерство. Час для естетики та балансу.",
            "favorable_0": "Краса",
            "favorable_1": "Партнерства",
            "favorable_2": "Мистецтво",
            "health": "Нирки, поперек. Баланс.",
            "love": "Ідеально для побачень!",
            "unfavorable_0": "Самотність",
            "unfavorable_1": "Конфлікти",
            "work": "Дизайн, переговори, контракти."
        },
        "Pisces": {
            "beauty": "Зволоження — обов'язково.",
            "desc": "Місяць у Рибах — мрії, інтуїція, співчуття. Тонка чутливість, творчість, заглиблення в себе.",
            "favorable_0": "Творчість",
            "favorable_1": "Медитація",
            "favorable_2": "Водні процедури",
            "health": "Ступні, лімфа. Лазня, ванна.",
            "love": "Романтика, мрії вдвох.",
            "unfavorable_0": "Алкоголь",
            "unfavorable_1": "Важливі рішення",
            "unfavorable_2": "Юридичні справи",
            "work": "Творчість, музика, фотографія."
        },
        "Sagittarius": {
            "beauty": "Стрижка — так, волосся росте швидко.",
            "desc": "Місяць у Стрільці — оптимізм, подорожі, філософія. Розширюй горизонти.",
            "favorable_0": "Подорожі",
            "favorable_1": "Спорт",
            "favorable_2": "Навчання",
            "health": "Стегна, печінка. Активний відпочинок.",
            "love": "Пригоди вдвох.",
            "unfavorable_0": "Рутина",
            "unfavorable_1": "Деталі",
            "unfavorable_2": "Юридичні справи",
            "work": "Масштабні плани, навчання."
        },
        "Scorpio": {
            "beauty": "Не стрижи! Волосся буде неслухняне.",
            "desc": "Місяць у Скорпіоні — глибина, трансформація, пристрасть. Потужні емоції та бажання контролю.",
            "favorable_0": "Дослідження",
            "favorable_1": "Трансформація",
            "favorable_2": "Секс",
            "health": "Репродуктивна система.",
            "love": "Глибока пристрасть, але ревнощі.",
            "unfavorable_0": "Операції",
            "unfavorable_1": "Починати нове",
            "work": "Розслідування, фінанси, стратегія."
        },
        "Taurus": {
            "beauty": "Стрижка — так! Волосся росте густо.",
            "desc": "Місяць у Тельці — стабільність, комфорт, задоволення. Найкращий час для краси та кулінарії.",
            "favorable_0": "Кулінарія",
            "favorable_1": "Краса",
            "favorable_2": "Фінанси",
            "health": "Горло, щитовидна залоза.",
            "love": "Романтична вечеря, подарунки.",
            "unfavorable_0": "Зміни",
            "unfavorable_1": "Ризик",
            "work": "Фінансові справи, стабільні завдання."
        },
        "Virgo": {
            "beauty": "Манікюр та педикюр — ідеально!",
            "desc": "Місяць у Діві — порядок, аналіз, здоров'я. Наведи порядок, сходи до лікаря, деталізуй.",
            "favorable_0": "Прибирання",
            "favorable_1": "Здоров'я",
            "favorable_2": "Аналіз",
            "health": "Кишечник. Діагностика.",
            "love": "Не найкращий час для романтики.",
            "unfavorable_0": "Лінь",
            "unfavorable_1": "Хаос",
            "unfavorable_2": "Романтика",
            "work": "Детальна робота, звіти."
        }
    }
}
EVENT_DATA_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "first_quarter": {
            "desc": "Tiempo de acción. Supera obstáculos, avanza hacia metas.",
            "title": "Primer cuarto"
        },
        "full_moon": {
            "desc": "Culminación del ciclo. Emociones al máximo. Termina tareas, celebra resultados.",
            "title": "Luna Llena"
        },
        "last_quarter": {
            "desc": "Deja ir y limpia. Tiempo para revisión y liberación de lo innecesario.",
            "title": "Último cuarto"
        },
        "mercury_direct": {
            "desc": "Comunicaciones restauradas. Se pueden firmar contratos.",
            "title": "Mercurio Directo"
        },
        "mercury_retro": {
            "desc": "Retrasos en la comunicación, fallos técnicos. Verifica todo dos veces.",
            "title": "Mercurio retrógrado"
        },
        "new_moon": {
            "desc": "Inicio de un nuevo ciclo. Perfecto para establecer metas e intenciones.",
            "title": "Luna Nueva"
        }
    },
    "pt": {
        "first_quarter": {
            "desc": "Hora de agir. Supere obstáculos, avance em direção às metas.",
            "title": "Primeiro Quarto"
        },
        "full_moon": {
            "desc": "Culminação do ciclo. Emoções no auge. Finalize tarefas, comemore resultados.",
            "title": "Lua Cheia"
        },
        "last_quarter": {
            "desc": "Deixe ir e limpe. Hora de revisar e se livrar do desnecessário.",
            "title": "Quarto Minguante"
        },
        "mercury_direct": {
            "desc": "Comunicações restauradas. Seguro assinar contratos.",
            "title": "Mercúrio Direto"
        },
        "mercury_retro": {
            "desc": "Atrasos na comunicação, falhas técnicas. Verifique tudo duas vezes.",
            "title": "Mercúrio Retrógrado"
        },
        "new_moon": {
            "desc": "Início de um novo ciclo. Perfeito para definir metas e intenções.",
            "title": "Lua Nova"
        }
    },
    "tr": {
        "first_quarter": {
            "desc": "Harekete geçme zamanı. Engelleri aş, hedeflere doğru ilerle.",
            "title": "İlk Çeyrek"
        },
        "full_moon": {
            "desc": "Döngü zirvesi. Duygular zirvede. İşleri bitir, sonuçları kutla.",
            "title": "Dolunay"
        },
        "last_quarter": {
            "desc": "Bırak ve arın. Gözden geçirme ve gereksizden kurtulma zamanı.",
            "title": "Son Çeyrek"
        },
        "mercury_direct": {
            "desc": "İletişim düzeldi. Sözleşme imzalamak güvenli.",
            "title": "Merkür Düz"
        },
        "mercury_retro": {
            "desc": "İletişim gecikmeleri, teknik aksaklıklar. Her şeyi iki kez kontrol et.",
            "title": "Merkür Retrosu"
        },
        "new_moon": {
            "desc": "Yeni bir döngünün başlangıcı. Hedefler ve niyetler belirlemek için mükemmel.",
            "title": "Yeni Ay"
        }
    },
    "uk": {
        "first_quarter": {
            "desc": "Час дій. Долай перешкоди, рухайся до цілей.",
            "title": "Перша чверть"
        },
        "full_moon": {
            "desc": "Кульмінація циклу. Емоції на піку. Завершуй справи, святкуй результати.",
            "title": "Повня"
        },
        "last_quarter": {
            "desc": "Відпускай і очищуй. Час для ревізії та позбавлення від зайвого.",
            "title": "Остання чверть"
        },
        "mercury_direct": {
            "desc": "Комунікації відновлюються. Можна підписувати договори.",
            "title": "Меркурій директний"
        },
        "mercury_retro": {
            "desc": "Затримки в комунікаціях, збої техніки. Перевіряй все двічі.",
            "title": "Меркурій ретроградний"
        },
        "new_moon": {
            "desc": "Початок нового циклу. Ідеально для постановки цілей та намірів.",
            "title": "Новолуння"
        }
    }
}
PHASE_NAMES_I18N: dict[str, dict[str, dict[str, str]]] = {
    "es": {
        "0": {
            "name": "Luna Nueva"
        },
        "1": {
            "name": "Cuarto Creciente"
        },
        "2": {
            "name": "Cuarto Creciente"
        },
        "3": {
            "name": "Gibosa creciente"
        },
        "4": {
            "name": "Luna Llena"
        },
        "5": {
            "name": "Gibosa menguante"
        },
        "6": {
            "name": "Cuarto menguante"
        },
        "7": {
            "name": "Cuarto Menguante"
        }
    },
    "pt": {
        "0": {
            "name": "Lua Nova"
        },
        "1": {
            "name": "Lua Crescente"
        },
        "2": {
            "name": "Quarto Crescente"
        },
        "3": {
            "name": "Gibosa Crescente"
        },
        "4": {
            "name": "Lua Cheia"
        },
        "5": {
            "name": "Gibosa Minguante"
        },
        "6": {
            "name": "Quarto Minguante"
        },
        "7": {
            "name": "Crescente Minguante"
        }
    },
    "tr": {
        "0": {
            "name": "Yeni Ay"
        },
        "1": {
            "name": "Hilal"
        },
        "2": {
            "name": "İlk Dördün"
        },
        "3": {
            "name": "Büyüyen Şişkin Ay"
        },
        "4": {
            "name": "Dolunay"
        },
        "5": {
            "name": "Küçülen Şişkin"
        },
        "6": {
            "name": "Son Dördün"
        },
        "7": {
            "name": "Eski Ay"
        }
    },
    "uk": {
        "0": {
            "name": "Новолуння"
        },
        "1": {
            "name": "Молодий місяць"
        },
        "2": {
            "name": "Перша чверть"
        },
        "3": {
            "name": "Прибуваючий Гіббус"
        },
        "4": {
            "name": "Повний місяць"
        },
        "5": {
            "name": "Спадаючий опуклий"
        },
        "6": {
            "name": "Остання чверть"
        },
        "7": {
            "name": "Старий місяць"
        }
    }
}
