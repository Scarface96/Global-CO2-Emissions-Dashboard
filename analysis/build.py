"""Run the CO2 analysis and write the website to site/index.html.

    python -m analysis.build
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from . import data
from .report import AXIS, BLUE, GRID, INK_2, MUTED, ORANGE, SEQUENTIAL, SERIES, Report, style, to_json

REPO = "Scarface96/Global-CO2-Emissions-Dashboard"
RESPONSIBILITY = ["United States", "China", "European Union (27)", "Russia", "United Kingdom", "Japan", "India", "Africa"]
DECOUPLING = ["United Kingdom", "Germany", "United States", "China", "India", "South Africa"]


def fuel_figure(w: pd.DataFrame) -> go.Figure:
    w = w.loc[1850:]
    fig = go.Figure()
    for i, f in enumerate(data.FUELS):
        fig.add_scatter(x=w.index, y=w[f].fillna(0) / 1000, name=data.FUEL_LABELS[f], mode="lines", stackgroup="one",
                        line=dict(width=0.5, color=SERIES[i]), fillcolor=SERIES[i],
                        hovertemplate=f"{data.FUEL_LABELS[f]}: %{{y:.1f}} Gt in %{{x}}<extra></extra>")
    style(fig, height=420)
    fig.update_yaxes(title="Billion tonnes of CO₂ per year")
    fig.update_layout(hovermode="x unified")
    return fig


def map_figure(c: pd.DataFrame, start: int = 1960, end: int = 2021) -> go.Figure:
    d = c[c["year"].between(start, end)].dropna(subset=["co2_per_capita"])
    scale = [[i / (len(SEQUENTIAL) - 1), col] for i, col in enumerate(SEQUENTIAL)]
    cap = 20

    def trace(y):
        g = d[d["year"] == y]
        return go.Choropleth(
            locations=g["iso_code"], z=g["co2_per_capita"].clip(upper=cap), customdata=np.stack([g["country"], g["co2_per_capita"]], axis=1),
            colorscale=scale, zmin=0, zmax=cap, marker_line_color="#fcfcfb", marker_line_width=0.4,
            colorbar=dict(title=dict(text="Tonnes per<br>person"), thickness=12, outlinewidth=0, ticksuffix=" t", len=0.7),
            hovertemplate="%{customdata[0]}<br>%{customdata[1]:.1f} t CO₂ per person<extra></extra>",
        )

    fig = go.Figure(data=[trace(end)], frames=[go.Frame(data=[trace(y)], name=str(y)) for y in range(start, end + 1)])
    steps = [dict(method="animate", label=str(y), args=[[str(y)], dict(mode="immediate", frame=dict(duration=0, redraw=True), transition=dict(duration=0))]) for y in range(start, end + 1)]
    fig.update_layout(
        sliders=[dict(active=end - start, steps=steps, x=0.05, len=0.9, y=0, currentvalue=dict(prefix="Year ", font=dict(size=14, color=INK_2)), pad=dict(t=8), tickcolor=AXIS, font=dict(color=MUTED, size=10))],
        updatemenus=[dict(type="buttons", showactive=False, x=0.0, y=0.02, xanchor="right", yanchor="top", pad=dict(r=8, t=8),
                          buttons=[dict(label="▶ Play", method="animate", args=[None, dict(frame=dict(duration=180, redraw=True), fromcurrent=False, transition=dict(duration=0))])])],
        geo=dict(showframe=False, showcoastlines=False, projection_type="natural earth", bgcolor="#fcfcfb", landcolor="#efeee9", showland=True, lataxis_range=[-58, 85]),
    )
    style(fig, height=520)
    fig.update_layout(margin=dict(l=0, r=0, t=8, b=40))
    return fig


def rankings_figure(r: dict, year: int) -> go.Figure:
    titles = [f"Total, {year} (Mt)", f"Per person, {year} (t)", "All-time total since 1750 (Gt)"]
    fig = make_subplots(rows=1, cols=3, subplot_titles=titles, horizontal_spacing=0.17)
    specs = [("total", "co2", 1, "Mt"), ("per_capita", "co2_per_capita", 1, "t per person"), ("cumulative", "cumulative_co2", 1000, "Gt")]
    for i, (key, col, div, unit) in enumerate(specs, 1):
        t = r[key].iloc[::-1]
        hl = [ORANGE if n in ("United States", "China") else BLUE for n in t["country"]]
        fig.add_bar(y=t["country"], x=t[col] / div, orientation="h", marker_color=hl, showlegend=False,
                    hovertemplate=f"%{{y}}: %{{x:,.1f}} {unit}<extra></extra>", row=1, col=i)
    style(fig, height=420)
    fig.update_annotations(font=dict(size=14, color=INK_2))
    fig.update_yaxes(showgrid=False, tickfont=dict(size=12))
    fig.update_xaxes(showgrid=True, gridcolor=GRID)
    return fig


def responsibility_figure(t: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    labels = {"share_cumulative": "Share of all CO₂ ever emitted", "share_annual": "Share of this year's CO₂", "share_population": "Share of world population"}
    for i, (col, name) in enumerate(labels.items()):
        fig.add_bar(x=t["country"], y=t[col], name=name, marker_color=SERIES[i], hovertemplate=f"%{{x}}<br>{name}: %{{y:.1%}}<extra></extra>")
    style(fig, height=420)
    fig.update_layout(barmode="group", bargroupgap=0.06)
    fig.update_yaxes(tickformat=".0%")
    return fig


def decoupling_figure(ix: pd.DataFrame, base: int) -> go.Figure:
    names = [n for n in DECOUPLING if n in set(ix["country"])]
    fig = make_subplots(rows=2, cols=3, subplot_titles=names, shared_xaxes=True, vertical_spacing=0.14, horizontal_spacing=0.06)
    for i, name in enumerate(names):
        g = ix[ix["country"] == name]
        row, col = i // 3 + 1, i % 3 + 1
        fig.add_scatter(x=g["year"], y=g["gdp_index"], name="GDP", mode="lines", line=dict(color=BLUE, width=2), showlegend=i == 0, legendgroup="gdp",
                        hovertemplate=f"{name} %{{x}}<br>GDP index %{{y:.0f}}<extra></extra>", row=row, col=col)
        fig.add_scatter(x=g["year"], y=g["co2_index"], name="CO₂", mode="lines", line=dict(color=ORANGE, width=2), showlegend=i == 0, legendgroup="co2",
                        hovertemplate=f"{name} %{{x}}<br>CO₂ index %{{y:.0f}}<extra></extra>", row=row, col=col)
        fig.add_hline(y=100, line=dict(color=AXIS, width=1), row=row, col=col)
    style(fig, height=560)
    fig.update_annotations(font=dict(size=14, color=INK_2))
    fig.update_yaxes(type="log", tickvals=[50, 100, 200, 400, 800], title_text="")
    fig.add_annotation(text=f"Index, {base} = 100 (log scale)", x=0, xref="paper", y=1.13, yref="paper", showarrow=False, xanchor="left", yanchor="bottom", font=dict(size=12, color=MUTED))
    fig.update_layout(margin=dict(t=64), legend=dict(x=1, xanchor="right", y=1.13, yanchor="bottom"))
    return fig


def trend_figure(t: pd.DataFrame, start: int, end: int) -> go.Figure:
    colors = [BLUE if v < 0 else ORANGE for v in t["annual_change"]]
    fig = go.Figure(go.Bar(x=t["annual_change"], y=t["country"], orientation="h", marker_color=colors,
                           customdata=t["co2_latest"], hovertemplate="%{y}<br>%{x:+.1%} a year<br>%{customdata:,.0f} Mt in " + str(end) + "<extra></extra>"))
    style(fig, height=640, legend=False)
    fig.update_xaxes(tickformat="+.0%", showgrid=True, gridcolor=GRID, zeroline=True, zerolinecolor=AXIS, title=f"Average change per year, {start}–{end}")
    fig.update_yaxes(showgrid=False, tickfont=dict(size=12))
    return fig


EXPLORER = """
<form class="controls" onsubmit="return false">
  <label>Country<select id="ex-a"></select></label>
  <label>Compare per person with<select id="ex-b"></select></label>
</form>
<div class="readout" aria-live="polite">
  <div><b id="ex-total">–</b><span id="ex-total-l">emitted in the latest year</span></div>
  <div><b id="ex-pc">–</b><span>tonnes per person</span></div>
  <div><b id="ex-peak">–</b><span>peak year</span></div>
  <div><b id="ex-change">–</b><span>change since 1990</span></div>
</div>
<figure class="chart"><div id="ex-fuel" style="height:340px"></div></figure>
<figure class="chart"><div id="ex-pcchart" style="height:300px"></div></figure>
"""


def explorer_js(payload: dict) -> str:
    fuels = [("coal_co2", "Coal"), ("oil_co2", "Oil"), ("gas_co2", "Gas"), ("cement_co2", "Cement")]
    return f"""
(function(){{
const D={to_json(payload)};
const F={to_json(fuels)}, C={to_json(SERIES[:4])};
const $=id=>document.getElementById(id);
const names=Object.keys(D).sort((a,b)=>a==='World'?-1:b==='World'?1:a.localeCompare(b));
names.forEach(n=>{{$('ex-a').add(new Option(n,n)); $('ex-b').add(new Option(n,n));}});
$('ex-a').value=D['South Africa']?'South Africa':names[1]; $('ex-b').value='World';
const base={{paper_bgcolor:'#fcfcfb',plot_bgcolor:'#fcfcfb',margin:{{l:8,r:16,t:30,b:8}},font:{{family:'"Public Sans",system-ui,sans-serif',size:13,color:'{INK_2}'}},
  hoverlabel:{{bgcolor:'white',bordercolor:'{AXIS}'}},legend:{{orientation:'h',x:0,y:1.12}},xaxis:{{showgrid:false,linecolor:'{AXIS}',automargin:true}},yaxis:{{gridcolor:'{GRID}',automargin:true}}}};
const fmt=v=>v>=1000?(v/1000).toFixed(2)+' Gt':v.toFixed(v<10?1:0)+' Mt';
function draw(){{
  const a=D[$('ex-a').value], b=D[$('ex-b').value], an=$('ex-a').value, bn=$('ex-b').value;
  const tr=F.map(([k,l],i)=>({{x:a.year,y:a[k].map(v=>v??0),name:l,type:'scatter',mode:'lines',stackgroup:'one',line:{{width:0.5,color:C[i]}},fillcolor:C[i],hovertemplate:l+': %{{y:,.1f}} Mt<extra></extra>'}}));
  tr.push({{x:a.year,y:a.co2,name:'Total',type:'scatter',mode:'lines',line:{{color:'#0b0b0b',width:1.5,dash:'dot'}},hovertemplate:'Total: %{{y:,.1f}} Mt<extra></extra>'}});
  Plotly.react('ex-fuel',tr,Object.assign({{}},base,{{hovermode:'x unified',yaxis:Object.assign({{}},base.yaxis,{{title:{{text:an+': CO₂ by source (Mt per year)'}}}})}}),{{displaylogo:false,responsive:true}});
  const pc=[[a,an,'{BLUE}'],[b,bn,'{ORANGE}']].filter((x,i)=>i===0||bn!==an).map(([d,n,c])=>({{x:d.year,y:d.co2_per_capita,name:n,type:'scatter',mode:'lines',line:{{color:c,width:2}},hovertemplate:n+' %{{x}}: %{{y:.1f}} t per person<extra></extra>'}}));
  Plotly.react('ex-pcchart',pc,Object.assign({{}},base,{{yaxis:Object.assign({{}},base.yaxis,{{title:{{text:'Tonnes of CO₂ per person'}},rangemode:'tozero'}})}}),{{displaylogo:false,responsive:true}});
  const i=a.co2.length-1, last=a.co2[i]; let pk=0; a.co2.forEach((v,j)=>{{if(v!=null&&v>a.co2[pk]) pk=j;}});
  const j90=a.year.indexOf(1990);
  $('ex-total').textContent=fmt(last); $('ex-total-l').textContent='emitted in '+a.year[i];
  $('ex-pc').textContent=a.co2_per_capita[i]!=null?a.co2_per_capita[i].toFixed(1):'–';
  $('ex-peak').textContent=a.year[pk];
  $('ex-change').textContent=j90>=0&&a.co2[j90]?((last/a.co2[j90]-1)*100>=0?'+':'')+((last/a.co2[j90]-1)*100).toFixed(0)+'%':'–';
}}
['ex-a','ex-b'].forEach(id=>$(id).addEventListener('input',draw)); draw();
}})();
"""


def main(out="site/index.html"):
    df = data.load()
    c = data.countries(df)
    w = data.world(df)
    year = data.latest_year(df)
    ranks = data.rankings(c, year)
    resp = data.responsibility(df, year, RESPONSIBILITY)
    rs = resp.set_index("country")
    ix = data.indexed(c, DECOUPLING, 1990, 2018)
    dec = data.decoupled(c, 1990, 2018)
    trend = data.recent_trend(c, year - 10, year)
    wl = w.loc[year]
    since_1990 = wl["co2"] / w.loc[1990, "co2"] - 1
    coal_share = wl["coal_co2"] / wl["co2"]
    falling = trend[trend["annual_change"] < 0]["country"].tolist()

    r = Report(
        title=f"The United States has emitted {rs.loc['United States', 'share_cumulative']:.0%} of all CO₂ in history. China now emits {rs.loc['China', 'share_annual']:.0%} of each year's.",
        project="Global CO₂ Emissions",
        summary=(
            f"The world emitted {wl['co2'] / 1000:.1f} billion tonnes of CO₂ from fossil fuels and industry in {year}, "
            f"{since_1990:.0%} more than in 1990. Who is \"the biggest emitter\" depends entirely on how you count: by year, per person, or over history."
        ),
        repo=REPO,
        accent=SERIES[2],
        source='Our World in Data CO₂ and greenhouse gas dataset (visualizing_global_co2_data.csv), 1750–2021, built on the Global Carbon Project. <a href="https://github.com/owid/co2-data">owid/co2-data</a>.',
        method=(
            "pandas separates real countries (ISO codes) from regional aggregates. Shares use the dataset's World row. Decoupling compares "
            "1990 and 2018, the last year with GDP. Recent trends are log-linear fits with numpy, so each bar is an average yearly % change."
        ),
    )
    r.kpis([
        (f"{wl['co2'] / 1000:.1f} Gt", f"CO₂ emitted in {year}", f"{since_1990:+.0%} since 1990"),
        (f"{wl['co2_per_capita']:.1f} t", "per person, world average"),
        (f"{coal_share:.0%}", "of it from coal"),
        (f"{int(dec['decoupled'].sum())} of {len(dec)}", "large emitters grew GDP while cutting CO₂", "1990–2018"),
    ])

    wt = w.loc[1850:, ["co2"] + data.FUELS].reset_index().rename(columns={**data.FUEL_LABELS, "co2": "total"}).round(0)
    r.section(
        "Where does the world's CO₂ come from?",
        f"<p>Coal built the industrial world and is still the largest single source, at <b>{coal_share:.0%}</b> of emissions in {year}. "
        "Oil took off after 1950 and gas after 1970. The dips in the record line up with crises, the Great Depression, the early-1980s oil shock, "
        "2009 and the 2020 pandemic, and emissions climbed again after every one.</p>",
        fig=fuel_figure(w), table=wt[wt["year"] % 10 == 1].tail(18), note="Hover anywhere on the chart to read every source for that year.",
    )
    r.section(
        "How has emitting per person spread around the world?",
        "<p>Press play to watch 1960 to 2021. North America, Australia and the Gulf states stay darkest throughout, while China moves from among the lowest "
        "to above the European average. Much of Africa remains under one tonne per person.</p>",
        fig=map_figure(c, 1960, year), note="Colours stop at 20 t so the rest of the world stays readable; a few Gulf states are higher. Hover for exact values.",
    )
    rk = pd.concat([v.reset_index(drop=True).set_axis(["country", "value"], axis=1).assign(ranking=k) for k, v in ranks.items()])
    r.section(
        "Who is the biggest emitter?",
        "<p>Three honest answers. By total emissions today, <b>China</b> leads by a wide margin. Per person, small oil and gas producers top the list, "
        "with Australia and the United States the only large economies outside the Gulf in the top ten. Over all of history, the <b>United States</b> has emitted the most, with China second.</p>",
        fig=rankings_figure(ranks, year), table=rk.round(1), note="US and China highlighted. The per-person ranking only includes countries with at least one million people.",
    )
    rt = resp.copy()
    for col in ["share_cumulative", "share_annual", "share_population"]:
        rt[col] = (rt[col] * 100).round(1)
    r.section(
        "Who is responsible for the CO₂ already in the air?",
        f"<p>Warming tracks the total emitted over time, not any single year. The US holds <b>{rs.loc['United States', 'share_cumulative']:.0%}</b> of "
        f"all historical emissions with {rs.loc['United States', 'share_population']:.0%} of the world's people, and the EU another {rs.loc['European Union (27)', 'share_cumulative']:.0%}. "
        f"<b>Africa</b>, home to {rs.loc['Africa', 'share_population']:.0%} of humanity, accounts for just {rs.loc['Africa', 'share_cumulative']:.0%}. "
        f"India's share of the population is {rs.loc['India', 'share_population'] / rs.loc['India', 'share_cumulative']:.0f} times its share of historical CO₂.</p>",
        fig=responsibility_figure(resp),
        table=rt.rename(columns={"share_cumulative": "% of all-time CO₂", "share_annual": f"% of {year} CO₂", "share_population": "% of population"}),
    )
    dect = dec[dec["decoupled"]].copy()
    dect["co2_change"] = (dect["co2_change"] * 100).round(0)
    dect["gdp_change"] = (dect["gdp_change"] * 100).round(0)
    at = lambda n: ix[(ix["country"] == n) & (ix["year"] == 2018)].iloc[0]
    uk, us, sa = at("United Kingdom"), at("United States"), at("South Africa")
    r.section(
        "Can an economy grow while emissions fall?",
        f"<p>Yes, and many have. Between 1990 and 2018, <b>{int(dec['decoupled'].sum())} of the {len(dec)} countries</b> emitting over 10 Mt grew their economies while "
        f"cutting CO₂. The <b>United Kingdom</b> is the clearest large example: GDP up {uk['gdp_index'] - 100:.0f}%, CO₂ down {100 - uk['co2_index']:.0f}%. "
        f"The US doubled its economy with CO₂ almost flat ({us['co2_index'] - 100:+.0f}%). South Africa's GDP nearly tripled while CO₂ rose "
        f"{sa['co2_index'] - 100:.0f}%, a partial decoupling. China and India grew both together.</p>",
        fig=decoupling_figure(ix, 1990),
        table=dect[["country", "gdp_change", "co2_change"]].rename(columns={"gdp_change": "GDP change %", "co2_change": "CO₂ change %"}),
        table_caption="Show the countries that decoupled",
        note="Production-based emissions. Some decoupling reflects manufacturing moving abroad.",
    )
    tt = trend.copy()
    tt["annual_change"] = (tt["annual_change"] * 100).round(2)
    r.section(
        f"Which big emitters are cutting, and which are still growing?",
        f"<p>Among the 25 largest emitters, {len(falling)} have trended down over {year - 10}–{year}, led by the UK, Italy, Japan and Germany at "
        "2–4% a year. Fast-growing economies are rising: India by about 4% a year, Vietnam by about 10%. China, already the largest, still grew about 1.6% a year.</p>",
        fig=trend_figure(trend, year - 10, year),
        table=tt.round(1).rename(columns={"annual_change": "avg change per year %", "co2_latest": f"Mt in {year}"}),
    )
    r.section(
        "Explore any country",
        "<p>Pick a country to see where its emissions come from since 1950, and compare its emissions per person with any other country or the world.</p>",
        html=EXPLORER,
    )
    r.script(explorer_js(data.explorer_payload(c, w)))

    path = r.write(out)
    print(f"Wrote {path} ({path.stat().st_size / 1024:.0f} KB).")
    return r


if __name__ == "__main__":
    main()
