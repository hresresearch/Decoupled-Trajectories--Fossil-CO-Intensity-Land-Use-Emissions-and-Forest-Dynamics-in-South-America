# Trayectorias desacopladas: intensidad de CO₂ fósil, emisiones de uso de la tierra y dinámica de bosques en Sudamérica

Este repositorio contiene datos y scripts para un análisis comparativo a nivel país sobre la evolución de la intensidad de CO₂ fósil del PIB, las emisiones de uso de la tierra, cambio de uso de la tierra y silvicultura (LULUCF) y la superficie forestal en doce países sudamericanos entre 2000 y 2020.

El proyecto combina estadísticas oficiales armonizadas de CEPALSTAT, los Indicadores de Desarrollo del Banco Mundial (WDI) y FAOSTAT para construir:
- un panel anual país–año para 2000, 2010 y 2020, y
- un panel de cambios decenales para 2000–2010 y 2010–2020.

Con estos paneles se estiman regresiones lineales sencillas que relacionan:
- los cambios decenales en la intensidad de CO₂ fósil del PIB con cambios en la superficie forestal, la participación de la hidroelectricidad en la generación eléctrica y el PIB per cápita, y
- los cambios decenales en las emisiones LULUCF per cápita con cambios en la superficie forestal y la participación de la agricultura en el valor agregado del PIB.

Los principales resultados empíricos son:
- las emisiones de CO₂ fósil por unidad de PIB disminuyeron en la mayoría de los países sudamericanos y se asocian significativamente con cambios en la matriz eléctrica y el crecimiento del ingreso, pero no con los cambios porcentuales decenales en la superficie forestal una vez controladas la energía y el ingreso;
- los cambios decenales en las emisiones LULUCF per cápita están estrechamente vinculados a la dinámica de la superficie forestal y a la participación de la agricultura en el PIB, de modo que la pérdida de bosques se asocia con mayores aumentos de las emisiones LULUCF per cápita y las reducciones en la participación agrícola con trayectorias LULUCF más favorables;
- agrupaciones regionales sencillas (Cono Sur agrícola, frontera andino‑amazónica y otros países) muestran que una intensidad de CO₂ fósil del PIB baja o decreciente puede coexistir con pérdidas forestales importantes o tendencias mixtas en los bosques.

En conjunto, los resultados muestran que la descarbonización del sector energético y las emisiones por uso de la tierra siguen trayectorias distintas, aunque interrelacionadas, en Sudamérica. Los indicadores habituales de desempeño climático basados únicamente en la intensidad de CO₂ fósil del PIB pueden sobrestimar el progreso de mitigación en economías con alta cobertura boscosa donde las emisiones LULUCF siguen siendo importantes.

## Estructura del repositorio

- `article/data/` – paneles listos para el análisis utilizados en el artículo:
  - `master_forest_energy_analysis_panel.csv` – panel país–año para 2000, 2010, 2020.
  - `south_america_delta_panel_analysis.csv` – panel de cambios decenales para 2000–2010 y 2010–2020.
  - `variables_codebook.csv` – nombres de variables, descripciones, fuentes y unidades.
- `data_cepal/` – datos fuente e intermedios del flujo ETL centrado en CEPALSTAT.
- `article/scripts/` – scripts en Python para construir los paneles de análisis y las figuras del artículo.

Documentación adicional de los pasos ETL y de los métodos se encuentra en `article/methods_full_draft.md` y `article/methods.md`.

