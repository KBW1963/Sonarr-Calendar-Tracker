# Sonarr Calendar Tracker

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Sonarr](https://img.shields.io/badge/Sonarr-v3%2Fv4-orange)

A beautiful, feature‑rich HTML dashboard for your Sonarr shows.  
Track upcoming episodes, monitor overall progress, and see which seasons have been completed – all in a sleek, customisable interface.

![Screenshot](docs/sc<img width="1864" height="6360" alt="sonarr_calendar_screenshot" src="https://github.com/user-attachments/assets/562caa25-62f6-4956-808b-1768eb892400" />
reenshot.png) <!-- Add a screenshot later -->

---

## ✨ Features

- 📅 **Customisable date range** – Choose how many days past and future to display.
- 🖼️ **Poster image caching** – Images are downloaded and stored locally for faster loading.
- 🎨 **Dark/light theme toggle** – Switch between themes with a click (your choice is saved in your browser).
- 📊 **Overall & per‑show progress** – See at a glance how much of your library is downloaded, and drill down into each series.
- 🏆 **Recently completed seasons** – Shows that finished their current season within the date range are highlighted.
- 🔄 **Auto‑refresh mode** – Keep the dashboard running and update periodically (configurable).
- ⌨️ **Graceful interrupt handling** – Press `Ctrl+C` once to exit cleanly, twice to force quit.
- 🌍 **OS‑aware date formatting** – Dates automatically adapt to your system’s locale (e.g. `DD/MM/YYYY` or `MM/DD/YYYY`).
- 🔗 **Direct links to Sonarr** – Click any show card to open its page in Sonarr.

---

## 📦 Requirements

- **Python 3.8 or higher**
- **Sonarr** (v3 or v4) with API access
- Operating systems: Windows, macOS, Linux (all fully supported)

---

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/sonarr-calendar.git
cd sonarr-calendar
