## NASA Astronomy Picture of the Day (APOD) Viewer

A simple Python-based web server that lets users view NASA’s Astronomy Picture of the Day (APOD) and select any date to explore previous images and videos.


## Project Motivation

NASA’s APOD API showcases daily images and videos that celebrate the wonders of the universe. By default, it only shows today’s picture. This project enhances the experience by adding a date picker so users can explore APODs from any day they wish.


## Setup Instructions

1. Clone the repo
2. Get NASA API Key from: https://api.nasa.gov/
3. Setup your API Key run: $Env:NASA_API_KEY = "your_api_key_here" in powershell terminal
4. Run the server: python NASA_apod.py
5. On your browser, go to: http://localhost:8080/apod

## Features
1. Simple Python HTTP server using socket and requests
2. Dynamic HTML page with a modern design and integrated date picker
3. Fetches APOD data directly from NASA’s public API
4. Supports images and videos

## Technical Concepts Used
1. HTTP request parsing and response generation
2. Environment variables for API key management
3. HTML forms and CSS styling
4. External API integration



