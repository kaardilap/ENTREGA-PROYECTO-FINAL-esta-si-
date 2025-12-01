## extractor.py
# Un único extractor robusto: detecta cultivo, síntomas, causas, vectores y sugiere virus.
# No usa modelos pesados. Usa coincidencias por keywords + TF-IDF (scikit-learn).

import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --------------------------
# Catálogos ampliados
# --------------------------
CULTIVOS = {
    "tomate": ["tomate", "jitomate", "tomates", "tomato"],
    "papa": ["papa", "patata", "papas", "potato"],
    "banano": ["banano", "banana", "plátano", "platano"],
    "maíz": ["maíz", "maiz", "elote", "corn"],
    "cacao": ["cacao", "cacaotero"],
    "arroz": ["arroz", "rice"],
    "frijol": ["frijol", "bean"],
}

# Síntomas con sinónimos/frases comunes (español)
SINTOMAS = {
    "amarillamiento": ["amarillo", "amarillamiento", "clorosis", "hojas amarillas", "hoja amarilla"],
    "hojas enrolladas": ["hojas enrolladas", "enrolladas", "hojas rizadas", "enrollamiento", "leaf roll"],
    "enanismo": ["enanismo", "plantas enanas", "crecimiento atrofiado", "crecimiento lento"],
    "manchas en hojas": ["manchas en hojas", "manchas cafés", "spots", "punteado", "puntos en hojas"],
    "necrosis": ["necrosis", "tejido muerto", "zona necrótica"],
    "mosaico": ["mosaico", "patrón moteado", "manchas tipo mosaico", "mottling"],
    "deformación de hojas": ["deformadas", "deformación de hojas", "hojas torcidas", "hojas deformes"],
    "marchitez": ["marchitamiento", "marchitas", "hojas marchitas", "wilting"],
    "tizón": ["tizón", "blight", "hojas negras", "quemado"],
}

# Vectores y palabras asociadas
VECTORES = {
    "mosca blanca": ["mosca blanca", "mosquitas blancas", "whitefly", "bemisia"],
    "pulgón": ["pulgón", "pulgones", "aphid", "áfidos"],
    "trips": ["trips", "thrips"],
    "ácaros": ["ácaro", "ácaros", "mite"],
}

# Virus por cultivo (lista no exhaustiva, ampliable)
VIRUS_POR_CULTIVO = {
    "tomate": {
        "TYLCV (Tomato Yellow Leaf Curl Virus)": ["hojas enrolladas", "amarillamiento", "curl"],
        "ToBRFV (Tomato brown rugose fruit virus)": ["manchas en frutos", "necrosis", "manchas en hojas"],
        "TMV (Tobacco Mosaic Virus)": ["mosaico", "moteado", "deformación de hojas"],
    },
    "papa": {
        "PVY (Potato virus Y)": ["manchas en hojas", "mosaico", "amarillamiento", "deformación de hojas"],
        "PLRV (Potato leafroll virus)": ["hojas enrolladas", "amarillamiento", "enrollamiento"],
    },
    "banano": {
        "BBTV (Banana Bunchy Top Virus)": ["enanismo", "hojas erectas", "deformación de hojas"],
        "BSV (Banana Streak Virus)": ["mosaico", "manchas en hojas"],
    },
    "maíz": {
        "MSV (Maize streak virus)": ["mosaico", "manchas en hojas", "amarillamiento"],
    }
}

# --------------------------
# Helpers: limpieza
# --------------------------
def _clean(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"http\S+", " ", text)
    text = re.sub(r"[^a-záéíóúüñ0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# --------------------------
# Detección de cultivo
# --------------------------
def detectar_cultivo(texto):
    txt = _clean(texto)
    for cultivo, keys in CULTIVOS.items():
        for k in keys:
            if k in txt:
                return cultivo
    return None

# --------------------------
# Detección de síntomas (keywords + TF-IDF backup)
# --------------------------
def detectar_sintomas(texto):
    txt = _clean(texto)
    encontrados = set()

    # 1) matching por keywords
    for sintoma, variantes in SINTOMAS.items():
        for v in variantes:
            if v in txt:
                encontrados.add(sintoma)
                break

    # 2) si no hubo matches o para complementar, usar TF-IDF contra descripciones de síntoma
    if len(encontrados) == 0:
        try:
            corpus = [txt] + [" ".join(v) for v in SINTOMAS.values()]
            vect = TfidfVectorizer().fit_transform(corpus)
            sims = cosine_similarity(vect[0:1], vect[1:]).flatten()
            for sintoma, score in zip(list(SINTOMAS.keys()), sims):
                if score >= 0.20:
                    encontrados.add(sintoma)
        except Exception:
            # en caso de fallo de sklearn, retornamos lo que tengamos (puede ser vacío)
            pass

    return sorted(list(encontrados))

# --------------------------
# Detección de causas / vectores
# --------------------------
def detectar_causas(texto):
    txt = _clean(texto)
    causas = set()

    # vectores
    for vname, vkeys in VECTORES.items():
        for k in vkeys:
            if k in txt:
                causas.add(vname)
                break

    # palabras que sugieren hongos, bacterias, deficiencias, virus
    if any(x in txt for x in ["hongo", "hongos", "mildiu", "roya", "moho", "fungal"]):
        causas.add("hongos")
    if any(x in txt for x in ["bacteria", "bacterias", "psb", "pseudomonas", "bacterial"]):
        causas.add("bacterias")
    if any(x in txt for x in ["deficiencia", "falta de", "carencia", "nutricional", "nitrógeno", "hierro"]):
        causas.add("deficiencia nutricional")
    if any(x in txt for x in ["virus", "virosis", "viral"]):
        causas.add("virus")

    # si no determinamos causas, devolver vacío (diagnostico_integrado llenará con un fallback)
    return sorted(list(causas))

# --------------------------
# Inferir virus candidatos (reglas simples + conteo de coincidencias)
# --------------------------
def detectar_virus(sintomas, cultivo=None, texto=""):
    candidatos = []
    txt = _clean(texto)
    # preferir uso de cultivo si se proporciona
    if cultivo and cultivo in VIRUS_POR_CULTIVO:
        pool = VIRUS_POR_CULTIVO[cultivo]
    else:
        # consolidar todos los virus disponibles
        pool = {}
        for cdict in VIRUS_POR_CULTIVO.values():
            pool.update(cdict)

    for virus_name, patrones in pool.items():
        cuenta = 0
        # coincidencias en sintomas detectados
        for s in sintomas:
            for p in patrones:
                if p in s.lower() or p in txt:
                    cuenta += 1
                    break
        # si hay al menos 1 coincidencia, considerarlo (ajustable a >=2)
        if cuenta >= 1:
            candidatos.append(virus_name)

    # ordenar por nombre para estabilidad
    return sorted(list(set(candidatos)))
