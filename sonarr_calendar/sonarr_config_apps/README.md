# Sonarr Calendar – Configuration Scripts

This folder contains two helper scripts to create the configuration file for the [Sonarr Calendar](https://github.com/yourusername/sonarr-calendar).  
- sonarr_calendar_config uses GUI UI and provides an input form (x64 use really) allowing user to input the required values.
- sonarr_config_cli version is for terminal use and walks through the required values.

---

## 📋 Prerequisites

- **Python 3.8 or higher** installed on your system.
- Your **Sonarr URL** and **API key** (find the API key in Sonarr under **Settings → General**).

No additional Python packages are required – the scripts use only the standard library.

---

## 🔧 Which script should I use?

| Script | Description |
|--------|-------------|
| `sonarr_config_cli.py` | **Interactive wizard** – Is CLI based. Ideal for Linux based OS's. You will be asked to provide required values in order to setup the configuration.|
| `sonarr_calendar_config.py` | **Form based** – Is a GUI based form. Input the values in order to setup the configuration.|

Both scripts produce the same configuration file – you can run either one depending on your preference.

---

## ?What will it ask?

The script will guide you through each setting with a clear explanation. 

You will be asked for:
- Sonarr URL – e.g., http://localhost:8989 (must start with http:// or https://)
- Sonarr API key – from Sonarr Settings → General
- Days past – number of days before today to include (default: 7)
- Days future – number of days after today to include (default: 7)
- Output HTML file – path where the dashboard will be saved (default: sonarr_calendar.html)
- Output JSON file – optional, leave empty to skip
- Image cache directory – folder for storing posters (default: sonarr_images)
- Refresh interval (hours) – how often to auto‑refresh (default: 6)

### After entering all values, you will see a summary and be asked to confirm before the file is written.
---
### 📁 Where is the configuration file saved?

### Both scripts save the configuration as .sonarr_calendar_config.json in the current working directory (the directory from which you ran the script).
### This is also where the main calendar generator will look for it by default.
---

## 🚀 How to use

### 1. Open a terminal / command prompt
Navigate to the folder containing the scripts.


### 2. Run the script of your choice
Remember you may need to use python3 on Linux OS's

- CLI or GUI
  ```bash

  python sonarr_config_cli.py or python sonarr_calendar_config.py

