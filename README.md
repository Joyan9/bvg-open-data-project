# BVG M13 Tram Data Engineering Project

## **Introduction**
This project is my first attempt at learning and applying the concepts of data engineering to solve a real-world problem. Since I commute daily using the M13 tram in Berlin, I wanted to analyze its operational efficiency and make data-backed decisions regarding my travel. I discovered an amazing BVG REST API built by Jannis (@derhuerst), which is a wrapper around the BVG HAFAS API, and used it as the data source for this project.

---

## **Purpose**
This project aims to:
- **Understand the operational efficiency** of tram line M13.
- Learn and apply data engineering concepts by creating a data pipeline.
- Generate insights that can answer specific questions about tram performance.

---

## **Questions to Analyze**
1. On average, **how punctual** is tram M13 at the stations of interest:
   - **Schönhauser Allee/Bornholmer Straße**
   - **Antonplatz**
2. What is the **total number of trips per day** for tram M13?
3. How many trips **arrived or departed late** at the stations of interest?

---

## **Technical Approach**
### **1. Data Pipeline Overview**
The data pipeline fetches, processes, and stores tram data from the BVG REST API.

#### **Components**
- **API**: BVG REST API by Jannis (@derhuerst).
- **Stations of Interest**:
  - Schönhauser Allee/Bornholmer Straße
  - Antonplatz
- **Endpoints Used**:
  - Departures (`/stops/:id/departures`)
  - Arrivals (`/stops/:id/arrivals`)

### **2. Data Processing**
- Extract relevant details for tram M13, such as:
  - **Trip ID**
  - **Line**
  - **Direction**
  - **Scheduled and Actual Arrival/Departure Times**
  - **Delays**
- Calculate delays and classify trips as punctual or late.

### **3. Data Storage**
- Processed data is converted into **Pandas DataFrames**.
- Saved as **Parquet files** in an S3 bucket for efficient storage and retrieval.
- Filenames include station name, endpoint (departures/arrivals), and timestamp.

### **4. Scheduling**
- **Scheduler**: Since the project uses a small EC2 t2.micro instance (1vCPU, 1GB RAM), I implemented a **cron job** scheduler instead of heavier solutions like Airflow or Mage.
- Data is fetched and processed at regular intervals to maintain up-to-date information.

---

## **Future Plans**
In the next phase of this project, I plan to:
- **Transform the Parquet files** to create a more analysis-friendly format.
- Enable a **data analyst (me in this case)** to easily answer the defined questions.
- Explore adding dashboards or visualization tools to present the insights in a user-friendly manner.

---

## **Acknowledgments**
Thanks to [@derhuerst](https://github.com/derhuerst) for creating the BVG REST API wrapper!


