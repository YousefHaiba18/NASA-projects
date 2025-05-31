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


