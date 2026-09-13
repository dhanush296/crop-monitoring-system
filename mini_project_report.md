# Mini Project Report: AI Crop Monitoring System

## 1. Problem Statement
Farmers face significant challenges in continuously monitoring crop health, managing unpredictable weather conditions that lead to pest outbreaks, and tracking soil quality. Traditional manual monitoring is time-consuming, requires extensive agricultural knowledge, and is prone to human error. Furthermore, traditional soil testing requires physical samples to be sent to laboratories, delaying critical interventions. This lack of immediate, integrated information leads to delayed disease treatment, suboptimal resource usage, reduced crop yields, and financial losses. There is a pressing need for a unified, real-time system that can instantly diagnose plant diseases, assess soil conditions, and predict pest risks using accessible technology.

## 2. Objective
To develop an AI-powered Crop Monitoring System that provides real-time, actionable insights to farmers. The primary objectives are:
*   **Automated Disease Detection:** Utilize a machine learning model to diagnose crop health from uploaded leaf images.
*   **Environmental Monitoring:** Integrate live weather and soil data APIs (OpenWeather and Open-Meteo) based on the user's GPS coordinates or city location.
*   **Comprehensive Assessment:** Calculate dynamic soil scores and pest risk levels using a hybrid of real-time telemetry and heuristic algorithms.
*   **Intuitive Visualization:** Present all data on an easy-to-use, responsive web dashboard that includes data visualizations (Chart.js) and clear recommended action plans.

## 3. Existing Systems
Existing agricultural monitoring solutions often operate in silos. They typically tackle only one specific aspect of farming—such as standalone mobile apps for disease detection via image classification, or generic weather forecasting websites. They rarely integrate these distinct data points into a cohesive whole. Current applications generally lack the ability to synthesize live API weather data, physical soil conditions, and AI-driven image predictions to provide an immediate, overarching "Action Plan" tailored to a specific location and plant condition.

## 4. Novelty
*   **Unified Dashboard:** Synthesizes image-based AI crop health diagnosis, live GPS-based weather data, and real-time soil condition telemetry into a single, intuitive interface.
*   **Dynamic Heuristic Scoring:** Implements a custom algorithm that calculates a dynamic "Soil Score" by combining simulated base nutrients (NPK) with live soil temperature and moisture penalties from the Open-Meteo API.
*   **Predictive Pest Risk:** Evaluates local temperature and humidity thresholds from the OpenWeather API to predict potential pest outbreaks (High, Medium, Low risk).
*   **Actionable Intelligence:** Rather than just presenting raw data, the system automatically translates the combined environmental and health data into localized, recommended action plans for the farmer.

## 5. Code Implementation
The project is built using a modern, lightweight tech stack:
*   **Backend (Python/Flask):** 
    *   Exposes a REST API (`/predict`) to handle image uploads and location data.
    *   **AI Model:** Uses `TensorFlow`/`Keras` to load a pre-trained model (`crop_model_fixed.keras`) for image classification.
    *   **External Integrations:** Utilizes the `requests` library to fetch live data from the OpenWeather API (temperature, humidity, coordinates) and Open-Meteo API (soil temperature, soil moisture).
    *   **Logic Engine:** Contains custom Python functions (`get_weather_and_pest_risk`, `get_soil_data`) to process raw API data into human-readable risks and scores.
*   **Frontend (HTML/CSS/JavaScript):** 
    *   A responsive, single-page application built with vanilla web technologies.
    *   Uses the browser's Geolocation API to fetch precise user coordinates.
    *   Integrates **Chart.js** to render a dynamic bar chart for the NPK nutrient breakdown.
    *   Communicates with the Flask backend via `fetch` API to retrieve and display the AI predictions and telemetry data seamlessly.

## 6. Output
The final output is a web-based dashboard where:
1.  The user uploads an image of a crop leaf and provides their location (via text or GPS button).
2.  The system processes the input and updates the dashboard with:
    *   **Health Status:** The predicted crop health/disease (e.g., Healthy, Apple Scab).
    *   **Soil Score:** A calculated score out of 100 based on moisture, temperature, and nutrients.
    *   **Pest Risk:** A categorical risk level based on current weather conditions.
    *   **Nutrient Breakdown:** A graphical NPK chart.
    *   **Action Plan:** A clear, text-based recommendation on what the farmer should do next based on the synthesized data.

## 7. Github repository link
*Please insert your GitHub repository URL here (e.g., https://github.com/username/crop-monitoring-system)*
