
---

# VollerAi Backend - AI-Powered Data Analyst for Kenya's Current Issues

The **VollerAi Backend** is a powerful AI-driven data analysis tool focused on gathering and processing data from Instagram’s Graph API. The backend is responsible for filtering, analyzing, and generating insights on key issues affecting Kenya, including employment, financial trends, and climate change. Built using Django, this backend houses the core functionality of VollerAi, including API endpoints, data collection processes, financial tracking, and educational content generation.

The backend integrates various technologies to ensure real-time updates, transparency in government financial monitoring, and the creation of dynamic educational content based on the analyzed data. It is designed to run efficiently on Google Cloud Platform (GCP) with automatic data collection and updates via Cron jobs.

## Key Features

### 1. **AI-Driven Data Analysis**
   - VollerAi gathers data from trusted Instagram news accounts and uses machine learning algorithms to filter out irrelevant content.
   - The AI model focuses on significant socio-economic issues affecting Kenya such as employment trends, climate conditions, and financial transparency.
   - The data is then processed to generate actionable insights, predictions, and summaries.

### 2. **Instagram Data Collection**
   - The backend uses Instagram's Graph API to collect posts and stories from pre-approved and trusted news sources in Kenya.
   - The collected data undergoes filtering and analysis before being stored in the PostgreSQL database.

### 3. **Financial Tracking**
   - VollerAi tracks and reports on financial spending by the Kenyan government.
   - Detailed reports on financial allocations, spending patterns, and usage are generated to promote transparency and accountability.
   
### 4. **Dynamic Educational Content**
   - The backend generates educational material based on current issues and trends identified in the data.
   - These courses are updated dynamically as new data is processed, ensuring that citizens always have access to the latest information.

### 5. **Regular Data Updates**
   - Cron jobs are used to schedule automatic data collection and analysis at regular intervals.
   - This ensures that VollerAi’s insights are always up-to-date and relevant.

## API Endpoints

The backend provides RESTful API endpoints for interacting with the processed data. These endpoints allow users and developers to retrieve key insights, trends, and educational content.

### Available Endpoints

- **/api/v1/data/issues/** - Retrieves key socio-economic issues, including employment trends, financial statistics, and more.
- **/api/v1/data/financial-monitoring/** - Provides detailed financial reports on government spending, including tracked usage.
- **/api/v1/data/educational-courses/** - Returns educational content generated based on the analyzed data.

More detailed API documentation can be found in the project repository.

## Tech Stack

### **Backend Framework: Django**
   - **Django** is the core of VollerAi’s backend. It handles data collection, filtering, and AI-driven insights generation.
   - **Django Rest Framework (DRF)** is used to create RESTful APIs, allowing seamless interaction between the frontend and backend.

### **Database: PostgreSQL**
   - **PostgreSQL** is used for managing the database, ensuring efficient storage and querying of large amounts of data collected from Instagram and other sources.

### **External API: Instagram Graph API**
   - The Instagram Graph API is used to pull data from trusted news accounts.
   - Data is extracted and processed by the AI model to identify relevant socio-economic issues.

### **Deployment: Google Cloud Platform (GCP)**
   - The backend is hosted on **Google Cloud Platform (GCP)**, ensuring scalability and reliability.
   - **Cron jobs** are set up to schedule regular updates and re-analysis of the data.

### **Machine Learning: Python**
   - **Python** scripts are integrated to run machine learning models for data processing and insights generation.
   - These models filter out irrelevant content and identify trends in the gathered data.

## Cron Jobs for Regular Data Updates

VollerAi’s backend uses Cron jobs to automate the data collection, analysis, and updating process. These jobs are scheduled to run at specific intervals to ensure that the information available to users is always fresh and relevant.

### Cron Jobs Include:

- **Data Collection Job**: Fetches new data from Instagram using the Graph API.
- **Data Analysis Job**: Filters and processes the newly collected data using AI algorithms.
- **Data Update Job**: Regularly updates financial tracking and educational content based on the latest trends.

## How to Set Up and Run Locally

### Prerequisites
1. **Python 3.x** installed.
2. **PostgreSQL** installed and configured.
3. **Django** and **Django Rest Framework** installed.
4. Instagram Graph API access token.

### Installation Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Manoty/VollerAi-backend.git
   cd VollerAi-backend
   ```

2. **Create a virtual environment and activate it**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # For Windows use: venv\Scripts\activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the PostgreSQL database**:
   - Create a new database for the project.
   - Update the `DATABASES` configuration in `settings.py` with your PostgreSQL credentials.

5. **Migrate the database**:
   ```bash
   python manage.py migrate
   ```

6. **Run the server**:
   ```bash
   python manage.py runserver
   ```

### Environment Variables

Make sure to set the following environment variables in your environment:

- **Instagram API Access Token**: Needed to access data from Instagram’s Graph API.
- **PostgreSQL Credentials**: Needed to connect to the PostgreSQL database.

### Cron Job Setup

To ensure regular data updates, configure your server with the following Cron jobs:

- Data collection and analysis.
- Financial report generation.
- Educational course updates.

Refer to the Google Cloud Platform (GCP) documentation on setting up Cron jobs for detailed instructions.

## Contributing to the Backend

We welcome contributions! If you are interested in contributing to the VollerAi Backend, please fork the repository, create a new branch, and submit a pull request. Make sure to include detailed documentation for any new functionality added.

## Issues and Feedback

This project is still in development, and we highly appreciate feedback and issue reports. If you encounter any problems or have suggestions for improvement, feel free to open an issue in this repository.

## Conclusion

The **VollerAi Backend** is the backbone of a groundbreaking AI-powered data analysis tool aimed at providing actionable insights into Kenya’s socio-economic issues. By continuously collecting and analyzing data from trusted sources, the backend enables VollerAi to stay updated on key issues affecting the country. With AI-driven predictions, financial transparency monitoring, and educational content generation, the VollerAi Backend is set to make a significant impact in promoting informed decision-making in Kenya.

