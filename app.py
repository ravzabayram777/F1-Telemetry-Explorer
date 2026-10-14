
import pandas as pd
import json


import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="F1 Telemetry Explorer",
    page_icon="🏎️",
    layout="wide"
)

st.title("🏎️ F1 Telemetry Explorer")
st.caption(
    "Exploring speed, driver inputs and braking events "
    "from recorded Formula 1 telemetry."
)


st.markdown(
    """
    **Data source:** [TracingInsights — 2026 Public F1 Telemetry Files](https://github.com/TracingInsights/2026)

    **Session:** Italian Grand Prix — Qualifying  
    **Driver:** Charles Leclerc (LEC)  
    **File:** `1_tel.json`

    **Method:** Telemetry exploration, braking-event detection,
    speed-drop comparison and estimated average deceleration.

    **Limitations:** Exploratory analysis only. Sampling intervals
    and event boundaries may affect calculated values.
    This is not a validated assessment of vehicle performance.
    """
)


# Load the exported analysis files
@st.cache_data
def load_data():
    telemetry = pd.read_csv("telemetry.csv")
    braking = pd.read_csv("braking_analysis.csv")
    return telemetry, braking

try:
    telemetry, braking = load_data()
except FileNotFoundError:
    st.error(
        "CSV files not found. Put telemetry.csv and "
        "braking_analysis.csv in the same folder as app.py."
    )
    st.stop()

# Sidebar controls
st.sidebar.header("Analysis settings")

max_distance = float(telemetry["distance"].max())
distance_range = st.sidebar.slider(
    "Distance range",
    min_value=0.0,
    max_value=max_distance,
    value=(0.0, max_distance)
)

signal = st.sidebar.selectbox(
    "Driver / vehicle signal",
    ["throttle", "brake", "gear", "rpm", "acceleration"]
)

filtered = telemetry[
    telemetry["distance"].between(
        distance_range[0], distance_range[1]
    )
].copy()

# Summary metrics
c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Maximum speed",
    f"{telemetry['speed'].max():.1f} km/h"
)
c2.metric(
    "Minimum speed",
    f"{telemetry['speed'].min():.1f} km/h"
)
c3.metric(
    "Telemetry samples",
    f"{len(telemetry):,}"
)
c4.metric(
    "Detected braking sections",
    f"{len(braking)}"
)

st.divider()

# Speed trace
st.subheader("1. Speed vs distance")

fig_speed = px.line(
    filtered,
    x="distance",
    y="speed",
    labels={
        "distance": "Distance (source units)",
        "speed": "Speed (km/h)"
    },
    title="Vehicle speed trace"
)

# Mark the detected braking starts
visible_events = braking[
    braking["start_distance"].between(
        distance_range[0], distance_range[1]
    )
]

fig_speed.add_scatter(
    x=visible_events["start_distance"],
    y=visible_events["entry_speed_kmh"],
    mode="markers",
    name="Braking starts",
    marker=dict(symbol="x", size=10)
)



fig_speed.update_layout(
    hovermode="x unified",
    margin=dict(l=10, r=10, t=50, b=10)
)
st.plotly_chart(fig_speed, use_container_width=True)

# Driver / vehicle signal
st.subheader(f"2. {signal.title()} vs distance")

fig_signal = px.line(
    filtered,
    x="distance",
    y=signal,
    labels={
        "distance": "Distance (source units)",
        signal: signal.replace("_", " ").title()
    }
)
fig_signal.update_layout(
    hovermode="x unified",
    margin=dict(l=10, r=10, t=20, b=10)
)
st.plotly_chart(fig_signal, use_container_width=True)

# Braking event analysis
st.subheader("3. Braking event analysis")

sort_by = st.selectbox(
    "Sort events by",
    {
        "Largest speed drop": "speed_drop_kmh",
        "Longest duration": "duration_s",
        "Highest entry speed": "entry_speed_kmh"
    }.keys()
)

sort_column = {
    "Largest speed drop": "speed_drop_kmh",
    "Longest duration": "duration_s",
    "Highest entry speed": "entry_speed_kmh"
}[sort_by]

sorted_events = braking.sort_values(
    sort_column, ascending=False
).reset_index(drop=True)

display_columns = [
    "start_time_s",
    "end_time_s",
    "entry_speed_kmh",
    "exit_speed_kmh",
    "speed_drop_kmh",
    "duration_s",
    "distance_span",
    "entry_gear",
    "exit_gear"
]

st.dataframe(
    sorted_events[display_columns].round(2),
    use_container_width=True,
    hide_index=True
)


# Compare speed drops across braking events

fig_braking = px.bar(
    sorted_events,
    x="start_time_s",
    y="speed_drop_kmh",
    hover_data=[
        "entry_speed_kmh",
        "exit_speed_kmh",
        "duration_s"
    ],
    labels={
        "start_time_s": "Braking start time (s)",
        "speed_drop_kmh": "Speed drop (km/h)",
        "entry_speed_kmh": "Entry speed (km/h)",
        "exit_speed_kmh": "Exit speed (km/h)",
        "duration_s": "Duration (s)"
    },
    title="Speed drop by braking event"
)

st.plotly_chart(fig_braking, use_container_width=True)


# Compare average deceleration across braking events
braking_plot = sorted_events.copy()

braking_plot["avg_deceleration_m_s2"] = (
    braking_plot["speed_drop_kmh"] / 3.6
) / braking_plot["duration_s"]

fig_deceleration = px.bar(
    braking_plot,
    x="start_time_s",
    y="avg_deceleration_m_s2",
    labels={
        "start_time_s": "Braking start time (s)",
        "avg_deceleration_m_s2": "Average deceleration magnitude (m/s²)"
    },
    title="Average deceleration by braking event",
    hover_data=[
        "speed_drop_kmh",
        "duration_s",
        "entry_speed_kmh",
        "exit_speed_kmh"
    ]
)

st.plotly_chart(fig_deceleration, use_container_width=True)


# Show short braking events for further inspection
short_events = braking[braking["duration_s"] < 0.5]

st.write("Braking events shorter than 0.5 seconds")
st.dataframe(short_events, hide_index=True)




# Select a braking event for closer inspection
st.subheader("4. Inspect an individual event")

event_labels = [
    f"Event {i + 1} — {row['start_time_s']:.2f} s, "
    f"{row['entry_speed_kmh']:.0f} km/h entry speed"
    for i, (_, row) in enumerate(braking.iterrows())
]

selected_label = st.selectbox(
    "Choose an event",
    event_labels
)

selected_index = event_labels.index(selected_label)
event = braking.iloc[selected_index]





# Get telemetry samples within the selected braking event
event_data = telemetry[
    telemetry["distance"].between(
        event["start_distance"],
        event["end_distance"]
    )
]


# Plot the selected braking event
fig_event = px.line(
    telemetry,
    x="distance",
    y="speed",
    labels={
        "distance": "Distance (source units)",
        "speed": "Speed (km/h)"
    },
    title="Selected braking event"
)

# Highlight the selected distance interval
fig_event.add_vrect(
    x0=event["start_distance"],
    x1=event["end_distance"],
    fillcolor="orange",
    opacity=0.25,
    line_width=0
)

# Highlight the speed trace within the selected event
fig_event.add_scatter(
    x=event_data["distance"],
    y=event_data["speed"],
    mode="lines",
    name="Selected event",
    line=dict(width=4)
)

st.plotly_chart(fig_event, use_container_width=True)






m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "Entry speed",
    f"{event['entry_speed_kmh']:.1f} km/h"
)
m2.metric(
    "Exit speed",
    f"{event['exit_speed_kmh']:.1f} km/h"
)
m3.metric(
    "Speed drop",
    f"{event['speed_drop_kmh']:.1f} km/h"
)
m4.metric(
    "Duration",
    f"{event['duration_s']:.2f} s"
)


# Calculate average deceleration
entry_speed_ms = event["entry_speed_kmh"] / 3.6
exit_speed_ms = event["exit_speed_kmh"] / 3.6

average_acceleration = (
    exit_speed_ms - entry_speed_ms
) / event["duration_s"]

st.metric(
    "Average acceleration (estimated)",
    f"{average_acceleration:.2f} m/s²"
)

st.caption(
    "Estimated from entry and exit speeds over the detected "
    "braking event duration; not a direct vehicle measurement."
)


st.write(
    f"**Gear change:** {int(event['entry_gear'])} → "
    f"{int(event['exit_gear'])}"
)
st.write(
    f"**Distance interval:** "
    f"{event['start_distance']:.2f} – "
    f"{event['end_distance']:.2f}"
)

st.info(
    "These events are defined by consecutive samples with "
    "the brake signal active. Speed drop and duration alone "
    "do not establish braking quality or performance."
)

st.caption(
    "Exploratory analysis of recorded telemetry. "
    "Signal units and event definitions should be validated "
    "before drawing engineering conclusions."
)
with open("1_tel.json", "r", encoding="utf-8") as file:
    raw_data = json.load(file)

st.write("JSON data type:", type(raw_data).__name__)
st.write("JSON data preview:", str(raw_data)[:500])

st.write("Available data groups:", list(raw_data.keys()))
st.write("Telemetry columns:", list(raw_data["tel"].keys()))

# Build a track map from position coordinates
track = pd.DataFrame({
    "time": raw_data["tel"]["time"],
    "x": raw_data["tel"]["x"],
    "y": raw_data["tel"]["y"],
    "speed": raw_data["tel"]["speed"]
})
fig_track = px.scatter(
    track,
    x="x",
    y="y",
    color="speed",
    color_continuous_scale="Turbo",
    title="Track Map — Speed Profile",
    labels={
        "x": "X position",
        "y": "Y position",
        "speed": "Speed (km/h)"
    }
)
fig_track.add_scatter(
    x=track["x"],
    y=track["y"],
    mode="lines",
    line=dict(color="gray", width=2),
    showlegend=False
)

fig_track.update_yaxes(scaleanchor="x", scaleratio=1)
fig_track.add_scatter(
    x=[track["x"].iloc[0]],
    y=[track["y"].iloc[0]],
    mode="markers",
    name="Start",
    marker=dict(size=12, color="green")
)

fig_track.add_scatter(
    x=[track["x"].iloc[-1]],
    y=[track["y"].iloc[-1]],
    mode="markers",
    name="End",
    marker=dict(size=12, color="red")
)

fig_track.update_yaxes(scaleanchor="x", scaleratio=1)

st.plotly_chart(fig_track, use_container_width=True)
st.write("First point:", track.iloc[0].to_dict())
st.write("Last point:", track.iloc[-1].to_dict())
st.write("Number of points:", len(track))

st.write("First 5 coordinates:")
st.dataframe(track.head())

st.write("Last 5 coordinates:")
st.dataframe(track.tail())

st.write("First recorded time:", track["time"].iloc[0])
st.write("Last recorded time:", track["time"].iloc[-1])
st.write("Total recorded duration (s):", track["time"].iloc[-1] - track["time"].iloc[0])