README = """
#  SISTEMA DE DIAGNÓSTICO AGRÍCOLA – Versión Final 2025
Diagnóstico automático de enfermedades en cultivos + análisis científico desde PubMed.

------------------------------------------------------------

##  Descripción general

Este proyecto implementa un sistema completo de diagnóstico agrícola basado en:

###  1. Análisis de artículos de PubMed
- Búsqueda automática de artículos (BioPython + parche SSL para Windows).
- Descarga de títulos y resúmenes.
- Generación automática de:
  ✔ Nube de palabras  
  ✔ Histograma de frecuencia  
- Exportación a CSV.

###  2. Diagnóstico Integrado
- Detecta cultivo, síntomas, causas y virus desde texto libre.
- Genera búsqueda científica inteligente en PubMed según síntomas.
- Recupera artículos relevantes como apoyo diagnóstico.

###  3. Arquitectura modular del sistema
Cada componente está separado en módulos:

    extractor.py
    diagnostico_integrado.py
    pubmed_downloader.py
    nlp_analyzer.py
    main_ii.py

------------------------------------------------------------

##  Estructura del proyecto

proyecto_diagnostico_agricola/
│
├── extractor.py               # Detecta síntomas, causas y virus
├── diagnostico_integrado.py   # Genera diagnóstico + PubMed
├── pubmed_downloader.py       # Búsqueda PubMed (SSL parcheado)
├── nlp_analyzer.py            # Nube de palabras y análisis NLP
├── main_ii.py                 # Menú principal
│
├── articulos_pubmed.csv       # (Autogenerado)
├── palabras.png               # Nube de palabras
├── histograma.png             # Histograma
│
└── README.py                  # Este archivo

------------------------------------------------------------

##  Requisitos

python >= 3.9  
biopython  
matplotlib  
wordcloud  
nltk  

Instalación:

    pip install biopython matplotlib wordcloud nltk

Descarga de recursos NLTK:

    import nltk
    nltk.download('punkt')
    nltk.download('stopwords')

------------------------------------------------------------

##  Cómo ejecutar

Ejecuta el programa principal:

    python main_ii.py

Aparece el menú:

    === SISTEMA DE DIAGNÓSTICO AGRÍCOLA ===
    1. Analizar artículos de PubMed
    2. Diagnóstico integrado
    3. Salir

------------------------------------------------------------

##  MODO 1: Análisis de artículos de PubMed

Ejemplo de búsqueda:

    ToBRFV AND tomato AND viral disease

El sistema:
- Recupera artículos
- Crea:
    articulos_pubmed.csv
    palabras.png
    histograma.png

------------------------------------------------------------

##  MODO 2: Diagnóstico integrado

Ejemplo de uso:

    Mi cultivo de papa tiene las hojas enrolladas y amarillas.

Resultado esperado:
- Cultivo detectado: papa
- Síntomas: enrollamiento, amarillamiento
- Virus probable: PLRV
- Genera query PubMed:
  
      papa AND leaf rolling AND yellowing AND plant disease

- Muestra artículos relevantes

------------------------------------------------------------

##  Cómo funciona el sistema

### ✔ Extracción de síntomas
Basado en reglas optimizadas y un diccionario ampliado.

### ✔ Causas probables
Clasificación automática:
- virus  
- hongos  
- bacterias  
- deficiencias  

### ✔ Virus posibles
Reglas directas:
- Papa + enrollamiento → PLRV  
- Tomate + mosaico → ToBRFV  
- Banano + enanismo → BBTV  

### ✔ Cultivo detectado
Heurística simple:  
["papa", "tomate", "banano", "maíz", "cacao"]

### ✔ Query PubMed inteligente
    cultivo + síntomas + causas + "plant disease"

------------------------------------------------------------

##  Parche SSL (Windows)

El módulo `pubmed_downloader.py` incluye parche SSL para evitar:

    SSL: CERTIFICATE_VERIFY_FAILED

Permite conexión segura a PubMed sin certificados manuales.

------------------------------------------------------------

##  Objetivo del proyecto

Brindar una herramienta de:
- diagnóstico preliminar
- análisis científico automatizado
- soporte a técnicos agrícolas
- sin dependencias pesadas como PyTorch

Ideal para estudiantes, agrónomos y bioinformáticos.

------------------------------------------------------------

##  Limitaciones

- No reemplaza diagnóstico profesional.
- Depende de la calidad del texto ingresado.
- Las reglas pueden ampliarse.

------------------------------------------------------------

##  Próximas mejoras sugeridas

- Modelo ML liviano para síntomas.
- Ampliar diccionario de cultivos.
- Mejorar ranking de artículos científicos.

------------------------------------------------------------

##  Autor
Karina Andrea Ardila Pulgarín
Lina Maria Gomez Cardona
UNIVERSIDAD NACIONAL DE COLOMBIA --- SEDE MEDELLÍN
Versión final del sistema de diagnóstico agrícola — 2025.
"""
