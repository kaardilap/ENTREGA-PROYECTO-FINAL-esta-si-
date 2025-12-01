# main_ii.py - Menú principal (usa diagnostico_integrado, pubmed_downloader y nlp_analyzer)

from diagnostico_integrado import generar_diagnostico_integrado, imprimir_reporte_integrado
from pubmed_downloader import buscar_pubmed
import nlp_analyzer

def opcion_pubmed():
    query = input("\n Ingresa tu búsqueda para PubMed (ej: ToBRFV AND tomato): ").strip()
    max_art = input("Cantidad máxima de artículos (default 5): ").strip()
    max_art = int(max_art) if max_art.isdigit() else 5
    print(f"\n Buscando artículos para: {query}")
    articulos = buscar_pubmed(query, max_articulos=max_art)
    if not articulos:
        print("No se encontraron artículos.:(\n")
        return
    # llamar al analizador (genera CSV, nube, histograma)
    nlp_analyzer.analizar_articulos(articulos, save_wordcloud_path="wordcloud.png", save_hist_path="histograma.png")

def opcion_diagnostico():
    texto = input("\n Ingrese el texto del usuario/foro: ").strip()
    reporte = generar_diagnostico_integrado(texto)
    imprimir_reporte_integrado(reporte)

def main():
    while True:
        print("\n=== SISTEMA DE DIAGNÓSTICO AGRÍCOLA ===")
        print("1. Analizar artículos de PubMed")
        print("2. Diagnóstico integrado")
        print("3. Salir")

        opcion = input("Selecciona una opción: ").strip()
        if opcion == "1":
            opcion_pubmed()
        elif opcion == "2":
            opcion_diagnostico()
        elif opcion == "3":
            print("Saliendo... Muchas gracias por usar nuestro servicio ¡Hasta luego!")
            break
        else:
            print("Opción inválida. Intenta nuevamente.")

if __name__ == "__main__":
    main()

