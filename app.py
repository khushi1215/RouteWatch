import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="RouteWatch", page_icon="✈", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: radial-gradient(circle at 15% 0%, #10192E 0%, #070B14 55%, #05070D 100%);
    color: #EDEBE3;
}

.block-container {
    max-width: 1180px;
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] { display: none; }
#MainMenu, header, footer { visibility: hidden; }

.rw-hero {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 16px;
    margin-bottom: 6px;
}

.rw-title {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: clamp(28px, 4vw, 42px);
    color: #F2A93B;
    letter-spacing: 0.5px;
}

.rw-live-tag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #3ECF8E;
    border: 1px solid rgba(62,207,142,0.35);
    background: rgba(62,207,142,0.08);
    padding: 5px 12px;
    border-radius: 999px;
    letter-spacing: 1px;
}

.rw-live-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #3ECF8E;
    margin-right: 6px;
    box-shadow: 0 0 6px #3ECF8E;
}

.rw-sub {
    font-size: 15px;
    color: #8A94A6;
    margin-bottom: 36px;
}

.rw-section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #6B7488;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 40px 0 14px;
}

.rw-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 14px;
}

.rw-route-card {
    background: rgba(19, 28, 46, 0.55);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 22px 24px;
    position: relative;
    overflow: hidden;
}

.rw-route-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}

.rw-route-card.rw-high-delay::before { background: linear-gradient(90deg, #E85D4A, transparent); }
.rw-route-card.rw-low-delay::before { background: linear-gradient(90deg, #3ECF8E, transparent); }

.rw-route-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 20px;
    font-weight: 700;
    color: #EDEBE3;
    margin-bottom: 4px;
}

.rw-route-meta {
    font-size: 13px;
    color: #6B7488;
    margin-bottom: 18px;
}

.rw-route-pct {
    font-family: 'JetBrains Mono', monospace;
    font-size: 40px;
    font-weight: 700;
    line-height: 1;
}

.rw-route-pct-label {
    font-size: 12px;
    color: #6B7488;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}

.rw-metric-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
}

.rw-metric-card {
    background: rgba(19, 28, 46, 0.55);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 18px 22px;
}

.rw-metric-label {
    font-size: 12px;
    color: #6B7488;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}

.rw-metric-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 30px;
    font-weight: 700;
    color: #F2A93B;
}

.rw-panel {
    background: rgba(19, 28, 46, 0.55);
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 24px 26px;
    margin-top: 8px;
}

div[data-baseweb="select"] > div {
    background-color: rgba(19,28,46,0.7) !important;
    border-color: rgba(255,255,255,0.08) !important;
    border-radius: 10px !important;
}

.rw-footer {
    font-size: 12px;
    color: #4E5568;
    margin-top: 48px;
    padding-top: 18px;
    border-top: 1px solid rgba(255,255,255,0.06);
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="rw-hero"><span class="rw-title">&#9992; ROUTEWATCH</span>'
    '<span class="rw-live-tag"><span class="rw-live-dot"></span>LIVE DATA</span></div>'
    '<div class="rw-sub">Delay tracking across 3 self-collected India&ndash;Europe routes, updated daily.</div>',
    unsafe_allow_html=True,
)


@st.cache_data
def load_data():
    df = pd.read_csv('data/flights_log.csv')
    df['dep_scheduled'] = pd.to_datetime(df['dep_scheduled'])
    df['dep_actual'] = pd.to_datetime(df['dep_actual'])
    df['arr_scheduled'] = pd.to_datetime(df['arr_scheduled'])
    df['arr_actual'] = pd.to_datetime(df['arr_actual'])

    complete = df[df['arr_actual'].notna()].copy()
    complete['actual_arr_delay_min'] = (
        complete['arr_actual'] - complete['arr_scheduled']
    ).dt.total_seconds() / 60
    complete['dep_hour'] = complete['dep_scheduled'].dt.hour
    return complete


data = load_data()
routes = sorted(data['route'].unique())

st.markdown('<div class="rw-section-label">Delay threshold</div>', unsafe_allow_html=True)
threshold = st.slider(
    'Minutes late counts as delayed',
    min_value=5, max_value=60, value=15, step=5,
    label_visibility='collapsed',
)
st.markdown(
    f'<div style="font-size:13px; color:#6B7488; margin-bottom:8px;">'
    f'Showing flights arriving <span style="color:#F2A93B; font-family:JetBrains Mono;">{threshold}+ minutes</span> late as delayed. '
    f'Industry-standard reporting uses 15 minutes.</div>',
    unsafe_allow_html=True,
)

data['is_delayed'] = data['actual_arr_delay_min'] >= threshold

st.markdown('<div class="rw-section-label">All routes</div>', unsafe_allow_html=True)

overview = data.groupby('route')['is_delayed'].agg(['mean', 'count']).reindex(routes)
cards_html = '<div class="rw-grid">'
for route, row in overview.iterrows():
    pct = row['mean'] * 100
    risk_class = "rw-high-delay" if pct >= 10 else "rw-low-delay"
    color = "#E85D4A" if pct >= 10 else "#3ECF8E"
    cards_html += (
        f'<div class="rw-route-card {risk_class}">'
        f'<div class="rw-route-code">{route}</div>'
        f'<div class="rw-route-meta">{int(row["count"])} flights tracked</div>'
        f'<div class="rw-route-pct" style="color:{color};">{pct:.0f}%</div>'
        f'<div class="rw-route-pct-label">delayed</div>'
        f'</div>'
    )
cards_html += '</div>'
st.markdown(cards_html, unsafe_allow_html=True)

st.markdown('<div class="rw-section-label">Route detail</div>', unsafe_allow_html=True)
selected_route = st.selectbox("Choose a route", routes, label_visibility="collapsed")

route_data = data[data['route'] == selected_route]
delay_rate = route_data['is_delayed'].mean() * 100
total_flights = len(route_data)
delayed_count = int(route_data['is_delayed'].sum())

st.markdown(
    '<div class="rw-metric-row">'
    f'<div class="rw-metric-card"><div class="rw-metric-label">Flights tracked</div><div class="rw-metric-value">{total_flights}</div></div>'
    f'<div class="rw-metric-card"><div class="rw-metric-label">Delay rate</div><div class="rw-metric-value">{delay_rate:.0f}%</div></div>'
    f'<div class="rw-metric-card"><div class="rw-metric-label">Delayed flights</div><div class="rw-metric-value">{delayed_count}</div></div>'
    '</div>',
    unsafe_allow_html=True,
)

hour_stats = route_data.groupby('dep_hour')['is_delayed'].agg(['mean', 'count'])
hour_stats = hour_stats.reindex(sorted(hour_stats.index))
hour_stats['mean'] = hour_stats['mean'] * 100
hour_labels = [f"{h:02d}:00" for h in hour_stats.index]

fig = go.Figure(data=[
    go.Bar(
        x=hour_labels,
        y=hour_stats['mean'].values,
        marker_color=['#E85D4A' if v >= 10 else '#3ECF8E' for v in hour_stats['mean'].values],
        text=[f"{v:.0f}% (n={n})" for v, n in zip(hour_stats['mean'].values, hour_stats['count'].values)],
        textposition='outside',
        textfont=dict(family='JetBrains Mono', color='#EDEBE3', size=12),
        marker_line_width=0,
    )
])
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#8A94A6', size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    height=300,
    xaxis=dict(showgrid=False, tickfont=dict(family='JetBrains Mono')),
    yaxis=dict(gridcolor='rgba(255,255,255,0.06)', ticksuffix='%', zeroline=False),
    showlegend=False,
)

st.markdown('<div class="rw-panel">', unsafe_allow_html=True)
st.markdown(f'<div style="font-size:14px; color:#8A94A6; margin-bottom:4px;">Delay rate by departure hour &mdash; {selected_route}</div>', unsafe_allow_html=True)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="rw-footer">Data collected daily via a live flight API. '
    'Delay defined as 15+ minutes late, the industry-standard threshold. '
    'Full project reasoning in KNOWLEDGE.md.</div>',
    unsafe_allow_html=True,
)
