# Delivery Driver Management & Route Optimization System

This is a full-stack application designed to manage delivery drivers, orders, and optimize delivery routes. It consists of a FastAPI backend and a React.js frontend.

## Table of Contents

-   [Features](#features)
-   [Tech Stack](#tech-stack)
-   [Project Structure](#project-structure)
-   [Getting Started](#getting-started)
    -   [Prerequisites](#prerequisites)
    -   [Running with Docker Compose](#running-with-docker-compose)
    -   [Running Locally (Backend)](#running-locally-backend)
    -   [Running Locally (Frontend)](#running-locally-frontend)
-   [API Endpoints](#api-endpoints)
-   [Testing](#testing)
-   [Data Files](#data-files)
-   [Deployment](#deployment)

## Features

-   **Backend (FastAPI)**:
    -   Reads driver, order, and route data from CSV files.
    -   Provides **full CRUD (Create, Read, Update, Delete) API endpoints** for managing drivers, orders, and routes.
    -   Implements a route optimization algorithm to assign orders to drivers based on defined optimization rules and **calculates Key Performance Indicators (KPIs)**.
    -   **Stores and retrieves past simulation runs (history)**.
    -   Includes **input validation and error handling** for simulation parameters.
    -   Uses SQLAlchemy ORM with SQLite for data persistence.
-   **Frontend (React.js)**:
    -   **Dashboard** for an overview of drivers, orders, and **key performance indicators (KPIs)**.
    -   Pages to list and view details of orders and routes.
    -   **Optimization page with input forms** to trigger the order assignment process, **display KPIs**, and visualize results with **multiple charts**.
    -   **Management pages with full CRUD UI** for Drivers, Routes, and Orders.
    -   **Simulation History page** to view past simulation results.

## Tech Stack

-   **Backend**: Python (FastAPI), SQLAlchemy (SQLite), Pandas, Scikit-learn (for basic optimization heuristics).
-   **Frontend**: React.js, Tailwind CSS, Axios, Chart.js.
-   **Deployment**: Docker, Docker Compose.

## Project Structure

```
delivery-driver-system/
├── backend/                  # FastAPI backend application
│   ├── app/                  # Python source code
│   ├── data/                 # CSV data files (drivers.csv, orders.csv, routes.csv)
│   ├── tests/                # Unit tests for the backend
│   ├── Dockerfile            # Dockerfile for the backend service
│   ├── requirements.txt      # Python dependencies
│   └── README.md             # Backend specific README
├── frontend/                 # React.js frontend application
│   ├── public/               # Public assets
│   ├── src/                  # React source code
│   ├── Dockerfile            # Dockerfile for the frontend service
│   ├── package.json          # Node.js dependencies
│   └── README.md             # Frontend specific README
├── docker-compose.yml        # Defines multi-container Docker application
├── Makefile                  # Utility commands for development
└── README.md                 # Main project README
```

## Getting Started

### Prerequisites

-   [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed.
-   [Make](https://www.gnu.org/software/make/) (usually pre-installed on Linux/macOS).

### Running with Docker Compose

Navigate to the root of the project directory (`delivery-driver-system/`) and run:

```bash
make start
```

This command will:
1.  Build the Docker images for both backend and frontend.
2.  Start the backend service (FastAPI) on `http://localhost:8000`.
3.  Start the frontend service (React.js) on `http://localhost:3000`.
4.  The backend will automatically load data from the CSV files into an SQLite database (`sql_app.db`) on its first startup.

To stop the services and clean up:

```bash
make clean
```

### Running Locally (Backend)

Refer to `backend/README.md` for detailed instructions on running the backend locally without Docker.

### Running Locally (Frontend)

Refer to `frontend/README.md` for detailed instructions on running the frontend locally without Docker.

## API Endpoints

FastAPI automatically generates interactive API documentation (Swagger UI) at `http://localhost:8000/docs`.

For detailed API documentation, including request/response examples for each endpoint, please refer to the `backend/README.md` file.

## Testing

To run backend unit tests using Docker:

```bash
make test
```

For local backend testing, refer to `backend/README.md`.

## Data Files

Initial data for drivers, orders, and routes are provided in CSV format within the `backend/data/` directory. These files are automatically loaded into the database when the backend starts.

-   `drivers.csv`: Contains driver information.
-   `orders.csv`: Contains order details.
-   `routes.csv`: Contains route details.

## Deployment

Dockerfiles are provided for both the backend and frontend, making the application ready for deployment to cloud platforms. You can use services like Render, Railway, Heroku, or Vercel for the backend, and Vercel or Netlify for the frontend.

-   **Backend Deployment**: The `backend/Dockerfile` can be used to build and deploy the FastAPI application.
-   **Frontend Deployment**: The `frontend/Dockerfile` can be used to build and deploy the React application.

Consult the documentation of your chosen deployment platform for specific instructions on deploying Dockerized applications.