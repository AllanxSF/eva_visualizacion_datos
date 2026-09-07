

def agregar_control_financiero(df):
    df = df.copy()

    # Identificar valores financieros pequeños que pueden
    # estar expresados en una escala diferente.
    df["budget_status"] = df["budget"].apply(
        lambda x: "Revisar escala" if x < 1_000_000 else "Escala consistente"
    )

    df["revenue_status"] = df["revenue"].apply(
        lambda x: "Revisar escala" if x < 1_000_000 else "Escala consistente"
    )

    return df


def resumen_financiero(df):
    return {
        "total_registros": len(df),
        "budget_revisar": (df["budget_status"] == "Revisar escala").sum(),
        "budget_consistente": (df["budget_status"] == "Escala consistente").sum(),
        "revenue_revisar": (df["revenue_status"] == "Revisar escala").sum(),
        "revenue_consistente": (df["revenue_status"] == "Escala consistente").sum()
    }