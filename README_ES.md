# Trayectorias desacopladas: intensidad de CO₂ fósil, emisiones de uso de la tierra y dinámica de bosques en Sudamérica

Este repositorio contiene el flujo reproducible de datos para el proyecto “Trayectorias desacopladas: intensidad de CO₂ fósil, emisiones de uso de la tierra y dinámica de bosques en Sudamérica (2000–2020)”. Se enfoca en tres entregables:

1. Extracciones armonizadas de CEPALSTAT, los Indicadores de Desarrollo del Banco Mundial y FAOSTAT.
2. Tablas listas para el análisis que resumen la dinámica de la intensidad de CO₂ fósil, la superficie forestal y las emisiones LULUCF.
3. Scripts en Python que reconstruyen los paneles, exportan versiones públicas de los datos y regeneran las figuras del artículo.

El estudio compara doce países sudamericanos en tres años de referencia (2000, 2010, 2020) y en dos décadas de cambio (2000–2010 y 2010–2020). Con estos paneles se estiman regresiones lineales que vinculan:
- los cambios decenales en la intensidad de CO₂ fósil del PIB con la dinámica forestal, los desplazamientos en la matriz eléctrica y el crecimiento del ingreso, y
- los cambios decenales en las emisiones LULUCF per cápita con la dinámica de los bosques y la participación de la agricultura en el PIB.

El mensaje central es que la descarbonización energética y la mitigación por uso de la tierra avanzan por caminos diferentes—en ocasiones divergentes. Algunos países exhiben intensidades bajas de CO₂ fósil aun cuando enfrentan pérdida de bosques y focos LULUCF; por ello, los tableros de mitigación deben monitorear simultáneamente los componentes fósiles y de uso de la tierra para reflejar el progreso real.

## Estructura del repositorio

- `data_cepal/` – descargas crudas de CEPALSTAT más archivos ZIP y CSV intermedios que alimentan los modelos.
- `data_article/` – tablas públicas citadas en el manuscrito:
  - `master_forest_energy_analysis_panel.csv` – panel país–año (2000, 2010, 2020) con indicadores de energía, bosques y socioeconomía.
  - `south_america_delta_panel_analysis.csv` – panel de cambios decenales para 2000–2010 y 2010–2020.
  - `variables_codebook.csv` – descripciones, unidades y fuentes.
- `scripts/` – cadena completa de ETL y modelación. Componentes destacados:
  - `build_master_panel.py`, `build_extended_forest_energy_panel.py`, `build_variables_codebook.py` – crean las tablas principales en `data_cepal/` y exportan la versión pública en `data_article/`.
  - Módulos `*_extension.py` – incorporan covariables (gobernanza, comercio, socioeconomía y matriz energética).
  - `build_article_figures.py` – utiliza `data_article/` para recrear las figuras del artículo, guardándolas en `article/figures/` (directorio local ignorado por Git).
  - `regression_models.py` – rutinas para estimar las relaciones descritas en el texto.

## Uso

1. Cree un entorno de Python con las dependencias habituales (por ejemplo `python -m venv .venv && source .venv/bin/activate` seguido de `pip install pandas numpy matplotlib`).
2. Ejecute los scripts de `scripts/` para actualizar los datos:
   ```bash
   python scripts/build_master_panel.py
   python scripts/build_extended_forest_energy_panel.py
   python scripts/build_variables_codebook.py
   ```
   Estos comandos regeneran los CSV en `data_cepal/` y exportan el subconjunto público en `data_article/`.
3. (Opcional) Reproduzca las figuras del artículo:
   ```bash
   python scripts/build_article_figures.py
   ```
   Las salidas se guardan localmente en `article/figures/`.

Cada script informa su progreso mediante `cepalstat_client.logger`. Consulte los docstrings de `scripts/` para obtener detalles sobre argumentos y supuestos de procesamiento.
