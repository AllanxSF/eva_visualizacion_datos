import pandas as pd


COLS_TEXTO = [
    "type",
    "title",
    "director",
    "cast",
    "country",
    "genres",
    "language",
    "description"
]


COLS_REQUERIDAS = {
    "show_id",
    "type",
    "title",
    "director",
    "cast",
    "country",
    "date_added",
    "release_year",
    "rating",
    "duration",
    "genres",
    "language",
    "description",
    "popularity",
    "vote_count",
    "vote_average",
}


def limpieza_datos(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y prepara los datasets de StreamView Analytics.
    """

    df = df.copy()

    # Normalizar nombres de columnas
    df.columns = df.columns.str.lower().str.strip()

    # Validar columnas requeridas
    faltantes = COLS_REQUERIDAS - set(df.columns)

    if faltantes:
        raise ValueError(
            f"Columnas faltantes: {faltantes}"
        )

    # Limpiar variables de texto
    for col in COLS_TEXTO:
        df[col] = df[col].astype("string").str.strip()

    # Tratamiento de valores nulos
    df["director"] = df["director"].fillna("Desconocido")
    df["cast"] = df["cast"].fillna("Desconocido")
    df["country"] = df["country"].fillna("Desconocido")
    df["genres"] = df["genres"].fillna("Desconocido")
    df["description"] = df["description"].fillna("Sin descripción")

    # Eliminar duration solamente si está completamente vacía
    if df["duration"].isna().all():
        df = df.drop(columns=["duration"])

    # Convertir fecha
    df["date_added"] = pd.to_datetime(
        df["date_added"],
        errors="coerce"
    )

    # Convertir variables numéricas
    columnas_numericas = [
        "show_id",
        "release_year",
        "rating",
        "popularity",
        "vote_count",
        "vote_average"
    ]

    for col in columnas_numericas:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # Eliminar duplicados exactos
    df = df.drop_duplicates()

    return df