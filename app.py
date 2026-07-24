import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="RouteWatch", page_icon="✈", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-color: #0B1220;
    color: #E8E6DE;
}

section[data-testid="stSidebar"] { display: none; }

.rw-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 4px;
    padding-top: 8px;
}

.rw-title {
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: 30px;
    color: #F2A93B;
    letter-spacing: 1px;
}

.rw-sub {
    font-size: 14px;
    color: #8A94A6;
    margin-bottom: 28px;
}

.rw-card {
    background: #131C2E;
    border: 1px solid #1F2A3E;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 10px;
}

.rw-card-label {
    font-size: 12px;
    color: #8A94A6;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 6px;
}

.rw-card-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 32px;
    font-weight: 700;
    color: #F2A93B;
}

.rw-board {
    background: #131C2E;
    border: 1px solid #1F2A3E;
    border-radius: 10px;
    overflow: hidden;
    margin-top: 8px;
}

.rw-board-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    border-bottom: 1px solid #1F2A3E;
    font-family: 'JetBrains Mono', monospace;
}

.rw-board-row:last-child { border-bottom: none; }

.rw-route-code {
    font-size: 16px;
    font-weight: 700;
    color: #E8E6DE;
    min-width: 110px;
}

.rw-status-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 8px;
}

.rw-dot-good { background: #3ECF8E; box-shadow: 0 0 6px #3ECF8E; }
.rw-dot-bad { background: #E85D4A; box-shadow: 0 0 6px #E85D4A; }

.rw-flights-count {
    font-size: 13px;
    color: #8A94A6;
    font-family: 'Inter', sans-serif;
}

.rw-delay-pct {
    font-size: 18px;
    font-weight: 700;
    min-width: 60px;
    text-align: right;
}

.rw-section-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: #8A94A6;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 32px 0 10px;
}

div[data-baseweb="select"] > div {
    background-color: #131C2E !important;
    border-color: #1F2A3E !important;
}

.rw-footer {
    font-size: 12px;
    color: #5A6478;
    margin-top: 36px;
    padding-top: 16px;
    border-top: 1px solid #1F2A3E;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="rw-header">
    <span class="rw-title">✈ ROUTEWATCH</span>
</div>
<div class="rw-sub">Live delay tracking across 3 self-collected India–Europe routes</div>
""", unsafe_allow_html=True)


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
    complete['is_delayed'] = complete['actual_arr_delay_min'] >= 15
    complete['dep_hour'] = complete['dep_scheduled'].dt.hour
    return complete


data = load_data()
routes = sorted(data['route'].unique())

st.markdown('<div class="rw-section-label">All routes</div>', unsafe_allow_html=True)

overview = data.groupby('route')['is_delayed'].agg(['mean', 'count']).reindex(routes)
board_rows = ""
for route, row in overview.iterrows():
    pct = row['mean'] * 100
    dot_class = "rw-dot-bad" if pct >= 10 else "rw-dot-good"
    color = "#E85D4A" if pct >= 10 else "#3ECF8E"
    board_rows += f"""
    <div class="rw-board-row">
        <div style="display:flex; align-items:center;">
            <span class="rw-status-dot {dot_class}"></span>
            <span class="rw-route-code">{route}</span>
        </div>
        <span class="rw-flights-count">{int(row['count'])} flights</span>
        <span class="rw-delay-pct" style="color:{color};">{pct:.0f}%</span>
    </div>
    """
st.markdown(f'<div class="rw-board">{board_rows}</div>', unsafe_allow_html=True)

st.markdown('<div class="rw-section-label">Route detail</div>', unsafe_allow_html=True)
selected_route = st.selectbox("Choose a route", routes, label_visibility="collapsed")

route_data = data[data['route'] == selected_route]
delay_rate = route_data['is_delayed'].mean() * 100
total_flights = len(route_data)
delayed_count = int(route_data['is_delayed'].sum())

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown(f'<div class="rw-card"><div class="rw-card-label">Flights tracked</div><div class="rw-card-value">{total_flights}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="rw-card"><div class="rw-card-label">Delay rate</div><div class="rw-card-value">{delay_rate:.0f}%</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="rw-card"><div class="rw-card-label">Delayed</div><div class="rw-card-value">{delayed_count}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="rw-section-label">Delay rate by departure hour</div>', unsafe_allow_html=True)

hour_delay = route_data.groupby('dep_hour')['is_delayed'].mean() * 100
hour_delay = hour_delay.reindex(sorted(hour_delay.index))
hour_labels = [f"{h:02d}:00" for h in hour_delay.index]

fig = go.Figure(data=[
    go.Bar(
        x=hour_labels,
        y=hour_delay.values,
        marker_color=['#E85D4A' if v >= 10 else '#3ECF8E' for v in hour_delay.values],
        text=[f"{v:.0f}%" for v in hour_delay.values],
        textposition='outside',
        textfont=dict(family='JetBrains Mono', color='#E8E6DE'),
    )
])
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#8A94A6', size=12),
    margin=dict(l=10, r=10, t=10, b=10),
    height=280,
    xaxis=dict(gridcolor='#1F2A3E', showgrid=False),
    yaxis=dict(gridcolor='#1F2A3E', ticksuffix='%'),
    showlegend=False,
)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

st.markdown("""
<div class="rw-footer">
Data collected daily via a live flight API. Delay defined as 15+ minutes late, the industry-standard threshold.
Full project reasoning in KNOWLEDGE.md.
</div>
""", unsafe_allow_html=True)
