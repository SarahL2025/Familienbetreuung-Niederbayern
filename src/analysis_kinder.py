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
    return long_df

# =========================
# Plot
# =========================
def plot_lines(long_df: pd.DataFrame, title: str, y_label: str, out_name: str):
    piv = long_df.pivot_table(index="Jahr", columns="Raumeinheit", values="Wert", aggfunc="first").sort_index()

    fig, ax = plt.subplots(figsize=(14, 7))
    piv.plot(ax=ax, linewidth=2)

    ax.set_title(title, pad=12)
    ax.set_xlabel("Jahr")
    ax.set_ylabel(y_label)

    years = piv.index.dropna().astype(int).tolist()
    if years:
        step = 2
        xticks = years[::step]
        ax.set_xticks(xticks)
        ax.set_xticklabels([str(y) for y in xticks], rotation=45, ha="right")

    ax.grid(True, linewidth=0.6, alpha=0.35)
    ax.legend(title="Landkreis / Region", loc="center left", bbox_to_anchor=(1.02, 0.5), frameon=False)

    plt.tight_layout()
    plt.savefig(os.path.join(PROJECT_ROOT, out_name), dpi=200, bbox_inches="tight")
    plt.show()

# =========================
# Hauptteil
# =========================
def main():
    df_kinder = read_inkar_table(FILES["Kinder_0_6"])
    plot_lines(df_kinder, "Einwohner unter 6 Jahre in Niederbayern (2003–2023)", "Einwohner unter 6 Jahre", "plot_kinder_0_6.png")

    df_betreuung = read_inkar_table(FILES["Kinderbetreuung"])
    plot_lines(df_betreuung, "Betreuungsquote Kleinkinder in Niederbayern (2003–2023)", "Betreuungsquote (%)", "plot_kinderbetreuung.png")

    df_geborene = read_inkar_table(FILES["Geborene"])
    plot_lines(df_geborene, "Geborene in Niederbayern (2003–2023)", "Geborene", "plot_geborene.png")

    df_frauen = read_inkar_table(FILES["Erwerbstätige_Frauen"])
    plot_lines(df_frauen, "Beschäftigtenquote Frauen in Niederbayern (2003–2023)", "Beschäftigtenquote Frauen (%)", "plot_erwerbstaetige_frauen.png")

if __name__ == "__main__":
    main()
