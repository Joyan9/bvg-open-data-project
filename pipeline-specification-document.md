# BVG Open Data Project

### **1. Purpose**
The purpose of this data pipeline is to collect and analyze data for Berlin tram line **M13** to:
- Track its **schedule and performance** between the stations **Schönhauser Allee/Bornholmer Straße** and **Antonplatz**.
- Identify **peak hours** by analyzing high occupancy times.
- Measure **punctuality** by comparing scheduled versus actual arrival and departure times.
- Monitor for **disturbances** on the tram line and analyze how frequently they occur.

This data pipeline aims to provide insights into the operational efficiency and usability of tram M13, which I can use for my day-to-day travelling.


## **Key Components**

### **1. Data Fetching**
- **Stations**:  
  - Schönhauser Allee/Bornholmer Straße  
  - Antonplatz
- **API Endpoints**:  
  - Departures (`/stops/:id/departures`)  
  - Arrivals (`/stops/:id/arrivals`)
- **Filters**:  
  - Specific directions of interest to refine the data.

### **2. Data Processing**
- Extract relevant trip details, including:  
  - **Trip ID**, **line**, **direction**, and **arrival/departure times**.  
  - **Delays**: Calculate differences between scheduled and actual times.  
  - **Occupancy**: Capture inferred occupancy trends.  
  - **Remarks**: Note any service alerts or disturbances.

### **3. Data Storage**
- Convert processed data into a **Pandas DataFrame**.  
- Save data as **Parquet files** for efficient storage and retrieval.  
- Store files in an **S3 bucket**, with filenames including:  
  - Station name.  
  - API endpoint (departures or arrivals).  
  - Timestamp of data retrieval.

---

## **Core Functions**

### **1. `fetch_data()`**
- Sends API requests to BVG REST endpoints.  
- Handles station-specific queries (departures/arrivals).  
- Implements error handling for API failures.

### **2. `process_data()`**
- Transforms raw API responses into a clean, structured format.  
- Performs calculations and filters for delays, occupancy, and remarks.

### **3. `save_to_s3()`**
- Uploads processed data to an Amazon S3 bucket.  
- Organizes files by station, endpoint, and retrieval timestamp.

### **4. `fetch_process_save()`**
- Orchestrates the workflow:  
  - Fetches data from the API.  
  - Processes and transforms it.  
  - Stores the results in S3.

---

## **Scheduling**
- Designed for **periodic execution** using tools like **cron jobs** or **Airflow**.  
- Supports scalability for running across multiple stations and endpoints.  
- Includes robust error handling to retry failed tasks and log errors.

---

## **Technical Details**
- **API Calls**: Made using the `requests` library.  
- **Data Manipulation**: Processed using `pandas`.  
- **S3 Integration**: Managed via `boto3`.  
- **File Format**: Parquet for compact, efficient storage.  
