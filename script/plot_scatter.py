"""plot_scatter.py

Create an interactive scatter visualisation that summarises the integrated
Eurostat transport and climate indicators at country level (one point per
country, averaged across available years).

Inputs:
- ``data/output/integrated_eurostat_transport_climate.csv`` (produced by
    ``clean_data.py``).

Outputs:
- Interactive HTML: ``data/output/transport_climate_scatter.html``;
- Optional static renders: PNG and SVG in ``data/output/`` (requires
    ``kaleido`` for static export).

Visual encodings:
- X: share of buses+trains (%)
- Y: road CO2 per capita (kg/hab)
- Color: total GHG per capita (tCO2e/hab)

Citation: Eurostat (SDG_09_50, SDG_13_10, ENV_AC_AIBRID_RD)
"""

from pathlib import Path
import sys
import pandas as pd
import numpy as np

OUT_CSV = Path("data/output/integrated_eurostat_transport_climate.csv")
OUT_HTML = Path("data/output/transport_climate_scatter.html")
OUT_PNG = Path("data/output/transport_climate_scatter.png")
OUT_SVG = Path("data/output/transport_climate_scatter.svg")

def main():
    if not OUT_CSV.exists():
        print(f"File not found: {OUT_CSV}. Run `clean_data.py` first.")
        sys.exit(1)

    df = pd.read_csv(OUT_CSV)

    # Ensure numeric types
    for col in ["share_buses_trains", "road_co2_per_capita_g", "ghg_per_capita", "year"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Average per country (one point per country)
    grp = df.groupby("country").agg(
        share_buses_trains=("share_buses_trains", "mean"),
        road_co2_per_capita_g=("road_co2_per_capita_g", "mean"),
        ghg_per_capita=("ghg_per_capita", "mean"),
        year_min=("year", "min"),
        year_max=("year", "max"),
        years_count=("year", "nunique"),
    ).reset_index()

    # Convert road CO2 from g/hab to kg/hab for interpretability
    grp["road_co2_per_capita_kg"] = grp["road_co2_per_capita_g"] / 1000.0

    # Format year range for hover
    grp["year_min"] = grp["year_min"].astype(pd.Int64Dtype())
    grp["year_max"] = grp["year_max"].astype(pd.Int64Dtype())
    grp["year_range"] = grp.apply(lambda r: f"{r.year_min}-{r.year_max}" if pd.notna(r.year_min) and pd.notna(r.year_max) else "n/a", axis=1)

    try:
        import plotly.express as px
    except Exception:
        print("The `plotly` module is not installed. Install it with:\n  .\\venv\\Scripts\\python.exe -m pip install plotly")
        sys.exit(2)

    # Map country codes to full names using pycountry when available
    try:
        import pycountry
    except Exception:
        pycountry = None

    def code_to_name(code: str) -> str:
        if not isinstance(code, str) or not code:
            return code
        c = code.upper()
        # common exceptional mappings
        exceptions = {
            "EL": "Greece",
            "UK": "United Kingdom",
            "XK": "Kosovo",
        }
        if c in exceptions:
            return exceptions[c]
        if pycountry is not None:
            try:
                country = pycountry.countries.get(alpha_2=c)
                if country is not None:
                    return country.name
            except Exception:
                pass
        # fallback: return the code itself
        return code

    grp["country_name"] = grp["country"].apply(code_to_name)

    # Scatter: color by ghg_per_capita, fixed marker size
    custom_scale = [
        "#E6F4E6",  # very light green (low GHG)
        "#7FB769",  # olive green
        "#EAB676",  # warm light
        "#B22222",  # firebrick red
        "#5B0F00",  # very dark brown/red (high GHG)
    ]

    import plotly.express as px
    import plotly.graph_objects as go

    fig = px.scatter(
        grp,
        x="share_buses_trains",
        y="road_co2_per_capita_kg",
        color="ghg_per_capita",
        color_continuous_scale=custom_scale,
        hover_name="country_name",
        hover_data={
            "year_range": True,
            "years_count": True,
            "share_buses_trains": ":.2f",
            "road_co2_per_capita_kg": ":.2f",
            "ghg_per_capita": ":.2f",
        },
        labels={
            "share_buses_trains": "Share buses+trains (%)",
            "road_co2_per_capita_kg": "Road CO2 per capita (kg/hab)",
            "ghg_per_capita": "GHG per capita (tCO2e/hab)",
        },
        title="Public transport share vs. Road CO₂ emissions (EU countries)",
    )

    # Fix marker size (no size-encoding) and add thin outline for clarity
    fig.update_traces(marker=dict(size=45, line=dict(width=0.6, color='DarkSlateGrey')))
    # Improve layout: vertical colorbar on the right, title + subtitle, source
    try:
        fig.update_layout(showlegend=False)

        # Set a vertical colorbar on the right side with clear title
        fig.update_coloraxes(colorbar=dict(
            title="GHG per capita (tCO2e/hab)",
            orientation='v',
            y=0.5,
            x=1.02,
            xanchor='left',
            len=0.8,
            thickness=14,
        ))
        # Title with subtitle
        fig.update_layout(title={
            'text': "Public transport share vs. Road CO₂ emissions (EU countries)<br><sup>With total GHG per capita encoded as color</sup>",
            'y':0.98,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        })

        # Source annotation bottom-right
        fig.add_annotation(dict(
            x=1,
            y=0,
            xref='paper',
            yref='paper',
            xanchor='right',
            yanchor='bottom',
            text='Source: Eurostat (SDG_09_50, SDG_13_10, ENV_AC_AIBRID_RD)',
            showarrow=False,
            font=dict(size=10, color='gray')
        ))

        fig.update_layout(margin=dict(l=70, r=140, t=110, b=80))
    except Exception:
        pass

    # Add a linear regression line (OLS) to show trend
    try:
        x = grp['share_buses_trains'].to_numpy(dtype=float)
        y = grp['road_co2_per_capita_kg'].to_numpy(dtype=float)
        mask = np.isfinite(x) & np.isfinite(y)
        if mask.sum() >= 2:
            xm = x[mask]
            ym = y[mask]
            coeffs = np.polyfit(xm, ym, 1)
            slope, intercept = coeffs[0], coeffs[1]
            y_pred = slope * xm + intercept
            # R-squared
            ss_res = np.sum((ym - y_pred) ** 2)
            ss_tot = np.sum((ym - np.mean(ym)) ** 2)
            r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0.0

            # line coordinates (over full x range)
            x_line = np.linspace(np.nanmin(xm), np.nanmax(xm), 100)
            y_line = slope * x_line + intercept
            fig.add_trace(go.Scatter(x=x_line, y=y_line,
                                     mode='lines',
                                     line=dict(color='black', width=2, dash='dash'),
                                     name='Linear trend',
                                     hoverinfo='skip'))

            # Add an annotation with slope and R²
            fig.add_annotation(dict(
                x=0.02,
                y=0.95,
                xref='paper',
                yref='paper',
                xanchor='left',
                yanchor='top',
                text=f"Trend: slope={slope:.3f} kg per %; R²={r2:.3f}",
                showarrow=False,
                font=dict(size=11, color='black'),
                bgcolor='rgba(255,255,255,0.7)',
                bordercolor='rgba(0,0,0,0.1)',
                borderwidth=0,
            ))
    except Exception:
        pass

    try:
        # Decide label color based on GHG intensity so labels remain readable
        # If ghg_per_capita is above the median, marker color tends to be darker -> use white labels
        ghg_med = np.nanmedian(grp['ghg_per_capita'].to_numpy(dtype=float))
        label_colors = np.where(grp['ghg_per_capita'] > ghg_med, 'white', 'black')

        fig.add_trace(go.Scatter(
            x=grp['share_buses_trains'],
            y=grp['road_co2_per_capita_kg'],
            mode='text',
            text=grp['country'],
            textposition='bottom center',
            textfont=dict(size=11, color=label_colors),
            showlegend=False,
            hoverinfo='skip'
        ))
    except Exception:
        pass
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(OUT_HTML, include_plotlyjs='cdn')
    print(f"Interactive HTML saved: {OUT_HTML}")
    # Try to save static images (requires kaleido)
    try:
        fig.write_image(OUT_PNG, scale=2)
        fig.write_image(OUT_SVG)
        print(f"Static images saved: {OUT_PNG} , {OUT_SVG}")
    except Exception as e:
        print("Unable to write static images (kaleido may be missing).")
        print("To install: .\\venv\\Scripts\\python.exe -m pip install kaleido")
        print("Error:", e)

    # Open interactive view in default browser if environment supports it
    try:
        fig.show()
    except Exception:
        pass


if __name__ == "__main__":
    main()
