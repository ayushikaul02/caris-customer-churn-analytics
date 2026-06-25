# 📊 CARIS - Customer Churn Analytics & Retention Intelligence System

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io)
[![Docker](https://img.shields.io/badge/Docker-24.0+-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🎯 Overview

**CARIS** (Customer Churn Analytics & Retention Intelligence System) is an enterprise-grade customer churn analytics and retention system designed for telecom and e-commerce companies. It helps businesses monitor customer behavior, identify churn risks, analyze retention factors, and generate actionable insights.

Built as a Summer Internship project, this system demonstrates full-stack development capabilities with Python, FastAPI, Streamlit, and Docker.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📊 **Interactive Dashboard** | Real-time KPI monitoring with Streamlit |
| 🔐 **JWT Authentication** | Secure login with role-based access (admin/user) |
| 📈 **Customer Analytics** | Segmentation, Churn Analysis, Revenue Analysis |
| 🎯 **Retention Engine** | Personalized recommendations & campaigns |
| 📁 **Data Pipeline** | CSV, Excel, API ingestion with cleaning |
| 📊 **Reporting** | Excel, JSON, HTML report generation |
| 🐳 **Dockerized** | Easy deployment with Docker |

---
## 🔬 Model Explainability (SHAP Analysis)

Understanding *why* customers churn is as important as predicting it. SHAP (SHapley Additive exPlanations) analysis reveals the key drivers of churn.

### Feature Importance

![SHAP Feature Importance](shap_feature_importance.png)

![SHAP Feature Importance Bar](shap_feature_importance_bar.png)

### Key Insights from SHAP Analysis

| Feature | Impact on Churn |
|---------|-----------------|
| **Total Spent** | Strongest predictor - higher spending = lower churn |
| **Monthly Charge** | Moderate impact - higher charges = more loyalty |
| **Age** | Lower influence - consistent across age groups |
| **Tenure** | Newer customers are at higher risk |

### Business Implications

1. **Focus on High-Value Customers**: Customers with higher total spent are more loyal
2. **Target New Customers**: Tenure is a key indicator - focus retention on new customers
3. **Monitor Monthly Charges**: Pricing strategy directly impacts churn

> **Note**: SHAP analysis was performed using a Random Forest model trained on customer data. The model achieved 85% accuracy in predicting churn.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CARIS SYSTEM ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────────────┐    │
│  │  DATA       │    │   DATA PIPELINE │    │    ANALYTICS ENGINE     │    │
│  │  SOURCES    │    │                 │    │                         │    │
│  │             │    │  ┌───────────┐  │    │  ┌───────────────────┐  │    │
│  │  ┌───────┐  │    │  │  Clean &  │  │    │  │   Segmentation   │  │    │
│  │  │ CSV   │──┼────┼─▶│ Transform │──┼────┼─▶│   (K-Means)      │  │    │
│  │  └───────┘  │    │  └───────────┘  │    │  └───────────────────┘  │    │
│  │             │    │                 │    │                         │    │
│  │  ┌───────┐  │    │  ┌───────────┐  │    │  ┌───────────────────┐  │    │
│  │  │Excel  │──┼────┼─▶│  Feature  │──┼────┼─▶│   Churn Analysis  │  │    │
│  │  └───────┘  │    │  │  Engineer │  │    │  └───────────────────┘  │    │
│  │             │    │  └───────────┘  │    │                         │    │
│  │  ┌───────┐  │    │                 │    │  ┌───────────────────┐  │    │
│  │  │ API   │──┼────┼─▶  Validation   │    │  │  Revenue Analysis │  │    │
│  │  └───────┘  │    │                 │    │  └───────────────────┘  │    │
│  └─────────────┘    └─────────────────┘    └─────────────────────────┘    │
│                                                                             │
│                              │                                             │
│                              ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    RETENTION ENGINE                                  │   │
│  │  ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐   │   │
│  │  │ Recommendations│    │  Campaigns   │    │  Loyalty Rewards  │   │   │
│  │  └───────────────┘    └───────────────┘    └───────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                              │                                             │
│                              ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     DASHBOARD & API                                 │   │
│  │  ┌───────────────┐    ┌───────────────┐    ┌───────────────────┐   │   │
│  │  │  Streamlit    │    │   FastAPI     │    │    Swagger Docs   │   │   │
│  │  │  Dashboard    │    │   (13+ APIs)  │    │    (/docs)        │   │   │
│  │  └───────────────┘    └───────────────┘    └───────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

| Requirement | Version |
|-------------|---------|
| Python | 3.12+ |
| Git | Latest |
| Docker | 24.0+ (optional) |

### Installation Steps

```bash
# 1. Clone the repository
git clone https://github.com/ayushikaul02/caris-customer-churn-analytics.git
cd caris-customer-churn-analytics

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # On Linux/Mac
# OR
venv\Scripts\activate          # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Generate sample data
python scripts/generate_sample_data.py

# 5. Run the API server
python app.py

# 6. Run the dashboard (in a new terminal)
streamlit run dashboard.py
```

### Login Credentials

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Administrator |
| user | user123 | User |

---

## 📁 Project Structure

```
CARIS_Project/
│
├── 🚀 app.py                     # Main FastAPI application
├── 📊 dashboard.py               # Streamlit dashboard
├── 📦 requirements.txt           # Python dependencies
├── 🐳 Dockerfile                 # Docker configuration
├── 📝 docker-compose.yml         # Docker Compose setup
├── 📄 .env                       # Environment variables
├── 📋 .gitignore                 # Git ignore file
│
├── 📂 customer_ingestion/        # Data ingestion module
│   └── src/ingestion_service.py  # CSV, Excel, API, Database import
│
├── 📂 customer_transformation/   # Data cleaning & transformation
│   └── src/transformation_service.py
│
├── 📂 customer_analytics/        # Analytics engine
│   └── src/analytics_service.py  # Segmentation, Churn, Revenue
│
├── 📂 retention_engine/          # Retention recommendations
│   └── src/retention_service.py
│
├── 📂 dashboard_service/         # KPI dashboard service
│   └── src/dashboard_service.py
│
├── 📂 reporting_service/         # Report generation
│   └── src/report_service.py    # Excel, JSON, HTML reports
│
├── 📂 common/                    # Shared utilities
│   ├── config/                   # Configuration
│   ├── database/                 # Database connection
│   └── logging/                  # Logging setup
│
├── 📂 data/raw/                  # Sample data
│   ├── customers.csv
│   ├── subscriptions.csv
│   ├── transactions.csv
│   ├── support_tickets.csv
│   └── referrals.csv
│
├── 📂 scripts/                   # Utility scripts
│   ├── generate_sample_data.py
│   └── clean_customer_data.py
│
├── 📂 tests/                     # Unit tests
│   └── test_api.py
│
└── 📂 reporting_service/reports/ # Generated reports
```

---

## 📊 API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login to get JWT token |
| GET | `/api/auth/me` | Get current user info |

### Customers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/customers` | Get all customers (paginated) |
| GET | `/api/customers/{id}` | Get customer by ID |
| POST | `/api/customers` | Create new customer |
| PUT | `/api/customers/{id}` | Update customer |
| DELETE | `/api/customers/{id}` | Delete customer |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/churn` | Get churn analysis |
| GET | `/api/analytics/revenue` | Get revenue analysis |
| POST | `/api/analytics/customer-segments` | Get customer segmentation |
| GET | `/api/analytics/clv` | Get Customer Lifetime Value |
| GET | `/api/analytics/risk-analysis` | Get risk analysis |

### Dashboard

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/metrics` | Get all dashboard metrics |
| GET | `/api/dashboard/revenue` | Get revenue dashboard |
| GET | `/api/dashboard/customer` | Get customer dashboard |
| GET | `/api/dashboard/churn` | Get churn dashboard |
| GET | `/api/dashboard/regional` | Get regional dashboard |

### Retention

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/retention/recommendations` | Get retention recommendations |
| GET | `/api/retention/campaigns` | Get promotional campaigns |

### Reports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reports/monthly` | Generate monthly report |
| GET | `/api/reports/excel` | Generate Excel report |
| GET | `/api/reports/available` | List available reports |

> **📌 Note:** All endpoints (except `/` and `/health`) require JWT authentication.
> Full API documentation available at: `http://localhost:8000/docs`

---

## 🐳 Docker Deployment

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t caris-api .

# Run the container
docker run -p 8000:8000 caris-api
```

### Using Docker Compose

```bash
docker-compose up --build
```

### Verify Deployment

```bash
# Check if container is running
docker ps

# Test the API
curl http://localhost:8000/health
```

---

## 📊 Test Results

```
============================= test session starts =============================
collected 10 items

tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_root PASSED
tests/test_api.py::test_get_customers PASSED
tests/test_api.py::test_dashboard_metrics PASSED
tests/test_api.py::test_churn_analysis PASSED
tests/test_api.py::test_revenue_analysis PASSED
tests/test_api.py::test_recommendations PASSED
tests/test_api.py::test_customer_segments PASSED
tests/test_api.py::test_monthly_report PASSED
tests/test_api.py::test_excel_report PASSED

============================= 10 passed in 24.08s =============================
```

---

## 🛠️ Technology Stack

| Category | Technologies |
|----------|--------------|
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Data Processing** | Pandas, NumPy, Scikit-learn |
| **Machine Learning** | K-Means Clustering, Risk Scoring |
| **Dashboard** | Streamlit, Plotly, Matplotlib |
| **Database** | SQLAlchemy, PostgreSQL/MySQL, MongoDB |
| **Deployment** | Docker, AWS/Azure (planned) |
| **Authentication** | JWT, HTTPBearer |
| **Version Control** | Git, GitHub |
| **Testing** | Pytest, Requests |
| **Reporting** | OpenPyXL, ReportLab, JSON |

---

## 📈 Key Metrics Achieved

| Metric | Value |
|--------|-------|
| **Total Customers Analyzed** | 1,000+ |
| **Churn Rate Identified** | 16.1% |
| **Customer Segments** | 4 (Premium, High Value, Standard, Low Value) |
| **API Endpoints** | 13+ |
| **Tests Passed** | 10/10 |
| **Lines of Code** | 7,000+ |
| **Microservices** | 5 |
| **Data Structures** | 5 (Heap, Queue, Graph, HashMap, Trie) |

---

## 🔧 Environment Variables

Create a `.env` file in the root directory:

```env
# Database Configuration
DATABASE_URL=postgresql://user:pass@localhost:5432/caris_db
MYSQL_URL=mysql://user:pass@localhost:3306/caris_db
MONGODB_URL=mongodb://localhost:27017/

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your-secret-key-here

# Data Paths
RAW_DATA_PATH=./data/raw
PROCESSED_DATA_PATH=./data/processed
REPORT_PATH=./reporting-service/reports

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/app.log

# Redis
REDIS_URL=redis://localhost:6379
```

---

## 🎯 Project Deliverables

| Deliverable | Status |
|-------------|--------|
| Database Design Document | ✅ |
| ETL Pipeline | ✅ |
| Data Cleaning Framework | ✅ |
| Analytics Engine | ✅ |
| KPI Dashboard | ✅ |
| REST APIs | ✅ |
| Business Reports | ✅ |
| Project Documentation | ✅ |
| Deployment Guide | ✅ |

---

## 🚀 Future Roadmap

| Phase | Features |
|-------|----------|
| **Short-Term** | Cloud deployment, Authentication, Rate limiting |
| **Medium-Term** | Real-time data, Advanced ML (XGBoost), React frontend |
| **Long-Term** | Real-time churn prediction, Deep Learning, Mobile app |

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Ayushi Kaul**

---

## 🙏 Acknowledgments

| Thank You To | For |
|--------------|-----|
| FastAPI Team | Excellent framework and documentation |
| Streamlit Community | Amazing dashboard tool |
| Pandas Team | Powerful data processing |
| Scikit-learn Team | Machine learning algorithms |
| Mentor & Team | Guidance and support throughout internship |

---

## 📬 Contact

| Platform | Link |
|----------|------|
| GitHub | [@ayushikaul02](https://github.com/ayushikaul02) |
| LinkedIn | [Ayushi Kaul](https://linkedin.com/in/ayushikaul555) |
| Email | ayushikaul555@email.com |

---

## ⭐ Star the Project

If you found this project useful, please give it a ⭐ on GitHub!

---

**Made with ❤️ for the Summer Internship Program**

```
📅 Internship Duration: 15 May 2026 – 15 July 2026
🏢 Company: Sira Technology
👨‍💻 Role: Data Analytics Intern
```

---

*© 2026 CARIS - Customer Churn Analytics & Retention Intelligence System*
