# BVG Open Data Project

### **1. Purpose**
The purpose of this data pipeline is to collect and analyze data for Berlin tram line **M13** to:
- Track its **schedule and performance** between the stations **Schönhauser Allee/Bornholmer Straße** and **Antonplatz**.
- Identify **peak hours** by analyzing high occupancy times.
- Measure **punctuality** by comparing scheduled versus actual arrival and departure times.
- Monitor for **disturbances** on the tram line and analyze how frequently they occur.

This data pipeline aims to provide insights into the operational efficiency and usability of tram M13, improving the daily commute experience.

---

### **2. Scope**
This document covers:
- The pipeline flow, from data ingestion to storage and processing.
- High-level architectural design.
- Key components involved, including APIs, processing logic, and storage mechanisms.
- Limitations, such as the focus on one tram line (M13) and a limited set of endpoints.

#### Limitations:
- The pipeline will only track two specific stations: Schönhauser Allee/Bornholmer Straße and Antonplatz.
- Real-time occupancy data may not be directly available, requiring indirect inference based on departures, arrivals, and disturbances.
- Initial implementation will focus on **collecting and storing data**; further phases can expand to include dashboards and detailed analytics.

---

### **3. High-Level Architecture**
The pipeline will follow these steps:

1. **Data Ingestion**:
   - Use the **`GET /locations`** API to identify the station IDs for Schönhauser Allee/Bornholmer Straße and Antonplatz.
   - Use **`GET /stops/:id/departures`** and **`GET /stops/:id/arrivals`** to fetch tram schedules and real-time data, including trip IDs for tram M13.

2. **Data Enrichment**:
   - Use the **`GET /trips/:id`** API to gather details about each trip, such as route information, delays, and disturbances.

3. **Data Processing**:
   - **Punctuality Analysis**: Compare scheduled vs. actual arrival/departure times.
   - **Peak Hour Analysis**: Aggregate departure/arrival counts by time to determine high-traffic periods.
   - **Disturbance Detection**: Track alerts or delays associated with the M13 line.

4. **Data Storage**:
   - Store raw and processed data in a **relational database** (e.g., SQLite or PostgreSQL) for structured querying.
   - Optionally, store logs or intermediate data in a lightweight **JSON file** for easy debugging.

5. **Analytics and Reporting**:
   - Generate periodic summaries (e.g., daily/weekly reports) highlighting punctuality, peak hours, and disturbances.
   - Integrate with a visualization tool in future phases (e.g., Tableau, Power BI, or a custom Streamlit app).

---

### **4. Key Components**

#### **Data Sources**
- **API**: [`v6.bvg.transport.rest`](https://v6.bvg.transport.rest/) for public transport data.
  - Endpoints:
    - `/locations`: Identify station IDs for Schönhauser Allee/Bornholmer Straße and Antonplatz.
    - `/stops/:id/departures`: Fetch tram departure times.
    - `/stops/:id/arrivals`: Fetch tram arrival times.
    - `/trips/:id`: Gather details about specific trips.

#### **Processing Framework**
- **Language**: Python for scripting the API calls, processing, and data manipulation.
- **Libraries**:
  - `requests` or `httpx` for API interaction.
  - `pandas` for data processing and analysis.
  - `datetime` for time-based calculations.

#### **Data Storage**
- **Relational Database**:
  - Schema:
    - `stations`: Stores station details (e.g., ID, name, location).
    - `trips`: Stores trip details (e.g., trip ID, start and end times, delays).
    - `occupancy`: Tracks inferred occupancy trends for peak hour analysis.
    - `disturbances`: Tracks alerts or issues with the tram line.

#### **Output**
- **Reports**:
  - **CSV** or **JSON** files summarizing punctuality, peak hours, and disturbances.
- **Future Expansion**:
  - **Visualization**: Create a real-time dashboard or integrate with BI tools for live insights.

---

### **5. Workflow Summary**

1. **Station Initialization**:
   - Query `/locations` once to fetch station IDs for Schönhauser Allee/Bornholmer Straße and Antonplatz.
   - Store these IDs locally for reuse.

2. **Scheduled Data Collection**:
   - Use a scheduler (e.g., **cron jobs** or **Airflow**) to periodically call `/stops/:id/departures` and `/stops/:id/arrivals`.
   - Extract relevant tram data (M13) and store in a raw data table.

3. **Real-Time Enrichment**:
   - Fetch additional details using `/trips/:id` for the tram trips collected in the previous step.

4. **Data Processing**:
   - Perform calculations:
     - Punctuality: Compare actual vs. planned times.
     - Peak Hours: Count departures/arrivals per hour.
     - Disturbances: Identify delays or alerts.

5. **Output and Reporting**:
   - Save aggregated results in structured formats (e.g., daily summaries).

