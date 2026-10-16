import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import streamlit as st

from src import dashboard_datos as dd
from src.dashboard_datos import n_es

DATA_DIR = RAIZ / "data"

# Paleta accesible (Okabe-Ito) usada de forma consistente en todo el dashboard
AZUL, NARANJA, ROJO = "#0072B2", "#E69F00", "#D55E00"
COLOR_TIPO = {"Movie": AZUL, "TV Show": NARANJA}
COLOR_ROI = {"Bajo": ROJO, "Medio": NARANJA, "Alto": AZUL}

st.set_page_config(page_title="StreamView · Dashboard analítico", page_icon="🎬", layout="wide")
sns.set_theme(style="whitegrid")


# ───────────────────────── Carga (con caché) ─────────────────────────
@st.cache_data(show_spinner="Cargando catálogo…")
def cargar(fuente):
    df = dd.cargar_datos(DATA_DIR, fuente)
    return df, dd.tablas_multivalor(df)


disp = dd.fuentes_disponibles(DATA_DIR)
if not (disp["completo"] or disp["finanzas"]):
    st.error(f"No se encontraron datos en `{DATA_DIR}`. Revisa que existan los CSV del proyecto.")
    st.stop()

# ───────────────────────── Barra lateral: fuente, parámetros y filtros ─────────────────────────
st.sidebar.title("🎬 Filtros")

opciones_fuente = {}
if disp["completo"]:
    opciones_fuente["Catálogo completo (películas + series)"] = "completo"
if disp["finanzas"]:
    opciones_fuente["Solo películas con finanzas (finanzas_filtradas.csv)"] = "finanzas"
if len(opciones_fuente) > 1:
    fuente = opciones_fuente[st.sidebar.radio("Fuente de datos", list(opciones_fuente), key="f_fuente")]
else:
    fuente = next(iter(opciones_fuente.values()))

df_base, tablas = cargar(fuente)

with st.sidebar.expander("⚙️ Parámetros del análisis", expanded=False):
    min_votos_cal = st.number_input(
        "Votos mínimos para considerar la calificación", 0, 1000, 1, key="p_min_votos_cal",
        help="Los títulos sin votos traen calificación 0, que no es una nota real. "
             "Con 1 se excluyen de los promedios; súbelo para exigir más respaldo.")
    umbral_votos = st.number_input("Umbral de votos para el Top mejor evaluados", 0, 50000, 1000, step=100, key="p_umbral")
    min_pais = st.number_input("Mínimo de títulos por país (mapas)", 1, 500, 10, key="p_min_pais")
    min_genero = st.number_input("Mínimo de títulos por género", 1, 500, 10, key="p_min_gen")
    top_n = st.slider("Tamaño de los rankings (Top N)", 5, 20, 10, key="p_topn")

df = dd.aplicar_calificacion(df_base, min_votos_cal)

anio_min, anio_max = int(df["release_year"].min()), int(df["release_year"].max())

DEFAULTS = {
    "f_tipo": [], "f_anios": (anio_min, anio_max), "f_cal": (0.0, 10.0),
    "f_gen": [], "f_pais": [], "f_idioma": [],
}

def _restablecer():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v


st.sidebar.button("↺ Restablecer filtros", on_click=_restablecer, use_container_width=True)

st.sidebar.multiselect("Tipo de contenido", sorted(df["type"].unique()), key="f_tipo",
                       placeholder="Todos")
st.sidebar.slider("Rango de años de estreno", anio_min, anio_max, value=DEFAULTS["f_anios"], key="f_anios")
st.sidebar.slider("Rango de calificación", 0.0, 10.0, value=DEFAULTS["f_cal"], step=0.1, key="f_cal",
                  help="Si lo modificas, se excluyen los títulos sin calificación válida.")
st.sidebar.multiselect("Género", sorted(tablas["genero"]["genero"].unique()), key="f_gen", placeholder="Todos")
st.sidebar.multiselect("País", sorted(tablas["pais"]["pais"].unique()), key="f_pais", placeholder="Todos")
st.sidebar.multiselect("Idioma", sorted(df["idioma"].unique()), key="f_idioma", placeholder="Todos")

ss = st.session_state
df_f = dd.filtrar(df, tablas, tipo=ss.f_tipo, anios=ss.f_anios, calificacion=ss.f_cal, generos=ss.f_gen,
                  paises=ss.f_pais, idiomas=ss.f_idioma)

# ───────────────────────── Encabezado y KPIs ─────────────────────────
st.title("StreamView Analytics · Dashboard analítico")

st.markdown("""
<style>
/* Tarjetas de los KPI */
div[data-testid="stMetric"] {
    background-color: #eaeef3;
    border: 1px solid #d9e0e8;
    padding: 18px 20px;
    border-radius: 12px;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.04);
}
/* Espacio entre la etiqueta y el valor */
div[data-testid="stMetricLabel"] {
    font-size: 14px;
}
/* Valor principal del KPI */
div[data-testid="stMetricValue"] {
    font-size: 28px;
}
</style>
""", unsafe_allow_html=True)

if df_f.empty:
    st.warning("Los filtros actuales no dejan ningún título. Usa **Restablecer filtros** o amplía los rangos.")
    st.stop()

def _con_roi(base, tabla, minimo=0.8):
    """Suma el ROI mediano al puntaje solo si la mayoría de las filas lo tiene (en el catálogo completo
    solo ~3.000 películas traen finanzas; usarlo descartaría casi todo)."""
    ok = len(tabla) > 0 and tabla["roi_mediano"].notna().mean() >= minimo
    return base + (["roi_mediano"] if ok else [])


gen_df = dd.unir_metricas(tablas["genero"], df_f)
pais_df = dd.unir_metricas(tablas["pais"], df_f)
df_fin = df_f[df_f["fin_valido"]]

k = st.columns(4)
k[0].metric("Total de contenidos", n_es(len(df_f)))
k[1].metric("Películas", n_es((df_f["type"] == "Movie").sum()))
k[2].metric("Series", n_es((df_f["type"] == "TV Show").sum()))
k[3].metric("Países representados", n_es(pais_df["pais"].nunique()))
k = st.columns(4)
k[0].metric("Idiomas", n_es(df_f["language"].nunique()))
k[1].metric("Géneros", n_es(gen_df["genero"].nunique()))
k[2].metric("Popularidad promedio", n_es(df_f["popularity"].mean(), 1))
k[3].metric("Calificación promedio", n_es(df_f["calificacion"].mean(), 2),
            help=f"Promedio sobre títulos con ≥ {min_votos_cal} votos "
                 f"({n_es(df_f['calificacion'].notna().sum())} de {n_es(len(df_f))}).")

(t_scatter, t_gen, t_rank, t_pais, t_fin, t_preg) = st.tabs([
    "📈 Popularidad vs. calificación", "🎭 Géneros", "🏆 Rankings", "🗺️ Países",
    "💰 Finanzas", "❓ Preguntas de negocio"])

# ───────────────────────── 1. Popularidad vs. calificación (req. a) ─────────────────────────
with t_scatter:
    d = df_f.dropna(subset=["calificacion"]).copy()
    if len(d) < 3:
        st.info("No hay suficientes títulos con calificación válida para este análisis.")
    else:
        r_p = d["popularity"].corr(d["calificacion"])
        r_s = d["popularity"].corr(d["calificacion"], method="spearman")
        c1, c2, c3 = st.columns(3)
        c1.metric("Correlación de Spearman", f"{r_s:.2f}", dd.fuerza(r_s), delta_color="off")
        c2.metric("Correlación de Pearson", f"{r_p:.2f}", dd.fuerza(r_p), delta_color="off")
        c3.metric("Títulos graficados", n_es(len(d)))

        colorear = st.radio("Colorear por", ["Tipo de contenido", "Cantidad de votos"], horizontal=True)
        d["votos_log10"] = np.log10(d["vote_count"].clip(lower=1))
        d["tam"] = 4 + 12 * np.log1p(d["vote_count"]) / np.log1p(max(d["vote_count"].max(), 1))
        comunes = dict(x="popularity", y="calificacion", size="tam", size_max=14, opacity=0.55, log_x=True,
                       hover_name="etiqueta", render_mode="webgl",
                       hover_data={"popularity": ":.1f", "calificacion": ":.2f", "vote_count": ":,",
                                   "tam": False, "votos_log10": False},
                       labels={"popularity": "Popularidad (escala log)", "calificacion": "Calificación",
                               "vote_count": "Votos", "type": "Tipo", "votos_log10": "log10(votos)"})
        if colorear == "Tipo de contenido":
            fig = px.scatter(d, color="type", color_discrete_map=COLOR_TIPO, **comunes)
        else:
            fig = px.scatter(d, color="votos_log10", color_continuous_scale="Viridis", **comunes)
        fig.update_layout(height=560, title="Popularidad vs. calificación (tamaño = votos)")
        st.plotly_chart(fig, use_container_width=True)

# ───────────────────────── 2. Géneros (req. b, c) ─────────────────────────
with t_gen:
    gen = dd.resumen_por(gen_df, "genero")
    gen_ok = gen[gen["n"] >= min_genero].sort_values("n", ascending=False)
    if gen_ok.empty:
        st.info(f"Ningún género alcanza el mínimo de {min_genero} títulos con los filtros actuales.")
    else:
        mostrar = gen_ok.head(15)
        orden = mostrar["genero"].tolist()
        c1, c2 = st.columns(2)
        with c1:
            g_pop = df_f["popularity"].mean()
            fig = px.bar(mostrar, x="popularidad_prom", y="genero", orientation="h", text_auto=".1f",
                         color_discrete_sequence=[AZUL], category_orders={"genero": orden},
                         labels={"popularidad_prom": "Popularidad promedio", "genero": ""},
                         title="Popularidad promedio por género")
            fig.add_vline(x=g_pop, line_dash="dash", line_color="#333", annotation_text=f"General: {g_pop:.1f}")
            fig.update_yaxes(autorange="reversed"); fig.update_layout(height=520)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            g_cal = df_f["calificacion"].mean()
            fig = px.scatter(mostrar, x="calificacion_prom", y="genero", size="n", size_max=22,
                             color_discrete_sequence=[NARANJA], category_orders={"genero": orden},
                             hover_data={"n": ":,", "calificacion_prom": ":.2f"},
                             labels={"calificacion_prom": "Calificación promedio", "genero": "", "n": "Títulos"},
                             title="Calificación promedio por género (tamaño = títulos)")
            fig.add_vline(x=g_cal, line_dash="dash", line_color="#333", annotation_text=f"General: {g_cal:.2f}")
            fig.update_yaxes(autorange="reversed"); fig.update_layout(height=520)
            st.plotly_chart(fig, use_container_width=True)

        fig = px.treemap(gen_ok, path=["genero"], values="n", color="calificacion_prom",
                         color_continuous_scale="Viridis",
                         hover_data={"n": ":,", "calificacion_prom": ":.2f", "popularidad_mediana": ":.1f"},
                         labels={"n": "Títulos", "calificacion_prom": "Calificación prom.",
                                 "popularidad_mediana": "Popularidad mediana"},
                         title="Treemap de géneros por volumen (color = calificación promedio)")
        fig.update_traces(textinfo="label+value"); fig.update_layout(height=480)
        st.plotly_chart(fig, use_container_width=True)

# ───────────────────────── 3. Rankings (req. d, e) ─────────────────────────
with t_rank:
    st.subheader(f"Top {top_n} mejor evaluados (mínimo {n_es(umbral_votos)} votos)")
    elegibles = df_f[df_f["vote_count"] >= umbral_votos]
    if elegibles.empty:
        st.info("Ningún título alcanza el umbral de votos con los filtros actuales. Bájalo en *Parámetros del análisis*.")
    else:
        top_ev = elegibles.sort_values(["vote_average", "vote_count"], ascending=False).head(top_n)
        fig = px.bar(top_ev, x="vote_average", y="etiqueta", orientation="h", color="type",
                     color_discrete_map=COLOR_TIPO, text="vote_average",
                     hover_data={"vote_count": ":,", "popularity": ":.1f"},
                     labels={"vote_average": "Calificación", "etiqueta": "", "type": "Tipo", "vote_count": "Votos"})
        fig.update_traces(texttemplate="%{text:.2f}")
        fig.update_yaxes(autorange="reversed"); fig.update_xaxes(range=[0, 10]); fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader(f"Top {top_n} directores y actores por cantidad de contenidos")
    c1, c2 = st.columns(2)
    for col_ui, tabla, campo, color, titulo in [
        (c1, tablas["director"], "director_n", AZUL, "Directores"),
        (c2, tablas["actor"], "actor", NARANJA, "Actores"),
    ]:
        cnt = (tabla[tabla["uid"].isin(df_f["uid"])].groupby(campo)["uid"].nunique()
               .sort_values(ascending=False).head(top_n).reset_index(name="titulos"))
        with col_ui:
            if cnt.empty:
                st.info(f"Sin datos de {titulo.lower()} para los filtros actuales.")
            else:
                fig = px.bar(cnt, x="titulos", y=campo, orientation="h", text="titulos",
                             color_discrete_sequence=[color],
                             labels={"titulos": "Títulos", campo: ""}, title=titulo)
                fig.update_yaxes(autorange="reversed"); fig.update_layout(height=430)
                st.plotly_chart(fig, use_container_width=True)

# ───────────────────────── 4. Países (req. f) ─────────────────────────
with t_pais:
    pais = dd.resumen_por(pais_df, "pais")
    pais["iso3"] = pais["pais"].map(dd.ISO3)
    pais_ok = pais[(pais["n"] >= min_pais) & pais["iso3"].notna()].copy()
    if pais_ok.empty:
        st.info("Ningún país alcanza el mínimo de títulos con los filtros actuales.")
    else:
        metrica = st.radio("Métrica del mapa", ["Calificación promedio", "Popularidad mediana"], horizontal=True)
        col_m, escala = (("calificacion_prom", "Viridis") if metrica == "Calificación promedio"
                         else ("popularidad_mediana", "Plasma"))
        fig = px.choropleth(pais_ok, locations="iso3", color=col_m, hover_name="pais", color_continuous_scale=escala,
                            hover_data={"iso3": False, "n": ":,", "calificacion_prom": ":.2f",
                                        "popularidad_mediana": ":.1f"},
                            labels={"n": "Títulos", "calificacion_prom": "Calificación prom.",
                                    "popularidad_mediana": "Popularidad mediana"},
                            title=f"{metrica} por país")
        fig.update_geos(showframe=False, showcoastlines=False, projection_type="natural earth")
        fig.update_layout(height=520, margin=dict(t=60, l=0, r=0, b=0))
        st.plotly_chart(fig, use_container_width=True)

        top_p = pais.sort_values("n", ascending=False).head(top_n)
        fig = px.bar(top_p, x="n", y="pais", orientation="h", text="n", color_discrete_sequence=[AZUL],
                     labels={"n": "Títulos", "pais": ""}, title=f"Top {top_n} países por cantidad de títulos")
        fig.update_yaxes(autorange="reversed"); fig.update_layout(height=430)
        st.plotly_chart(fig, use_container_width=True)

# ───────────────────────── 5. Finanzas (req. g) ─────────────────────────
with t_fin:
    st.info(
        f"**Nota:** el análisis financiero incluye **solo películas con presupuesto e ingresos informados** "
        f"(valores > 0 y escala validada). Con los filtros actuales son **{n_es(len(df_fin))} de {n_es(len(df_f))} títulos** "
        f"({len(df_fin) / max(len(df_f), 1):.1%}). Las series y las películas sin datos financieros no se incluyen.")
    if df_fin.empty:
        st.warning("No hay películas con datos financieros válidos para los filtros actuales.")
    else:
        kf = dd.kpis_financieros(df_fin)
        c = st.columns(5)
        c[0].metric("Presupuesto promedio", f"{n_es(kf['presupuesto_prom'], 1)} M USD")
        c[1].metric("Total presupuesto", f"{n_es(kf['presupuesto_total'])} M USD")
        c[2].metric("Total ingresos", f"{n_es(kf['ingresos_total'])} M USD")
        c[3].metric("ROI aproximado", f"{n_es(kf['roi_aprox'], 1)} %",
                    help="(Total ingresos − Total presupuesto) / Total presupuesto, sobre el conjunto filtrado.")
        c[4].metric("ROI mediano por película", f"{n_es(kf['roi_mediano'], 1)} %")

        corr_fin = df_fin["budget_musd"].corr(df_fin["revenue_musd"])
        fig = px.scatter(df_fin, x="budget_musd", y="revenue_musd", color="roi_band", log_x=True, log_y=True,
                         color_discrete_map=COLOR_ROI, category_orders={"roi_band": ["Bajo", "Medio", "Alto"]},
                         hover_name="etiqueta", opacity=0.7,
                         hover_data={"budget_musd": ":.1f", "revenue_musd": ":.1f", "roi_pct": ":.0f", "roi_band": False},
                         labels={"budget_musd": "Presupuesto (M USD)", "revenue_musd": "Ingresos (M USD)",
                                 "roi_band": "Banda de ROI", "roi_pct": "ROI %"},
                         title=f"Presupuesto vs. ingresos · correlación = {corr_fin:.2f}")
        lo = float(min(df_fin["budget_musd"].min(), df_fin["revenue_musd"].min()))
        hi = float(max(df_fin["budget_musd"].max(), df_fin["revenue_musd"].max()))
        fig.add_trace(go.Scatter(x=[lo, hi], y=[lo, hi], mode="lines", name="Punto de equilibrio",
                                 line=dict(color="#333", dash="dash")))
        fig.update_layout(height=560)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader(f"Top {top_n} películas por ingresos")
        top_ing = df_fin.nlargest(top_n, "revenue_musd")
        fig = px.bar(top_ing, x="revenue_musd", y="etiqueta", orientation="h", text="revenue_musd",
                     color_discrete_sequence=[AZUL],
                     hover_data={"budget_musd": ":.1f", "profit_musd": ":.1f", "roi_pct": ":.0f"},
                     labels={"revenue_musd": "Ingresos (M USD)", "etiqueta": "", "budget_musd": "Presupuesto (M USD)",
                             "profit_musd": "Beneficio (M USD)", "roi_pct": "ROI %"})
        fig.update_traces(texttemplate="%{text:,.0f}")
        fig.update_yaxes(autorange="reversed"); fig.update_layout(height=460)
        st.plotly_chart(fig, use_container_width=True)

# ───────────────────────── 6. Preguntas de negocio (req. i) ─────────────────────────
with t_preg:
    gen_all = dd.resumen_por(gen_df, "genero")
    gen_cand = gen_all[gen_all["n"] >= min_genero]
    cols_g = _con_roi(["n", "calificacion_prom", "popularidad_mediana"], gen_cand)
    gen_sc = dd.puntaje(gen_cand, cols_g)
    st.subheader("¿Qué géneros priorizar?")
    if gen_sc.empty:
        st.info("No hay géneros con muestra suficiente.")
    else:
        top3 = ", ".join(gen_sc.head(3)["genero"])
        st.markdown(f"Los mejor puntuados son **{top3}**.")
        heat = gen_sc.set_index("genero")[cols_g]
        rangos = heat.rank(pct=True)
        fmt = {"n": "{:,.0f}", "calificacion_prom": "{:.2f}", "popularidad_mediana": "{:.1f}", "roi_mediano": "{:.0f} %"}
        anot = heat.copy().astype(object)
        for c_ in cols_g:
            anot[c_] = heat[c_].map(lambda v, f=fmt[c_]: "—" if pd.isna(v) else f.format(v))
        etiquetas = {"n": "Volumen", "calificacion_prom": "Calificación prom.",
                     "popularidad_mediana": "Popularidad mediana", "roi_mediano": "ROI mediano"}
        fig, ax = plt.subplots(figsize=(8, max(4, 0.4 * len(heat))))
        sns.heatmap(rangos, annot=anot, fmt="", cmap="viridis", cbar_kws={"label": "Percentil (1 = mejor)"},
                    xticklabels=[etiquetas[c_] for c_ in cols_g], ax=ax)
        ax.set_ylabel(""); plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
        st.pyplot(fig); plt.close(fig)

    st.subheader("¿Qué países son oportunidad?")
    cols_p = _con_roi(["calificacion_prom", "popularidad_mediana"], pais_ok)
    pais_sc = dd.puntaje(pais_ok, cols_p) if len(pais_ok) else pais_ok
    if len(pais_sc):
        pais_sc["cuota_titulos_%"] = pais_sc["n"] / len(df_f) * 100
        st.markdown(f"Mejor desempeño combinado entre países con ≥ {min_pais} títulos: "
                    f"**{', '.join(pais_sc.head(3)['pais'])}**.")
        st.dataframe(pais_sc[["pais", "n", "cuota_titulos_%"] + cols_p + ["puntaje"]].head(10).round(2),
                     use_container_width=True, hide_index=True)
    else:
        st.info("No hay países con muestra suficiente.")

    st.subheader("¿Qué películas fueron exitosas con presupuestos reducidos?")
    if df_fin.empty:
        st.info("Sin películas con datos financieros para los filtros actuales.")
    else:
        ex = (df_fin[(df_fin["budget_musd"] <= 20) & (df_fin["roi_pct"] >= 100)]
              .sort_values("profit_musd", ascending=False))
        if ex.empty:
            st.write("Ninguna cumple los criterios actuales.")
        else:
            st.markdown(f"**{n_es(len(ex))}** películas cumplen presupuesto ≤ {20} M USD y ROI ≥ {100} %. "
                        f"Mayores beneficios: **{', '.join(ex.head(3)['etiqueta'])}**. ")

    st.subheader("¿Existe relación entre popularidad y calificación?")
    dv = df_f.dropna(subset=["calificacion"])
    if len(dv) > 3:
        rs = dv["popularity"].corr(dv["calificacion"], method="spearman")
        st.markdown(f"Relación **{dd.fuerza(rs)}** (Spearman = {rs:.2f}).")