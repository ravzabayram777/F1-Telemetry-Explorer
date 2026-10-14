\# F1 Telemetry Explorer



A Python-based dashboard for exploring Formula 1 telemetry data, driver inputs, and detected braking events.



\## Project Overview



This project analyzes recorded telemetry from Charles Leclerc's qualifying session at the 2026 Italian Grand Prix. It uses Python to explore vehicle speed, throttle, brake signals, gear changes, and estimated acceleration.



The dashboard was built to practice data analysis, visualization, and interactive application development.



\## Features



\- Interactive speed vs. distance visualization

\- Exploration of throttle, brake, gear, RPM, and estimated acceleration

\- Detection and comparison of braking events

\- Comparison of speed drops and estimated average deceleration

\- Inspection of individual braking events

\- Identification of short braking events for further investigation



\## Technologies



\- Python

\- Pandas

\- Plotly

\- Streamlit



\## Data Source



Telemetry data: \[TracingInsights — 2026 F1 Telemetry Files](https://github.com/TracingInsights/2026)



\- \*\*Session:\*\* Italian Grand Prix — Qualifying

\- \*\*Driver:\*\* Charles Leclerc (LEC)

\- \*\*File:\*\* `1\_tel.json`



\## Methodology



The project processes recorded telemetry and derives braking-event summaries from consecutive samples where the brake signal is active. Estimated average acceleration is calculated from the speed difference and event duration.



\## Limitations



This is an exploratory data analysis project, not a validated vehicle-performance assessment. Sampling intervals, signal definitions, and event boundaries may affect the results. The analysis does not establish braking quality or compare driver performance.



\## Future Improvements



\- Validate telemetry units and sampling behavior

\- Improve braking-event detection

\- Add additional telemetry comparisons and visualizations

\- Expand documentation and analysis tests

