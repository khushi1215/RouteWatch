import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.linear_model import LogisticRegression

st.set_page_config(page_title="RouteWatch", page_icon="✈", layout="wide")

THEMES = {
    "dark": {
        "bg": "radial-gradient(circle at 15% 0%, #10192E 0%, #070B14 55%, #05070D 100%)",
        "text": "#EDEBE3",
        "text_secondary": "#8A94A6",
        "text_muted": "#6B7488",
        "footer_text": "#4E5568",
        "card_bg": "rgba(19, 28, 46, 0.55)",
        "card_border": "rgba(255,255,255,0.06)",
        "legend_bg": "rgba(19, 28, 46, 0.4)",
        "legend_border": "rgba(255,255,255,0.05)",
        "select_bg": "rgba(19,28,46,0.7)",
        "select_border": "rgba(255,255,255,0.08)",
        "footer_border": "rgba(255,255,255,0.06)",
        "accent": "#F2A93B",
        "good": "#3ECF8E",
        "bad": "#E85D4A",
        "chart_text": "#EDEBE3",
        "chart_axis": "#8A94A6",
        "chart_grid": "rgba(255,255,255,0.06)",
        "hover_bg": "#131C2E",
    },
    "light": {
        "bg": "radial-gradient(circle at 15% 0%, #FDF6E9 0%, #F4EFE4 55%, #EFEAE0 100%)",
        "text": "#231F14",
        "text_secondary": "#665F4F",
        "text_muted": "#8A8270",
        "footer_text": "#9B937F",
        "card_bg": "rgba(255, 255, 255, 0.65)",
        "card_border": "rgba(35,31,20,0.08)",
        "legend_bg": "rgba(255, 255, 255, 0.5)",
        "legend_border": "rgba(35,31,20,0.06)",
        "select_bg": "rgba(255,255,255,0.85)",
        "select_border": "rgba(35,31,20,0.12)",
        "footer_border": "rgba(35,31,20,0.08)",
        "accent": "#B5750F",
        "good": "#1E9E68",
        "bad": "#C7402F",
        "chart_text": "#231F14",
        "chart_axis": "#665F4F",
        "chart_grid": "rgba(35,31,20,0.08)",
        "hover_bg": "#FFFFFF",
    },
}

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

col_a, col_b = st.columns([6, 1])
with col_b:
    is_dark = st.toggle(
        "Theme toggle",
        value=(st.session_state.theme == "dark"),
        label_visibility="collapsed",
    )
    st.session_state.theme = "dark" if is_dark else "light"
    mode_text = "Dark mode" if is_dark else "Light mode"
    st.caption(mode_text)

T = THEMES[st.session_state.theme]

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

.stApp {{
    background: {T['bg']};
    color: {T['text']};
}}

.block-container {{
    max-width: 1180px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}}

section[data-testid="stSidebar"] {{ display: none; }}
#MainMenu, header, footer {{ visibility: hidden; }}

.rw-hero {{
    display: flex;
    align-items: center;
    justify-content: flex-start;
    flex-wrap: wrap;
    gap: 14px;
    margin-bottom: 6px;
}}

.rw-title {{
    font-family: 'JetBrains Mono', monospace;
    font-weight: 700;
    font-size: clamp(24px, 4vw, 42px);
    color: {T['accent']};
    letter-spacing: 0.5px;
}}

.rw-live-tag {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: {T['good']};
    border: 1px solid {T['good']}55;
    background: {T['good']}14;
    padding: 5px 12px;
    border-radius: 999px;
    letter-spacing: 1px;
    white-space: nowrap;
}}

.rw-live-dot {{
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: {T['good']};
    margin-right: 6px;
    box-shadow: 0 0 6px {T['good']};
}}

.rw-sub {{
    font-size: 15px;
    color: {T['text_secondary']};
    margin-bottom: 28px;
}}

.rw-section-label {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    color: {T['text_muted']};
    text-transform: uppercase;
    letter-spacing: 2px;
    margin: 32px 0 14px;
}}

.rw-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 14px;
}}

.rw-route-card {{
    background: {T['card_bg']};
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid {T['card_border']};
    border-radius: 16px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
}}

.rw-route-card::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}}

.rw-route-card.rw-high-delay::before {{ background: linear-gradient(90deg, {T['bad']}, transparent); }}
.rw-route-card.rw-low-delay::before {{ background: linear-gradient(90deg, {T['good']}, transparent); }}

.rw-route-code {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 19px;
    font-weight: 700;
    color: {T['text']};
    margin-bottom: 4px;
}}

.rw-route-meta {{
    font-size: 13px;
    color: {T['text_muted']};
    margin-bottom: 16px;
}}

.rw-route-pct {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 38px;
    font-weight: 700;
    line-height: 1;
}}

.rw-route-pct-label {{
    font-size: 12px;
    color: {T['text_muted']};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 4px;
}}

.rw-metric-row {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
}}

.rw-metric-card {{
    background: {T['card_bg']};
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid {T['card_border']};
    border-radius: 14px;
    padding: 16px 20px;
}}

.rw-metric-label {{
    font-size: 12px;
    color: {T['text_muted']};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}}

.rw-metric-value {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 28px;
    font-weight: 700;
    color: {T['accent']};
}}

.rw-panel {{
    background: {T['card_bg']};
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
    border: 1px solid {T['card_border']};
    border-radius: 16px;
    padding: 20px 22px;
    margin-top: 8px;
}}

div[data-baseweb="select"] > div {{
    background-color: {T['select_bg']} !important;
    border-color: {T['select_border']} !important;
    border-radius: 10px !important;
}}

.rw-legend {{
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
    background: {T['legend_bg']};
    border: 1px solid {T['legend_border']};
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    font-size: 12.5px;
    color: {T['text_secondary']};
}}

.rw-legend-item {{
    display: flex;
    align-items: center;
    gap: 7px;
}}

.rw-legend-dot {{
    width: 8px; height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}}

.rw-footer {{
    font-size: 12px;
    color: {T['footer_text']};
    margin-top: 40px;
    padding-top: 16px;
    border-top: 1px solid {T['footer_border']};
    text-align: center;
}}

.rw-predict-result {{
    text-align: center;
    padding: 22px 16px;
}}

.rw-predict-pct {{
    font-family: 'JetBrains Mono', monospace;
    font-size: 52px;
    font-weight: 700;
    line-height: 1;
}}

.rw-predict-label {{
    font-size: 13px;
    color: {T['text_muted']};
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 8px;
}}

.rw-disclaimer {{
    background: {T['legend_bg']};
    border: 1px solid {T['legend_border']};
    border-left: 3px solid {T['accent']};
    border-radius: 8px;
    padding: 12px 16px;
    font-size: 12.5px;
    color: {T['text_secondary']};
    margin-top: 14px;
}}

div[data-testid="stToggle"] {{
    background: {T['card_bg']};
    border: 1px solid {T['card_border']};
    border-radius: 999px;
    padding: 8px 14px;
    backdrop-filter: blur(14px);
    -webkit-backdrop-filter: blur(14px);
}}

div[data-testid="stToggle"] label p {{
    color: {T['text']} !important;
    font-size: 13px !important;
}}

label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{
    color: {T['text']} !important;
}}

.stSlider [data-testid="stTickBarMin"], .stSlider [data-testid="stTickBarMax"] {{
    color: {T['text_muted']} !important;
}}

.stSlider [data-testid="stThumbValue"] {{
    color: {T['accent']} !important;
    background: transparent !important;
}}

div[data-baseweb="select"] * {{
    color: {T['text']} !important;
}}

.stButton button {{
    background: {T['card_bg']} !important;
    color: {T['text']} !important;
    border: 1px solid {T['card_border']} !important;
}}

.stButton button p {{
    color: {T['text']} !important;
}}

[data-testid="stMarkdownContainer"] p {{
    color: inherit;
}}

.js-plotly-plot .plotly text {{
    fill: {T['chart_axis']} !important;
}}

@media (max-width: 640px) {{
    .block-container {{ padding-left: 1rem; padding-right: 1rem; padding-top: 1rem; }}
    .rw-route-card, .rw-metric-card, .rw-panel {{ padding: 14px 16px; }}
    .rw-route-pct {{ font-size: 30px; }}
    .rw-metric-value {{ font-size: 22px; }}
    .rw-section-label {{ margin: 24px 0 10px; }}
    .rw-legend {{ font-size: 11.5px; gap: 10px; padding: 10px 12px; }}
    .rw-sub {{ font-size: 13.5px; margin-bottom: 20px; }}
}}
</style>
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
    complete['dep_hour'] = complete['dep_scheduled'].dt.hour
    complete['day_of_week'] = complete['dep_scheduled'].dt.day_name()
    return complete


data = load_data()
routes = sorted(data['route'].unique())

with col_a:
    st.markdown(
        '<div class="rw-hero"><span class="rw-title">&#9992; ROUTEWATCH</span>'
        '<span class="rw-live-tag"><span class="rw-live-dot"></span>LIVE DATA</span></div>'
        f'<div class="rw-sub">Delay tracking across {len(routes)} self-collected India&ndash;Europe routes, updated daily.</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="rw-legend">'
    f'<div class="rw-legend-item"><span class="rw-legend-dot" style="background:{T["good"]}; box-shadow:0 0 6px {T["good"]};"></span>Below the delay threshold, more reliable</div>'
    f'<div class="rw-legend-item"><span class="rw-legend-dot" style="background:{T["bad"]}; box-shadow:0 0 6px {T["bad"]};"></span>At or above 10% delayed, less reliable</div>'
    f'<div class="rw-legend-item"><span style="font-family:JetBrains Mono; color:{T["accent"]};">n:</span>number of flights that data point is based on</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="rw-section-label">Delay threshold</div>', unsafe_allow_html=True)
threshold = st.slider(
    'Minutes late counts as delayed',
    min_value=5, max_value=60, value=15, step=5,
    label_visibility='collapsed',
)
st.markdown(
    f'<div style="font-size:13px; color:{T["text_muted"]}; margin-bottom:8px;">'
    f'Showing flights arriving <span style="color:{T["accent"]}; font-family:JetBrains Mono;">{threshold}+ minutes</span> late as delayed. '
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
    color = T['bad'] if pct >= 10 else T['good']
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
        marker_color=[T['bad'] if v >= 10 else T['good'] for v in hour_stats['mean'].values],
        text=[f"{v:.0f}% (n={n})" for v, n in zip(hour_stats['mean'].values, hour_stats['count'].values)],
        textposition='outside',
        textfont=dict(family='JetBrains Mono', color=T['chart_text'], size=12),
        marker_line_width=0,
        hovertemplate='%{x}: %{y:.0f}%<extra></extra>',
    )
])
fig.update_layout(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color=T['chart_axis'], size=12),
    margin=dict(l=10, r=10, t=30, b=10),
    height=300,
    xaxis=dict(
        showgrid=False,
        tickfont=dict(family='JetBrains Mono', color=T['chart_axis'], size=12),
    ),
    yaxis=dict(
        gridcolor=T['chart_grid'],
        ticksuffix='%',
        zeroline=False,
        tickfont=dict(color=T['chart_axis'], size=12),
    ),
    showlegend=False,
    hoverlabel=dict(
        bgcolor=T['hover_bg'],
        font=dict(color=T['chart_text'], family='Inter', size=12),
        bordercolor=T['card_border'],
    ),
)

st.markdown('<div class="rw-panel">', unsafe_allow_html=True)
st.markdown(f'<div style="font-size:14px; color:{T["text_secondary"]}; margin-bottom:4px;">Delay rate by departure hour: {selected_route}</div>', unsafe_allow_html=True)
st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
st.markdown('</div>', unsafe_allow_html=True)


@st.cache_resource
def train_model(_data, threshold):
    d = _data.copy()
    airline_counts = d['airline'].value_counts()
    rare_airlines = airline_counts[airline_counts < 10].index
    d['airline_grouped'] = d['airline'].apply(lambda x: 'Other' if x in rare_airlines else x)
    d['is_weekend'] = d['dep_scheduled'].dt.dayofweek >= 5

    feature_cols = ['route', 'airline_grouped', 'dep_hour', 'day_of_week', 'is_weekend']
    X = pd.get_dummies(d[feature_cols], columns=['route', 'airline_grouped', 'day_of_week'])
    y = d['is_delayed']

    model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
    model.fit(X, y)
    return model, X.columns, rare_airlines


model, model_columns, rare_airlines = train_model(data, threshold)

st.markdown('<div class="rw-section-label">Predict my flight</div>', unsafe_allow_html=True)

pred_col1, pred_col2, pred_col3 = st.columns(3)
with pred_col1:
    pred_route = st.selectbox("Route", routes, key="pred_route")
with pred_col2:
    airlines_on_route = sorted(data[data['route'] == pred_route]['airline'].unique())
    pred_airline = st.selectbox("Airline", airlines_on_route, key="pred_airline")
with pred_col3:
    pred_day = st.selectbox("Day of week",
        ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="pred_day")

pred_hour = st.slider("Departure hour", 0, 23, 8, key="pred_hour")

if st.button("Predict delay risk", width='stretch'):
    airline_input = "Other" if pred_airline in rare_airlines else pred_airline
    is_weekend_input = pred_day in ["Saturday", "Sunday"]

    input_row = pd.DataFrame([{
        'route': pred_route,
        'airline_grouped': airline_input,
        'dep_hour': pred_hour,
        'day_of_week': pred_day,
        'is_weekend': is_weekend_input,
    }])
    input_encoded = pd.get_dummies(input_row, columns=['route', 'airline_grouped', 'day_of_week'])
    input_encoded = input_encoded.reindex(columns=model_columns, fill_value=0)

    probability = model.predict_proba(input_encoded)[0][1] * 100
    result_color = T['bad'] if probability >= 30 else (T['accent'] if probability >= 15 else T['good'])

    st.markdown(
        f'<div class="rw-panel rw-predict-result">'
        f'<div class="rw-predict-pct" style="color:{result_color};">{probability:.0f}%</div>'
        f'<div class="rw-predict-label">estimated chance of arriving 15+ minutes late</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="rw-disclaimer">'
    '<b>This is a directional estimate, not a guarantee.</b> The model is trained on a small, '
    f'self-collected dataset ({len(data)} flights total) using only 4 factors: route, airline, day, and hour. '
    'It does not account for weather, air traffic conditions, aircraft rotation delays, or other real-world '
    'factors that actually affect whether a specific flight runs on time. Treat this as a historical pattern, '
    'not a forecast. Full model evaluation and its limitations are documented in KNOWLEDGE.md.'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="rw-footer">Data collected daily via a live flight API. '
    'Delay defined as 15+ minutes late, the industry-standard threshold. '
    'Full project reasoning in KNOWLEDGE.md.<br><br>'
    'Built by Khushi Shukla &middot; '
    '<a href="https://www.linkedin.com/in/kshukla1215/" target="_blank" style="color:inherit; text-decoration:underline;">LinkedIn</a>'
    '</div>',
    unsafe_allow_html=True,
)
