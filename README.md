# NIA – National Identity Analytics

<p align="center">
  <strong>Transforming India's Digital Identity Ecosystem</strong><br/>
  AI-powered Administrative Intelligence + Privacy-Preserving Citizen Verification
</p>
<p align="center">
  <img src="docs/banner.png" alt="Platform Banner" width="90%"/>
</p>
<p align="center">
  <a href="https://python.org">
    <img src="https://img.shields.io/badge/Python-3.10+-green.svg" alt="Python"/>
  </a>
  <a href="https://reactjs.org">
    <img src="https://img.shields.io/badge/React-18.3-blue.svg" alt="React"/>
  </a>
  <a href="https://fastapi.tiangolo.com">
    <img src="https://img.shields.io/badge/FastAPI-0.115-teal.svg" alt="FastAPI"/>
  </a>
  <a href="https://build.nvidia.com">
    <img src="https://img.shields.io/badge/NVIDIA-NIM-76B900.svg" alt="NVIDIA NIM"/>
  </a>
</p>
<p align="center">
  <a href="#">Video Walkthrough</a> •
  <a href="#">Presentation</a>
</p>

## Table of Contents

- [Overview](#-overview)
- [Problem Statement](#-problem-statement)
- [Key Innovation](#-key-innovation)
- [Features](#-features)
- [Architecture](#-architecture)
- [Technology Stack](#-technology-stack)
- [Getting Started](#-getting-started)
- [Usage](#-usage)
- [Novel Contributions](#-novel-contributions)
- [Performance](#-performance)
- [Screenshots](#-screenshots)
- [Team](#-team)
- [License](#-license)

## Overview

**NIA – National Identity Analytics** is an enterprise-grade analytics engine designed to help administrators, policymakers, and fraud investigators understand the pulse of India's large-scale digital identity ecosystem.

By combining high-performance data processing with cutting-edge AI, NIA transforms raw enrolment and update logs into **real-time dashboards, predictive intelligence, and privacy-preserving verification systems**.

## Problem Statement

Managing the identity lifecycle of over a billion citizens is an immense challenge. Traditional reporting tools look backward, showing you what happened last month. This platform looks forward.

We built this solution to answer critical questions in real-time:

- _Where is the next surge in biometric updates coming from?_
- _Which pincodes are showing suspicious update patterns right now?_
- _How can we optimize staffing based on predicted footfall next week?_

## Key Innovation

NIA introduces **AI-powered conversational analytics** combined with **proprietary risk indices** (Identity Velocity Index, Biometric Stress Index) that transform massive identity datasets into actionable intelligence. Unlike traditional BI tools, NIA enables natural language querying of complex administrative data while maintaining privacy and security at scale.

## Features

### AI Analyst Assistant

**Stop writing queries. Start asking questions.**

Interact with your data in plain English. Our NVIDIA-powered AI agent understands context, remembers your conversation, and can instantly pull complex stats, compare regions, or explain trends.

> _"Which state has the highest biometric stress index this month?"_

### Real-Time Anomaly Detection

**Spot fraud before it spreads.**

Automatically monitor thousands of pincodes for suspicious behavior. The system flags high-risk areas using advanced statistical models, identifying unusual spikes in demographic changes or biometric failures that could indicate fraud or system errors.

### Predictive Forecasting

**Know what's coming.**

Don't just react to demand—anticipate it. Our forecasting engine predicts enrolment and update volumes for the next 30 days, helping you allocate resources, staff centers, and manage infrastructure capacity proactively.

### Granular Regional Intelligence

**From National view to District details.**

Drill down instantly from a national overview to specific state and district performance. Compare regions side-by-side using proprietary metrics like the **Identity Velocity Index (IVI)** and **Biometric Stress Index (BSI)** to understand operational health at a glance.

### Dynamic Clustering

**Understand behavior patterns.**

Go beyond geography. Our machine learning clustering groups states based on actual usage patterns and stress markers, helping you apply targeted policies to regions facing similar challenges, regardless of their location.

## Architecture

<figure align="center">
  <img src="docs/diagram_1.png" alt="Mobile Process Flow Diagram" width="90%"/>
  <figcaption>Mobile Process Flow</figcaption>
</figure>

<figure align="center">
  <img src="docs/diagram_2.png" alt="Web Portal Flow Diagram" width="90%"/>
  <figcaption>Web Portal (Analytics + Admin)</figcaption>
</figure>


**Key Components:**

- **Data Pipeline:** High-performance CSV processing using Polars (10x faster than Pandas)
- **ML Engine:** Anomaly detection, forecasting, and clustering models
- **AI Agent:** NVIDIA NIM-powered conversational interface with context retention
- **Cache Layer:** Redis for sub-second query responses
- **Frontend:** Responsive React dashboard with interactive visualizations

## Technology Stack

### Backend

- **FastAPI** - High-performance async API framework
- **Polars** - Lightning-fast dataframe operations
- **NVIDIA NIM** - LLM inference for conversational AI
- **Redis** - In-memory caching and session management
- **SQLite** - Conversation persistence
- **Scikit-learn** - Machine learning models

### Frontend

- **React 18** - Modern UI framework
- **Vite** - Next-generation frontend tooling
- **TailwindCSS** - Utility-first styling
- **Chart.js** - Interactive data visualizations
- **Axios** - HTTP client

### Data Processing

- **Prophet** - Forecasting time-series data
- **NumPy** - Numerical computing
- **Pandas** - Data analysis (legacy support)

### Agentic AI

- **LangGraph** - Building Stateful and Complex Agent Workflows

## Getting Started

Get up and running with the full intelligence suite in minutes.

**Prerequisites:**

- Python 3.10+
- Node.js 18+

**Launch the Platform:**

Simply run the startup script for your OS:

**Windows:**

```cmd
start_platform.bat
```

**Linux/Mac:**

```bash
./start_platform.sh
```

Access the dashboard at `http://localhost:5173` and the API documentation at `http://localhost:8000/docs`.

## Usage

### Use Cases

- **For Policy Makers:** Design data-driven interventions for regions with low saturation or high rejection rates.
- **For Fraud Investigators:** Instantly isolate pincodes with "High Risk" flags for on-ground verification.
- **For Operations Managers:** Dynamic staffing for enrolment centers based on 30-day volume forecasts.
- **For Data Analysts:** Export clean, pre-processed insights without spending hours on data cleaning.

### Interacting with the AI Assistant

Simply ask questions in natural language:

- _"Which state has the highest biometric stress index this month?"_
- _"Show me pincodes with anomalous activity in Maharashtra"_
- _"Predict enrolment volume for Karnataka next 30 days"_

## Novel Contributions

### 1. Proprietary Risk Indices

- **Identity Velocity Index (IVI):** Measures the rate of identity changes relative to population density
- **Biometric Stress Index (BSI):** Quantifies biometric update pressure and failure patterns

### 2. Conversational Analytics

Natural language interface to complex administrative queries using NVIDIA NIM, eliminating the need for SQL knowledge or BI tool expertise.

### 3. Privacy-Preserving Architecture

All analytics operate on aggregated data with no PII exposure. Individual records never leave the processing layer.

### 4. Real-Time Anomaly Detection

Statistical anomaly detection across 19,000+ pincodes with automatic risk scoring and prioritization.

### 5. Predictive Capacity Planning

ML-powered forecasting for resource allocation and infrastructure planning.

## Performance

- **Data Processing:** Handles 2M+ records in under 5 seconds using Polars
- **Query Response:** Sub-second responses via Redis caching
- **Concurrent Users:** Supports 1000+ simultaneous dashboard users
- **AI Response Time:** Average 2-3 seconds for complex analytical queries
- **Data Refresh:** Monthly automated sync from source systems

## Screenshots

<p align="center">
  <img src="docs/mobile_screens.png" alt="App Screenshots" width="100%"/>
</p>

<style>
  .grid-container {
    display: grid;
    /* Creates 2 columns, each taking an equal fraction of the space */
    grid-template-columns: 1fr 1fr;
    /* Adds a small gap between the images */
    gap: 10px; 
    /* Centers the grid within the markdown document */
    justify-items: center; 
  }
  .grid-item img {
    /* Ensures images are responsive and don't overflow their grid area */
    width: 100%;
    height: auto;
    padding: 5px;
  }
</style>

<div class="grid-container">
  <div class="grid-item">
    <img src="docs/laptop_1.png" alt="State-wise Analysis">
  </div>
  <div class="grid-item">
    <img src="docs/laptop_2.png" alt="Executive Dashboard">
  </div>
  <div class="grid-item">
    <img src="docs/laptop_3.png" alt="State Clustering Analysis">
  </div>
  <div class="grid-item">
    <img src="docs/laptop_4.png" alt="Anamoly Detection">
  </div>
</div>

## 👥 Team

- [Vaidik Jaiswal](https://github.com/vaidikjais)
- [Arslaan Siddiqui](https://github.com/arslaan5)

---

_Built for the future of Identity Management._
