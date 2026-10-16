"""Capa de datos del dashboard analítico: carga, filtros y agregaciones (sin dependencia de Streamlit)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from src.limpieza import limpieza_datos

# ───────────────────────── Archivos esperados en /data ─────────────────────────
F_PELICULAS = "netflix_movies_detailed_up_to_2025.csv"
F_SERIES = "netflix_tv_shows_detailed_up_to_2025.csv"
F_FINANZAS = "finanzas_filtradas.csv"

# Columnas financieras validadas que se cruzan con el catálogo (la app no usa las crudas ni los *_status)
COLS_FIN_VALORES = ["budget_musd", "revenue_musd", "profit_musd", "roi_pct", "roi_band"]
COLS_FINANZAS = ["show_id", "type"] + COLS_FIN_VALORES

# Métricas que se traen a las tablas multivalor (género, país) para agregar por atributo
METRICAS = ["uid", "popularity", "calificacion", "roi_pct"]

# ───────────────────────── Diccionarios de apoyo ─────────────────────────
NOMBRE_IDIOMA = {
    "af": "Afrikáans", "am": "Amárico", "ar": "Árabe", "as": "Asamés", "az": "Azerí", "bg": "Búlgaro",
    "bn": "Bengalí", "bs": "Bosnio", "ca": "Catalán", "cn": "Cantonés", "cs": "Checo", "cy": "Galés",
    "da": "Danés", "de": "Alemán", "dz": "Dzongkha", "el": "Griego", "en": "Inglés", "es": "Español",
    "et": "Estonio", "eu": "Euskera", "fa": "Persa", "fi": "Finés", "fr": "Francés", "ga": "Irlandés",
    "gl": "Gallego", "he": "Hebreo", "hi": "Hindi", "hr": "Croata", "ht": "Criollo haitiano",
    "hu": "Húngaro", "hy": "Armenio", "id": "Indonesio", "is": "Islandés", "it": "Italiano",
    "ja": "Japonés", "ka": "Georgiano", "kk": "Kazajo", "kl": "Groenlandés", "km": "Jemer",
    "kn": "Canarés", "ko": "Coreano", "ku": "Kurdo", "ky": "Kirguís", "la": "Latín", "lb": "Luxemburgués",
    "lt": "Lituano", "lv": "Letón", "mi": "Maorí", "mk": "Macedonio", "ml": "Malayalam", "mn": "Mongol",
    "mr": "Maratí", "ms": "Malayo", "mt": "Maltés", "nb": "Noruego (bokmål)", "ne": "Nepalí",
    "nl": "Neerlandés", "no": "Noruego", "or": "Odia", "pa": "Panyabí", "pl": "Polaco", "ps": "Pastún",
    "pt": "Portugués", "ro": "Rumano", "ru": "Ruso", "si": "Cingalés", "sk": "Eslovaco", "sl": "Esloveno",
    "sr": "Serbio", "sv": "Sueco", "ta": "Tamil", "te": "Telugu", "th": "Tailandés", "tl": "Tagalo",
    "tr": "Turco", "uk": "Ucraniano", "ur": "Urdu", "vi": "Vietnamita", "xx": "Sin idioma",
    "yo": "Yoruba", "za": "Zhuang", "zh": "Chino (mandarín)", "zu": "Zulú",
}

ISO3 = {
    "Afghanistan": "AFG", "Albania": "ALB", "Algeria": "DZA", "Angola": "AGO", "Argentina": "ARG",
    "Armenia": "ARM", "Aruba": "ABW", "Australia": "AUS", "Austria": "AUT", "Azerbaijan": "AZE",
    "Bahamas": "BHS", "Bangladesh": "BGD", "Belarus": "BLR", "Belgium": "BEL", "Bhutan": "BTN",
    "Bolivia": "BOL", "Bosnia and Herzegovina": "BIH", "Botswana": "BWA", "Brazil": "BRA",
    "Brunei Darussalam": "BRN", "Bulgaria": "BGR", "Cambodia": "KHM", "Cameroon": "CMR", "Canada": "CAN",
    "Cayman Islands": "CYM", "Central African Republic": "CAF", "Chile": "CHL", "China": "CHN",
    "Colombia": "COL", "Congo": "COG", "Cote D'Ivoire": "CIV", "Croatia": "HRV", "Cuba": "CUB",
    "Cyprus": "CYP", "Czech Republic": "CZE", "Denmark": "DNK", "Dominican Republic": "DOM",
    "Ecuador": "ECU", "Egypt": "EGY", "Estonia": "EST", "Ethiopia": "ETH", "Faeroe Islands": "FRO",
    "Fiji": "FJI", "Finland": "FIN", "France": "FRA", "French Polynesia": "PYF", "Georgia": "GEO",
    "Germany": "DEU", "Ghana": "GHA", "Greece": "GRC", "Greenland": "GRL", "Guadaloupe": "GLP",
    "Guatemala": "GTM", "Hong Kong": "HKG", "Hungary": "HUN", "Iceland": "ISL", "India": "IND",
    "Indonesia": "IDN", "Iran": "IRN", "Iraq": "IRQ", "Ireland": "IRL", "Israel": "ISR", "Italy": "ITA",
    "Japan": "JPN", "Jordan": "JOR", "Kazakhstan": "KAZ", "Kenya": "KEN", "Kuwait": "KWT",
    "Kyrgyz Republic": "KGZ", "Lao People's Democratic Republic": "LAO", "Latvia": "LVA",
    "Lebanon": "LBN", "Liechtenstein": "LIE", "Lithuania": "LTU", "Luxembourg": "LUX", "Macao": "MAC",
    "Macedonia": "MKD", "Malawi": "MWI", "Malaysia": "MYS", "Malta": "MLT", "Mauritania": "MRT",
    "Mauritius": "MUS", "Mexico": "MEX", "Monaco": "MCO", "Mongolia": "MNG", "Montenegro": "MNE",
    "Morocco": "MAR", "Myanmar": "MMR", "Namibia": "NAM", "Nepal": "NPL", "Netherlands": "NLD",
    "New Caledonia": "NCL", "New Zealand": "NZL", "Nicaragua": "NIC", "Nigeria": "NGA", "Norway": "NOR",
    "Pakistan": "PAK", "Palau": "PLW", "Palestinian Territory": "PSE", "Panama": "PAN",
    "Paraguay": "PRY", "Peru": "PER", "Philippines": "PHL", "Poland": "POL", "Portugal": "PRT",
    "Puerto Rico": "PRI", "Qatar": "QAT", "Romania": "ROU", "Russia": "RUS", "Rwanda": "RWA",
    "Saudi Arabia": "SAU", "Senegal": "SEN", "Serbia": "SRB", "Singapore": "SGP", "Slovakia": "SVK",
    "Slovenia": "SVN", "Solomon Islands": "SLB", "South Africa": "ZAF", "South Korea": "KOR",
    "Spain": "ESP", "Sri Lanka": "LKA", "St. Kitts and Nevis": "KNA", "St. Lucia": "LCA",
    "St. Pierre and Miquelon": "SPM", "Sweden": "SWE", "Switzerland": "CHE", "Syrian Arab Republic": "SYR",
    "Taiwan": "TWN", "Tanzania": "TZA", "Thailand": "THA", "Tunisia": "TUN", "Turkey": "TUR",
    "US Virgin Islands": "VIR", "Uganda": "UGA", "Ukraine": "UKR", "United Arab Emirates": "ARE",
    "United Kingdom": "GBR", "United States Minor Outlying Islands": "UMI",
    "United States of America": "USA", "Uruguay": "URY", "Uzbekistan": "UZB", "Vanuatu": "VUT",
    "Venezuela": "VEN", "Vietnam": "VNM", "Zambia": "ZMB",
}

SIN_DATO = {"Desconocido", "Unknown", ""}


# ───────────────────────── Utilidades ─────────────────────────
def n_es(x: float, dec: int = 0) -> str:
    """Formato numérico en español: 1.234,5"""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "—"
    s = f"{x:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fuerza(r: float) -> str:
    """Interpretación verbal de un coeficiente de correlación."""
    r = abs(r)
    return "muy débil" if r < 0.1 else "débil" if r < 0.3 else "moderada" if r < 0.5 else "fuerte"


# ───────────────────────── Carga ─────────────────────────
def fuentes_disponibles(data_dir: Path) -> dict[str, bool]:
    data_dir = Path(data_dir)
    return {
        "completo": (data_dir / F_PELICULAS).exists() and (data_dir / F_SERIES).exists(),
        "finanzas": (data_dir / F_FINANZAS).exists(),
    }


def _preparar_comunes(df: pd.DataFrame) -> pd.DataFrame:
    for c in ["director", "cast", "country", "genres"]:
        df[c] = df[c].astype("object").where(df[c].notna(), "Desconocido")
    df["language"] = df["language"].astype("object").where(df["language"].notna(), "xx")
    df["idioma"] = df["language"].map(NOMBRE_IDIOMA).fillna(df["language"])
    df["etiqueta"] = df["title"].astype(str) + " (" + df["release_year"].astype("Int64").astype(str) + ")"
    df = df.reset_index(drop=True)
    df["uid"] = df.index            # identificador único de fila (show_id se repite entre películas y series)
    return df


def cargar_datos(data_dir: Path, fuente: str = "completo") -> pd.DataFrame:
    """
    fuente = "completo"  → películas + series (CSV originales) con los datos financieros
                           validados de finanzas_filtradas.csv unidos por (show_id, type).
    fuente = "finanzas"  → solo finanzas_filtradas.csv (películas con presupuesto e ingresos válidos).
    """
    data_dir = Path(data_dir)
    disp = fuentes_disponibles(data_dir)

    if fuente == "completo":
        if not disp["completo"]:
            raise FileNotFoundError(f"Faltan {F_PELICULAS} y/o {F_SERIES} en {data_dir}")
        pel = limpieza_datos(pd.read_csv(data_dir / F_PELICULAS, low_memory=False))
        ser = limpieza_datos(pd.read_csv(data_dir / F_SERIES, low_memory=False))
        # Se descartan budget/revenue crudos: la versión validada viene de finanzas_filtradas.csv
        df = pd.concat([pel, ser], ignore_index=True).drop(columns=["budget", "revenue"], errors="ignore")

        if disp["finanzas"]:
            fin = pd.read_csv(data_dir / F_FINANZAS, low_memory=False)[COLS_FINANZAS]
            df = df.merge(fin, on=["show_id", "type"], how="left")
        else:
            df = df.assign(**{c: np.nan for c in COLS_FIN_VALORES})
        df["fin_valido"] = df["budget_musd"].notna()
    elif fuente == "finanzas":
        if not disp["finanzas"]:
            raise FileNotFoundError(f"Falta {F_FINANZAS} en {data_dir}")
        df = pd.read_csv(data_dir / F_FINANZAS, low_memory=False)
        df["fin_valido"] = (df["budget"] > 0) & (df["revenue"] > 0)
        for c in ["budget_status", "revenue_status"]:
            if c in df.columns:
                df["fin_valido"] &= df[c].eq("Escala consistente")
    else:
        raise ValueError("fuente debe ser 'completo' o 'finanzas'")

    for c in ["release_year", "popularity", "vote_count", "vote_average"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return _preparar_comunes(df)


def aplicar_calificacion(df: pd.DataFrame, min_votos: int) -> pd.DataFrame:
    """
    `calificacion` = vote_average solo si el título tiene al menos `min_votos` votos.
    Los títulos sin votos traen calificación 0, que no es una nota real y sesgaría los promedios.
    """
    df = df.copy()
    df["calificacion"] = df["vote_average"].where(df["vote_count"] >= min_votos)
    return df


# ───────────────────────── Atributos multivalor ─────────────────────────
def explotar(df: pd.DataFrame, col: str, nuevo: str) -> pd.DataFrame:
    t = df[["uid", col]].copy()
    t[nuevo] = t[col].astype(str).str.split(",")
    t = t.explode(nuevo).drop(columns=col)
    t[nuevo] = t[nuevo].str.strip()
    return t[~t[nuevo].isin(SIN_DATO)].reset_index(drop=True)


def tablas_multivalor(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Una fila por (título, atributo). Se relacionan con `df` por `uid`."""
    return {
        "genero": explotar(df, "genres", "genero"),
        "pais": explotar(df, "country", "pais"),
        "director": explotar(df, "director", "director_n"),
        "actor": explotar(df, "cast", "actor"),
    }


def unir_metricas(tabla: pd.DataFrame, df_f: pd.DataFrame) -> pd.DataFrame:
    """Restringe una tabla multivalor a los títulos filtrados y le agrega sus métricas."""
    return tabla[tabla["uid"].isin(df_f["uid"])].merge(df_f[METRICAS], on="uid")


# ───────────────────────── Filtros ─────────────────────────
def filtrar(df, tablas, tipo=None, anios=None, calificacion=None, generos=None,
            paises=None, idiomas=None) -> pd.DataFrame:
    """Aplica todos los filtros del dashboard. None / lista vacía = sin filtrar."""
    m = pd.Series(True, index=df.index)
    if tipo:
        m &= df["type"].isin(tipo)
    if anios:
        m &= df["release_year"].between(*anios)
    if calificacion and tuple(calificacion) != (0, 10):
        m &= df["calificacion"].between(*calificacion)
    if generos:
        m &= df["uid"].isin(tablas["genero"].loc[tablas["genero"]["genero"].isin(generos), "uid"])
    if paises:
        m &= df["uid"].isin(tablas["pais"].loc[tablas["pais"]["pais"].isin(paises), "uid"])
    if idiomas:
        m &= df["idioma"].isin(idiomas)
    return df[m].copy()


# ───────────────────────── Agregaciones ─────────────────────────
def resumen_por(df_exp: pd.DataFrame, clave: str) -> pd.DataFrame:
    return (df_exp.groupby(clave)
            .agg(n=("uid", "nunique"),
                 popularidad_prom=("popularity", "mean"),
                 popularidad_mediana=("popularity", "median"),
                 calificacion_prom=("calificacion", "mean"),
                 roi_mediano=("roi_pct", "median"))
            .reset_index())


def puntaje(df: pd.DataFrame, columnas: list[str]) -> pd.DataFrame:
    """Puntaje exploratorio: promedio de percentiles (0 = peor, 1 = mejor) de cada métrica."""
    out = df.dropna(subset=columnas).copy()
    out["puntaje"] = out[columnas].rank(pct=True).mean(axis=1)
    return out.sort_values("puntaje", ascending=False)


def kpis_financieros(df_fin: pd.DataFrame) -> dict[str, float]:
    if df_fin.empty:
        return {}
    pres, ing = df_fin["budget_musd"].sum(), df_fin["revenue_musd"].sum()
    return {
        "presupuesto_prom": df_fin["budget_musd"].mean(),
        "presupuesto_total": pres,
        "ingresos_total": ing,
        "roi_aprox": (ing - pres) / pres * 100,      # sobre el agregado (más estable que promediar ROI)
        "roi_mediano": df_fin["roi_pct"].median(),
    }