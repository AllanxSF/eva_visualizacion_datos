# StreamView Analytics

Proyecto de visualización y análisis de datos sobre el catálogo de Netflix. El proyecto integra limpieza de datos, análisis exploratorio, métricas de negocio y dos dashboards complementarios para analizar películas y series desde distintas perspectivas.

> Proyecto académico — Evaluación 1, Visualización de Datos, 5.º semestre.

## Contenido

- [Descripción](#descripción)
- [Objetivos](#objetivos)
- [Dashboards](#dashboards)
- [Datos utilizados](#datos-utilizados)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Requisitos](#requisitos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Flujo de datos](#flujo-de-datos)
- [Funcionalidades del dashboard de Streamlit](#funcionalidades-del-dashboard-de-streamlit)
- [Decisiones técnicas](#decisiones-técnicas)
- [Limitaciones conocidas](#limitaciones-conocidas)
- [Equipo](#equipo)
- [Licencia](#licencia)

## Descripción

**StreamView Analytics** transforma un catálogo de películas y series en información útil para explorar:

- La popularidad y la calificación de los títulos.
- La distribución de contenidos por género, país, idioma y año.
- Los directores y actores con mayor presencia o desempeño.
- La evolución y composición del catálogo.
- La relación entre presupuesto, ingresos y retorno aproximado.

El repositorio contiene notebooks de análisis, módulos reutilizables de preparación de datos y dashboards desarrollados con herramientas de visualización de datos.

## Objetivos

1. Preparar y limpiar los datos para que puedan analizarse de forma consistente.
2. Explorar patrones del catálogo mediante análisis descriptivo y visualizaciones.
3. Comparar películas y series según popularidad, calificación y características de producción.
4. Incorporar información financiera para apoyar el análisis de desempeño.
5. Comunicar los resultados mediante dashboards interactivos y fáciles de interpretar.

## Dashboards

El proyecto contempla dos dashboards. Ambos deben considerarse complementarios y no necesariamente utilizan la misma herramienta o presentación.

### Dashboard 1 — [Espacio para documentar el dashboard de tu compañero]

> **Pendiente de completar por el compañero:** agregar aquí el nombre del dashboard, herramienta utilizada, objetivo, instrucciones de ejecución, principales visualizaciones, filtros, enlace o captura y cualquier requisito adicional.

| Campo | Valor |
|---|---|
| Nombre | `Por completar` |
| Herramienta | `Por completar` |
| Responsable | `Por completar` |
**Descripción:** `Por completar`

#### Cómo ejecutar

```text
Agregar aquí los comandos o pasos necesarios para ejecutar el Dashboard 1.
```

#### Principales visualizaciones

- `Por completar`
- `Por completar`
- `Por completar`

### Dashboard 2 — StreamView Analytics en Streamlit

Dashboard analítico desarrollado en Python con Streamlit. Permite filtrar el catálogo y consultar indicadores, rankings, visualizaciones de popularidad, calificaciones, géneros, países y finanzas.

**Archivo principal:** [`app/streamlit_app.py`](app/streamlit_app.py)

**Dependencias:** [`requirements-dashboard.txt`](requirements-dashboard.txt)

#### Ejecución rápida

Desde la raíz del repositorio:

```bash
pip install -r requirements-dashboard.txt
streamlit run app/streamlit_app.py
```

Al iniciar, Streamlit mostrará una dirección local, normalmente `http://localhost:8501`.

## Datos utilizados

Los archivos deben estar dentro de [`data/`](data/):

| Archivo | Descripción |
|---|---|
| `netflix_movies_detailed_up_to_2025.csv` | Catálogo detallado de películas. |
| `netflix_tv_shows_detailed_up_to_2025.csv` | Catálogo detallado de series. |
| `finanzas_filtradas.csv` | Datos financieros validados para títulos con información de presupuesto e ingresos. |

El dashboard de Streamlit requiere que existan al menos los CSV correspondientes a la fuente seleccionada. Si los archivos no están en `data/`, la aplicación mostrará un error y no podrá cargar el catálogo.

### Columnas principales

El proceso de limpieza valida, entre otras, las siguientes columnas:

`show_id`, `type`, `title`, `director`, `cast`, `country`, `date_added`, `release_year`, `rating`, `duration`, `genres`, `language`, `description`, `popularity`, `vote_count` y `vote_average`.

## Estructura del proyecto

```text
eva_visualizacion_datos/
├── app/
│   └── streamlit_app.py          # Aplicación del Dashboard 2
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
├── src/
│   ├── dashboard_datos.py        # Carga, transformación y métricas del dashboard
│   ├── limpieza.py               # Limpieza y validación de datos
│   └── negocio.py                # Lógica de análisis de negocio
├── .streamlit/
│   └── config.toml               # Tema y configuración visual de Streamlit
├── requirements-dashboard.txt    # Dependencias del Dashboard 2
└── README.md
```

## Requisitos

- Python 3.10 o superior recomendado.
- `pip`.
- Los archivos CSV descritos en [Datos utilizados](#datos-utilizados).
- Un navegador web para visualizar Streamlit.

Las dependencias del dashboard son:

- Streamlit
- pandas
- NumPy
- Plotly
- Matplotlib
- Seaborn

## Flujo de datos

```text
CSV originales
    │
    ▼
limpieza_datos()
    │
    ▼
Unión con finanzas_filtradas.csv mediante (show_id, type)
    │
    ▼
Tablas multivalor para géneros, países, directores y actores
    │
    ▼
Filtros del usuario
    │
    ▼
Agregaciones, KPIs y visualizaciones
```

La carga de datos se realiza en [`src/dashboard_datos.py`](src/dashboard_datos.py) y se reutiliza desde la aplicación. Streamlit utiliza `st.cache_data` para evitar cargar y procesar nuevamente los mismos archivos en cada interacción.

## Funcionalidades del dashboard de Streamlit

### Filtros

La barra lateral permite filtrar por:

- Tipo de contenido: película o serie.
- Rango de años de estreno.
- Rango de calificación.
- Género.
- País.
- Idioma.

También incluye parámetros para definir:

- Votos mínimos necesarios para considerar válida una calificación.
- Umbral de votos para el ranking de títulos mejor evaluados.
- Mínimo de títulos por país y por género.
- Cantidad de elementos mostrados en los rankings.

El botón **Restablecer filtros** devuelve la vista a los valores iniciales.

### Visualizaciones y análisis

| Sección | Contenido |
|---|---|
| Popularidad vs. calificación | Dispersión de popularidad y calificación, con codificación por tipo o votos y tamaño asociado a los votos. |
| Géneros | Barras de popularidad y calificación promedio, además de un treemap de géneros. |
| Rankings | Top de títulos mejor evaluados, directores y actores, con umbrales configurables. |
| Países | Mapa por país considerando un mínimo de títulos para evitar resultados poco representativos. |
| Finanzas | KPIs, dispersión financiera, ingresos principales y análisis de retorno aproximado. |
| Preguntas de negocio | Indicadores y visualizaciones orientadas a responder preguntas de negocio. |

El dashboard utiliza una paleta accesible basada en Okabe-Ito y escalas Viridis/Plasma para mejorar la lectura de gráficos y leyendas.

## Decisiones técnicas

- **Unión segura de datos:** se utiliza la clave compuesta `(show_id, type)` porque algunos `show_id` se repiten entre películas y series. Unir solo por `show_id` podría mezclar registros.
- **Identificador único:** cada registro recibe un `uid`, utilizado para relacionar las tablas multivalor.
- **Calificaciones confiables:** los títulos con cero votos pueden tener una calificación igual a cero, que no representa una nota real. Por defecto se excluyen de los promedios mediante el parámetro de votos mínimos.
- **Popularidad:** se presenta en escala logarítmica debido a su fuerte sesgo. También se reportan correlaciones de Spearman y Pearson.
- **Finanzas:** el ROI aproximado se calcula como `(ingresos totales - presupuesto total) / presupuesto total` sobre el conjunto filtrado.
- **Rankings:** se aplican umbrales mínimos de votos, títulos o registros financieros para evitar conclusiones basadas en muestras demasiado pequeñas.
- **Reutilización:** la lógica de carga, limpieza, filtros y agregaciones se mantiene separada de la interfaz de Streamlit.

## Equipo

| Integrante | Responsabilidad |
|---|---|
| `Allan Salinas` | Dashboard 1 PowerBI |
| `Matias Bustos` | Dashboard 2 en Streamlit |