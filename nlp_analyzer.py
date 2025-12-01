# nlp_analyzer.py
# Analizador ligero para analizar lista de artículos (titulo+resumen)
# Genera: CSV (opcional), wordcloud.png y histograma.png
# Función pública: analizar_articulos(articulos, save_wordcloud_path, save_hist_path)

import re
from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
import csv
import os

SPANISH_STOPWORDS = {
    "de","la","el","y","en","los","las","por","con","para","se","del","una","un",
    "como","que","es","su","sus","entre","ha","han","este","esta","fue","son",
    "o","si","no","más","sobre","también","porque","cuando","desde","otros"
}

STOPWORDS = set(ENGLISH_STOP_WORDS) | SPANISH_STOPWORDS

def _limpiar(texto):
    if not texto:
        return ""
    t = texto.lower()
    t = re.sub(r"http\S+", " ", t)
    t = re.sub(r"[^a-záéíóúüñ0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t

def _tokens(texto):
    t = _limpiar(texto)
    if not t:
        return []
    toks = [w for w in t.split() if len(w) > 2 and w not in STOPWORDS and not w.isdigit()]
    return toks

def top_n_words(articulos, n=30):
    all_tokens = []
    for a in articulos:
        titulo = a.get("titulo","") or ""
        resumen = a.get("resumen","") or ""
        tokens = _tokens(titulo + " " + resumen)
        all_tokens.extend(tokens)
    c = Counter(all_tokens)
    return c.most_common(n)

def generar_wordcloud(freqs, path="wordcloud.png", width=800, height=400):
    if not freqs:
        print(" No hay términos para generar nube.")
        return
    wc = WordCloud(width=width, height=height, background_color="white", collocations=False)
    wc.generate_from_frequencies(dict(freqs))
    plt.figure(figsize=(width/100, height/100))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def generar_histograma(freqs, path="histograma.png", top_k=15):
    if not freqs:
        print(" No hay términos para generar histograma.")
        return
    palabras, cuentas = zip(*freqs[:top_k])
    plt.figure(figsize=(10,6))
    plt.bar(range(len(palabras)), cuentas)
    plt.xticks(range(len(palabras)), palabras, rotation=45, ha="right")
    plt.title("Términos más frecuentes")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

def analizar_articulos(articulos, save_wordcloud_path="wordcloud.png", save_hist_path="histograma.png", save_csv=True):
    """
    articulos: lista de dicts con 'titulo' y 'resumen'
    Genera archivos en el directorio actual y devuelve top tokens.
    """
    if save_csv:
        csv_path = "articulos_pubmed.csv"
        try:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["titulo","resumen"])
                for a in articulos:
                    w.writerow([a.get("titulo",""), a.get("resumen","")])
            print(f" CSV guardado en: {os.path.abspath(csv_path)}")
        except Exception as e:
            print(" Error guardando CSV:", e)

    top = top_n_words(articulos, n=50)
    if not top:
        print("️ No se encontraron términos para analizar.")
        return top

    print("\n Palabras más frecuentes (top 20):")
    for w,c in top[:20]:
        print(f"  {w}: {c}")

    try:
        generar_wordcloud(top, path=save_wordcloud_path)
        print(" Nube guardada en:", save_wordcloud_path)
    except Exception as e:
        print(" Error generando nube:", e)

    try:
        generar_histograma(top, path=save_hist_path, top_k=15)
        print(" Histograma guardado en:", save_hist_path)
    except Exception as e:
        print("️ Error generando histograma:", e)

    return top
