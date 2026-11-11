# StreamView Analytics

Proyecto académico de visualización y análisis de datos sobre el catálogo de
Netflix. Integra preparación de datos, análisis exploratorio, métricas de
negocio y dos entregables visuales complementarios: un informe en Power BI y
un dashboard interactivo en Streamlit.

> Evaluación 1 — Visualización de Datos, 5.º semestre.

## Contenido

- [Descripción](#descripción)
- [Entregables](#entregables)
- [Datos](#datos)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Dashboard en Streamlit](#dashboard-en-streamlit)
- [Análisis y documentación](#análisis-y-documentación)
- [Flujo de datos](#flujo-de-datos)
- [Decisiones técnicas](#decisiones-técnicas)
- [Limitaciones](#limitaciones)
- [Equipo](#equipo)

## Descripción

StreamView Analytics permite explorar películas y series según:

- Popularidad, calificación y cantidad de votos.
- Géneros, países, idiomas y años de estreno.
- Directores y actores con mayor presencia.
- Evolución y composición del catálogo.
- Presupuesto, ingresos, beneficio y ROI aproximado de películas con datos
  financieros válidos.

La lógica de limpieza y transformación está separada de las interfaces para
facilitar la reutilización en los notebooks y en el dashboard.

## Entregables

### Informe en Power BI

El informe está disponible en
[`powerbi/StreamView.pbix`](powerbi/StreamView.pbix). Para abrirlo se necesita
Power BI Desktop. El archivo contiene la visualización desarrollada para el
proyecto y puede requerir actualizar las rutas de origen de datos según el
equipo donde se abra.

### Dashboard analítico en Streamlit

La aplicación se encuentra en
[`app/streamlit_app.py`](app/streamlit_app.py). Permite seleccionar el catálogo
completo o únicamente las películas con información financiera y aplicar
filtros interactivos.

Incluye las siguientes secciones:

| Sección | Contenido |
|---|---|
| Popularidad vs. calificación | Dispersión con escala logarítmica, correlaciones de Spearman y Pearson. |
| Géneros | Popularidad y calificación promedio, volumen y treemap. |
| Rankings | Títulos mejor evaluados, directores y actores con mayor presencia. |
| Países | Distribución geográfica y comparación por país. |
| Finanzas | Presupuesto, ingresos, beneficio, ROI y títulos destacados. |
| Preguntas de negocio | Priorización de géneros, oportunidades por país y películas rentables con bajo presupuesto. |

## Datos

Los archivos de entrada se encuentran en [`data/`](data/):

| Archivo | Uso |
|---|---|
| `netflix_movies_detailed_up_to_2025.csv` | Catálogo de películas. |
| `netflix_tv_shows_detailed_up_to_2025.csv` | Catálogo de series. |
| `finanzas_filtradas.csv` | Películas con presupuesto, ingresos y métricas financieras validadas. |

El catálogo completo se construye uniendo películas y series con los datos
financieros mediante la clave compuesta `(show_id, type)`. La aplicación
también puede ejecutarse solo con `finanzas_filtradas.csv`, siempre que ese
archivo esté disponible.

Las columnas principales del catálogo incluyen `show_id`, `type`, `title`,
`director`, `cast`, `country`, `date_added`, `release_year`, `rating`,
`duration`, `genres`, `language`, `description`, `popularity`, `vote_count` y
`vote_average`.

## Estructura del proyecto

```text
eva_visualizacion_datos/
├── app/
│   └── streamlit_app.py              # Dashboard interactivo
├── data/
│   ├── netflix_movies_detailed_up_to_2025.csv
│   ├── netflix_tv_shows_detailed_up_to_2025.csv
│   └── finanzas_filtradas.csv
├── docs/
│   ├── Informe Ejecutivo.pdf
│   └── StreamView Analytics.pdf
├── notebooks/
│   ├── analisis.ipynb
│   ├── analisis2.ipynb
│   └── analisis_popularidad_evolucion_finanzas.ipynb
├── powerbi/
│   └── StreamView.pbix                 # Informe de Power BI
├── src/
│   ├── dashboard_datos.py              # Carga, filtros y agregaciones
│   ├── limpieza.py                     # Limpieza y validación
│   └── negocio.py                      # Controles financieros
├── .streamlit/
│   └── config.toml                     # Configuración visual
├── requirements-dashboard.txt
└── README.md
```

## Requisitos

- Python 3.10 o superior.
- `pip`.
- Un navegador web para utilizar Streamlit.
- Power BI Desktop, solo para abrir el informe `.pbix`.

Las dependencias de la aplicación están declaradas en
[`requirements-dashboard.txt`](requirements-dashboard.txt):

- Streamlit
- pandas
- NumPy
- SciPy
- Plotly
- Matplotlib
- Seaborn

## Dashboard en Streamlit

### Instalación

Desde la raíz del repositorio:

```bash
python -m venv .venv
```

Activar el entorno virtual:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS o Linux
source .venv/bin/activate
```

Instalar las dependencias:

```bash
python -m pip install -r requirements-dashboard.txt
```

### Ejecución

```bash
streamlit run app/streamlit_app.py
```

Streamlit mostrará la dirección local, normalmente
`http://localhost:8501`.

La aplicación verifica automáticamente los archivos disponibles en `data/`.
Si no encuentra los CSV requeridos, muestra un error y detiene la carga.

### Filtros y parámetros

En la barra lateral se puede filtrar por:

- Tipo de contenido: película o serie.
- Rango de años de estreno.
- Rango de calificación.
- Género.
- País.
- Idioma.

También se pueden ajustar los votos mínimos para considerar válida una
calificación, el umbral del ranking de títulos mejor evaluados, el mínimo de
títulos por país y género, y el tamaño de los rankings. El botón
**Restablecer filtros** devuelve la vista a sus valores iniciales.

## Análisis y documentación

Los notebooks de [`notebooks/`](notebooks/) contienen análisis exploratorios y
visualizaciones sobre popularidad, evolución del catálogo y finanzas.

Los documentos de [`docs/`](docs/) incluyen el informe ejecutivo y el
documento de presentación de StreamView Analytics.

## Flujo de datos

```text
CSV de películas y series
            │
            ▼
      limpieza_datos()
            │
            ▼
Unión opcional con finanzas_filtradas.csv
            │
            ▼
Tablas multivalor de géneros, países,
directores y actores
            │
            ▼
Filtros y parámetros del usuario
            │
            ▼
Agregaciones, indicadores y gráficos
```

La capa de datos está implementada en
[`src/dashboard_datos.py`](src/dashboard_datos.py), mientras que
[`src/limpieza.py`](src/limpieza.py) normaliza columnas, convierte tipos,
trata valores nulos y elimina duplicados exactos. La aplicación usa
`st.cache_data` para evitar reprocesar los mismos archivos en cada interacción.

## Decisiones técnicas

- Se utiliza `(show_id, type)` para evitar mezclar películas y series que
  compartan identificador.
- Cada fila recibe un `uid` interno para relacionar tablas multivalor.
- Las calificaciones sin votos suficientes se excluyen de los promedios.
- La popularidad se visualiza en escala logarítmica por su distribución
  sesgada.
- El ROI agregado se calcula como
  `(ingresos totales - presupuesto total) / presupuesto total`.
- Los rankings y agregaciones aplican umbrales configurables para reducir el
  efecto de muestras pequeñas.
- La paleta visual usa colores accesibles Okabe-Ito y escalas Viridis.

## Limitaciones

- La calidad y cobertura de los resultados dependen de los CSV incluidos en
  `data/`.
- No todos los títulos tienen votos, calificación o información financiera.
- Los datos financieros están disponibles principalmente para películas.
- El archivo `.pbix` puede requerir actualizar las rutas de datos al abrirse
  en otro equipo.
- No se incluye una licencia de software explícita en este repositorio.

## Equipo

| Integrantes ||
|---|---|
| Allan Salinas 
| Matias Bustos 
