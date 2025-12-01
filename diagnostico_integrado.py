# diagnostico_integrado.py
# Diagnóstico integrado: usa extractor.py y pubmed_downloader.py
# Generación de queries multi-nivel (específica -> general -> rescate)

from extractor import detectar_sintomas, detectar_causas, detectar_virus, detectar_cultivo
from pubmed_downloader import buscar_pubmed

# Traducciones simples de síntomas a términos en inglés que PubMed prefiere
_SYMPTOM_TRANSLATION = {
    "amarillamiento": "yellowing",
    "hojas enrolladas": "leaf curling",
    "enanismo": "stunting",
    "manchas en hojas": "leaf spots",
    "necrosis": "necrosis",
    "mosaico": "mosaic",
    "deformación de hojas": "leaf deformation",
    "marchitez": "wilting",
    "tizón": "blight",
}

def _traducir_sintomas(sintomas):
    out = []
    for s in sintomas:
        out.append(_SYMPTOM_TRANSLATION.get(s, s))
    return out

def _construir_query_nivel1(cultivo, sintomas_en, causas):
    # Query específica: cultivo + (sintomas) + (vector/causa) + keywords
    parts = []
    if cultivo:
        parts.append(f'"{cultivo}"')
    if sintomas_en:
        parts.append("(" + " OR ".join(f'"{s}"' for s in sintomas_en) + ")")
    if causas:
        # añadir las causas (vectores) ya en texto
        parts.append("(" + " OR ".join(f'"{c}"' for c in causas) + ")")
    # forzar palabras que ayudan en PubMed
    parts.append("(plant OR crop)")
    parts.append("(virus OR pathogen OR disease)")
    return " AND ".join(parts)

def _construir_query_nivel2(cultivo, sintomas_en):
    # Query general: cultivo + sintomas + plant disease
    parts = []
    if cultivo:
        parts.append(f'"{cultivo}"')
    if sintomas_en:
        parts.append("(" + " OR ".join(f'"{s}"' for s in sintomas_en) + ")")
    parts.append("plant disease")
    return " AND ".join(parts)

def _construir_query_nivel3(cultivo):
    # Rescue: cultivo + virus
    if cultivo:
        return f'"{cultivo}" AND virus'
    return "plant disease AND virus"

def buscar_articulos_relevantes(cultivo, sintomas, causas, texto_original, max_articulos=6, email=None):
    # preparar términos en inglés para síntomas
    sintomas_en = _traducir_sintomas(sintomas)

    # NIVEL 1 (más específico)
    q1 = _construir_query_nivel1(cultivo, sintomas_en, causas)
    arts = buscar_pubmed(q1, max_articulos=max_articulos, email=email)
    if arts:
        return arts, q1

    # NIVEL 2 (más general)
    q2 = _construir_query_nivel2(cultivo, sintomas_en)
    arts = buscar_pubmed(q2, max_articulos=max_articulos, email=email)
    if arts:
        return arts, q2

    # NIVEL 3 (rescate)
    q3 = _construir_query_nivel3(cultivo)
    arts = buscar_pubmed(q3, max_articulos=max_articulos, email=email)
    if arts:
        return arts, q3

    # fallback: búsqueda por texto original limitado
    q4 = f'"{texto_original}"'
    arts = buscar_pubmed(q4, max_articulos=min(4, max_articulos), email=email)
    if arts:
        return arts, q4

    # si todo falla, devolver vacío y query de plant disease
    return [], "plant disease"

def generar_diagnostico_integrado(texto_usuario, max_articulos=6, email=None):
    txt = texto_usuario or ""
    cultivo = detectar_cultivo(txt)
    sintomas = detectar_sintomas(txt)
    causas = detectar_causas(txt)
    virus = detectar_virus(sintomas, cultivo=cultivo, texto=txt)

    # si no hay causas detectadas, dejar un fallback (no vaciar)
    causas_out = causas if causas else ["virus", "hongos", "deficiencias nutricionales"]

    articulos, query_usada = buscar_articulos_relevantes(cultivo, sintomas, causas, txt, max_articulos=max_articulos, email=email)

    reporte = {
        "cultivo": cultivo,
        "sintomas": sintomas,
        "causas": causas_out,
        "virus": virus,
        "query": query_usada,
        "articulos": articulos
    }
    return reporte


def imprimir_reporte_integrado(r):
    # Wrapper de compatibilidad (mantener interfaz anterior)
    print("\n==============================")
    print("  REPORTE FINAL INTEGRADO ")
    print("==============================\n")

    print(" Cultivo detectado:", r["cultivo"] or "No detectado")

    print("\n Síntomas detectados:")
    if r["sintomas"]:
        for s in r["sintomas"]:
            print("  -", s)
    else:
        print("  (ninguno)")

    print("\n Causas probables:")
    for c in r["causas"]:
        print("  -", c)

    print("\n🟥 Virus posibles:")
    if r["virus"]:
        for v in r["virus"]:
            print("  -", v)
    else:
        print("  (ninguno detectado)")

    print("\n Query PubMed generado:")
    print(" ", r["query"], "\n")

    print("📚 Artículos científicos relevantes:")
    if not r["articulos"]:
        print("  ️ Ningún artículo encontrado.\n")
        return

    for art in r["articulos"]:
        print("\n  🔸", art.get("titulo", "<sin título>"))
        print("     ", art.get("resumen", "")[:300].replace("\n", " "), "...")
