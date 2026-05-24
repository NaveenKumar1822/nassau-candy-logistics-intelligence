import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Nassau Candy Logistics Intelligence",
    page_icon="🍭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. HIGH-PERFORMANCE DATA INGESTION (CACHED) ---
@st.cache_data
def load_dashboard_data():
    # Reading our optimized data structures directly from the Gold Layer
    heatmap_df = pd.read_parquet('../01_data/05_dashboard/dash_state_heatmap.parquet')
    leaderboard_df = pd.read_parquet('../01_data/05_dashboard/dash_route_leaderboard.parquet')
    ship_mode_df = pd.read_parquet('../01_data/05_dashboard/dash_ship_mode.parquet')
    return heatmap_df, leaderboard_df, ship_mode_df

raw_heatmap, raw_leaderboard, raw_ship_mode = load_dashboard_data()

# --- STATE NAME TO STATE CODE CONVERSION ---
us_state_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}

raw_heatmap['state_province'] = raw_heatmap['state_province'].map(us_state_abbrev)

# --- 3. CONTROL CENTER (SIDEBAR) ---
st.sidebar.markdown("## ⚙️ Control Center")
st.sidebar.markdown("Filter lanes across specific operational nodes:")

selected_factories = st.sidebar.multiselect(
    "Manufacturing Origin (Factories)",
    options=sorted(raw_leaderboard['factory'].unique()),
    help="Select specific manufacturing centers to isolate downstream routes."
)

# --- 4. REACTIVE STREAMLIT FILTER RUNTIME ---
filtered_leaderboard = raw_leaderboard.copy()
filtered_ship_mode = raw_ship_mode.copy()

if selected_factories:
    filtered_leaderboard = filtered_leaderboard[filtered_leaderboard['factory'].isin(selected_factories)]
    filtered_ship_mode = filtered_ship_mode[filtered_ship_mode['factory'].isin(selected_factories)]

# --- 5. APPLICATION TITLE & TEXT LAYOUT ---
st.title("🍭 Factory-to-Customer Shipping Route Efficiency Dashboard")
st.markdown("#### Operational Intelligence Platform for Nassau Candy Distributors")
st.markdown("---")

# --- 6. TOP ROW: HIGH-DENSITY KPI CARDS ---
# Creating columns to arrange summary cards side-by-side elegantly
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

# Dynamic metrics that recalculate instantly when sidebar filters adjust
avg_lead_time = filtered_leaderboard['avg_lead_time'].mean()
global_res = filtered_leaderboard['route_efficiency_score'].mean()
total_sales_volume = filtered_leaderboard['total_sales'].sum()
active_lanes_count = len(filtered_leaderboard)

# Rendering the metric widgets
kpi1.metric(label="⏱️ Avg Shipping Lead Time", value=f"{avg_lead_time:.2f} Days")
kpi2.metric(label="🎯 Network Efficiency (RES)", value=f"{global_res:.1f}%")
kpi3.metric(label="💰 Total Sales Fulfilled", value=f"${total_sales_volume:,.2f}")
kpi4.metric(label="🛣️ Monitored Route Lanes", value=f"{active_lanes_count} Lanes")

st.markdown("---")

# --- 7. MIDDLE ROW: PLOTLY GEOGRAPHIC HEATMAP ---
st.subheader("🗺️ Geographic Bottleneck Map (Average Lead Time by Destination State)")

# Constructing an interactive USA Choropleth Map with Plotly Express
# Plotly expects standard 2-letter state codes for 'locations="state_province"' (e.g., 'NY', 'CA')
fig_map = px.choropleth(
    raw_heatmap, 
    locations="state_province",       # The geographic column index
    locationmode="USA-states",        # Maps values directly to a built-in US map geometry
    color="avg_lead_time",            # The column driving the color gradient severity
    scope="usa",                      # Zooms the map view specifically into the United States
    color_continuous_scale="Reds",    # Red scale highlights delayed states instantly
    labels={"avg_lead_time": "Avg Lead Time (Days)", "state_province": "State"},
    hover_data={"total_sales": ":$,.2f", "delay_rate": ":.1f%"} # Clean up formatting inside hover boxes
)

# Adjust plot borders and backgrounds to remain professional and clean
fig_map.update_layout(
    geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='rgb(255, 255, 255)'),
    margin=dict(l=0, r=0, t=0, b=0)
)

# Render the Plotly chart directly on the Streamlit page layout
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# --- 8. BOTTOM ROW: DUAL-COLUMN LAYOUT ---
# We split the bottom into two columns (one for the table, one for the bar chart)
col1, col2 = st.columns((1.5, 1)) # The first column is slightly wider

with col1:
    st.subheader("📊 Route Efficiency Leaderboard")
    st.markdown("Top performing vs. bottleneck shipping lanes.")
    
    # We sort the filtered dataframe by lowest efficiency to highlight bottlenecks first
    display_leaderboard = filtered_leaderboard.sort_values(by='route_efficiency_score', ascending=True)
    
    # Render an interactive Streamlit dataframe
    st.dataframe(
        display_leaderboard[['route_state', 'total_shipments', 'avg_lead_time', 'route_efficiency_score']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "route_state": "Shipping Route",
            "total_shipments": "Total Orders",
            "avg_lead_time": st.column_config.NumberColumn("Avg Lead Time (Days)", format="%.2f"),
            "route_efficiency_score": st.column_config.ProgressColumn(
                "Efficiency (RES)",
                help="Percentage of on-time deliveries.",
                format="%.1f%%",
                min_value=0,
                max_value=100,
            )
        }
    )

with col2:
    st.subheader("🚚 Carrier Tier Performance")
    st.markdown("Average lead times across shipping modes.")
    
    # Group the filtered ship mode data for a clean bar chart
    mode_summary = filtered_ship_mode.groupby('ship_mode').agg(
        avg_lead_time=('avg_lead_time', 'mean'),
        delay_rate=('delay_rate', 'mean')
    ).reset_index()
    
    # Create an interactive Plotly Bar Chart
    fig_bar = px.bar(
        mode_summary,
        x='ship_mode',
        y='avg_lead_time',
        color='delay_rate',
        color_continuous_scale="Blues",
        labels={
            "ship_mode": "Shipping Mode",
            "avg_lead_time": "Lead Time (Days)",
            "delay_rate": "Delay Rate (%)"
        },
        text_auto='.2f' # Automatically display the numbers on top of the bars
    )
    
    fig_bar.update_layout(
        xaxis_title="",
        yaxis_title="Average Days",
        margin=dict(l=0, r=0, t=30, b=0),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    # Render the bar chart inside the column
    st.plotly_chart(fig_bar, use_container_width=True)