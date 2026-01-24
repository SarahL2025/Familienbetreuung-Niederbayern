import os
import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Projektpfade: Script liegt in /src, Daten liegen in /data
# =========================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))      # eine Ebene hoch
DATA_DIR = os.path.join(PROJECT_ROOT, "data")                      # data-Ordner

FILES = {
    "Kinder_0_6": os.path.join(DATA_DIR, "kinder_0_6.csv"),
    "Kinderbetreuung": os.path.join(DATA_DIR, "Tabelle Kinderbetreuung.csv"),
    "Geborene": os.path.join(DATA_DIR, "Geborene.csv"),
    "Erwerbstätige_Frauen": os.path.join(DATA_DIR, "Erwerbstätige Frauen.csv"),
}

YEAR_START = 2003
YEAR_END = 2023


# =========================
# INKAR CSV einlesen (Jahre sind in der ersten Datenzeile)
# =========================
def read_inkar_table(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Datei nicht gefunden: {path}")

    df = pd.read_csv(path, sep=";", encoding="utf-8-sig", dtype=str)

    # Jahre aus erster Datenzeile (ab Spalte 3)
    years = df.iloc[0, 3:].tolist()
    years = [str(y).strip() for y in years]

    # Daten ab Zeile 1
    df = df.iloc[1:, :].copy()
    df.columns = ["Kennziffer", "Raumeinheit", "Aggregat"] + years

    # Long-Format
    long_df = df.melt(
        id_vars=["Kennziffer", "Raumeinheit", "Aggregat"],
        var_name="Jahr",
        value_name="Wert",
    )

    # Typen bereinigen
    long_df["Jahr"] = pd.to_numeric(long_df["Jahr"], errors="coerce").astype("Int64")
    long_df["Wert"] = (
        long_df["Wert"]
        .astype(str)
        .str.replace("\u00a0", "", regex=False)  # geschützte Leerzeichen
        .str.replace(" ", "", regex=False)       # normale Leerzeichen
        .str.replace(".", "", regex=False)       # Tausenderpunkt weg
        .str.replace(",", ".", regex=False)      # Dezimal-Komma -> Punkt
    )
    long_df["Wert"] = pd.to_numeric(long_df["Wert"], errors="coerce")

    long_df = long_df.dropna(subset=["Jahr"]).sort_values(["Raumeinheit", "Jahr"]).reset_index(drop=True)

    # Auf gewünschten Zeitraum begrenzen
    long_df = long_df[(long_df["Jahr"] >= YEAR_START) & (long_df["Jahr"] <= YEAR_END)].copy()

    return long_df


# =========================
# Helfer: Top 3 / Bottom 3 nach letztem verfügbaren Jahr je Region
# =========================
def select_top_bottom_regions(piv: pd.DataFrame, top_n: int = 3, bottom_n: int = 3) -> pd.DataFrame:
    # letztes verfügbares (nicht-NaN) Jahr je Region
    last_vals = piv.apply(lambda col: col.dropna().iloc[-1] if col.dropna().shape[0] > 0 else pd.NA)
    last_vals = last_vals.dropna().astype(float)

    if last_vals.empty:
        return piv  # fallback

    top_regions = last_vals.sort_values(ascending=False).head(top_n).index.tolist()
    bottom_regions = last_vals.sort_values(ascending=True).head(bottom_n).index.tolist()

    # Reihenfolge: erst Top, dann Bottom (ohne Duplikate)
    regions = []
    for r in top_regions + bottom_regions:
        if r not in regions:
            regions.append(r)

    return piv[regions]


# =========================
# Plot (nur Top 3 + Bottom 3) + Jahre 2003–2023
# =========================
def plot_lines_top_bottom(long_df: pd.DataFrame, title: str, y_label: str, out_name: str):
    piv = long_df.pivot_table(index="Jahr", columns="Raumeinheit", values="Wert", aggfunc="first").sort_index()

    # Jahre 2003–2023 immer vollständig anzeigen
    full_years = list(range(YEAR_START, YEAR_END + 1))
    piv = piv.reindex(full_years)

    # Auswahl: Top 3 / Bottom 3
    piv_sel = select_top_bottom_regions(piv, top_n=3, bottom_n=3)

    fig, ax = plt.subplots(figsize=(14, 7))
    piv_sel.plot(ax=ax, linewidth=2)

    ax.set_title(f"{title}\n(Top 3 höchste & Top 3 niedrigste – nach letztem verfügbaren Jahr)", pad=12)
    ax.set_xlabel("Jahr")
    ax.set_ylabel(y_label)

    # Alle Jahre anzeigen
    ax.set_xticks(full_years)
    ax.set_xticklabels([str(y) for y in full_years], rotation=45, ha="right")

    ax.grid(True, linewidth=0.6, alpha=0.35)
    ax.legend(title="Landkreis / Region", loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)

    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_ROOT, out_name), dpi=200, bbox_inches="tight")
    plt.show()


# =========================
# Hauptteil (4 Diagramme)
# =========================
def main():
    # 1) Einwohner unter 6 Jahre (Anteil in %)
    df_kinder = read_inkar_table(FILES["Kinder_0_6"])
    plot_lines_top_bottom(
        df_kinder,
        "Einwohner unter 6 Jahre in Niederbayern (2003–2023)",
        "Anteil der Einwohner unter 6 Jahren an den Einwohnern (%)",
        "plot_kinder_0_6.png",
    )

    # 2) Betreuungsquote Kleinkinder (U3 in Kitas)
    df_betreuung = read_inkar_table(FILES["Kinderbetreuung"])
    plot_lines_top_bottom(
        df_betreuung,
        "Betreuungsquote Kleinkinder in Niederbayern (2006–2023)",
        "Betreuungsquote Kleinkinder (Anteil U3 in Kindertageseinrichtungen, %)",
        "plot_kinderbetreuung.png",
    )

    # 3) Geborene (je 1.000 Einwohner)
    df_geborene = read_inkar_table(FILES["Geborene"])
    plot_lines_top_bottom(
        df_geborene,
        "Geborene in Niederbayern (2003–2023)",
        "Geborene (je 1.000 Einwohner)",
        "plot_geborene.png",
    )

    # 4) Beschäftigte Frauen am Wohnort (je 100 Frauen im erwerbsfähigen Alter, %)
    df_frauen = read_inkar_table(FILES["Erwerbstätige_Frauen"])
    plot_lines_top_bottom(
        df_frauen,
        "Beschäftigte Frauen am Wohnort in Niederbayern (2003–2023)",
        "Beschäftigte Frauen (je 100 Frauen im erwerbsfähigen Alter, %)",
        "plot_erwerbstaetige_frauen.png",
    )


if __name__ == "__main__":
    main()

