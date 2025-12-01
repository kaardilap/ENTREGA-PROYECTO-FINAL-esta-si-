# pubmed_downloader.py
import ssl
import time

try:
    from Bio import Entrez
    BIOPYTHON_AVAILABLE = True
except Exception:
    BIOPYTHON_AVAILABLE = False

# Crear contexto SSL que NO verifica certificados (Windows)
ssl_context = ssl._create_unverified_context()
import urllib.request
https_handler = urllib.request.HTTPSHandler(context=ssl_context)
opener = urllib.request.build_opener(https_handler)
urllib.request.install_opener(opener)

Entrez_email_default = "demo@example.com"
Entrez_api_key = None

def _safe_str(x):
    try:
        return str(x)
    except Exception:
        return ""

def buscar_pubmed(query, max_articulos=5, email=None):
    email = email or Entrez_email_default
    if not BIOPYTHON_AVAILABLE:
        print(" BioPython no está instalado; activa biopython para PubMed.")
        return []

    Entrez.email = email
    if Entrez_api_key:
        Entrez.api_key = Entrez_api_key

    try:
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_articulos, sort="relevance")
        record = Entrez.read(handle)
        handle.close()
        ids = record.get("IdList", [])
        if not ids:
            return []

        handle = Entrez.efetch(db="pubmed", id=",".join(ids), rettype="abstract", retmode="xml")
        records = Entrez.read(handle)
        handle.close()

        articulos = []
        if "PubmedArticle" in records:
            for rec in records["PubmedArticle"]:
                art = rec.get("MedlineCitation", {}).get("Article", {})
                titulo = _safe_str(art.get("ArticleTitle", ""))
                abstract_data = art.get("Abstract", {}).get("AbstractText", [])
                if isinstance(abstract_data, list):
                    resumen = " ".join([_safe_str(x.get("_", x)) if isinstance(x, dict) else _safe_str(x) for x in abstract_data])
                else:
                    resumen = _safe_str(abstract_data)
                resumen = " ".join(resumen.split())
                articulos.append({"titulo": titulo, "resumen": resumen})
        return articulos

    except Exception as e:
        print("Error consultando PubMed:", e)
        return []
