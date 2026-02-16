# Sonarr Calendar Tracker – Configuration Scripts

This folder contains two helper scripts to create the configuration file for the [Sonarr Calendar Tracker](https://github.com/yourusername/sonarr-calendar).  
By default both scripts generate a `.sonarr_calendar_config.json` file in the same directory where they are run, however you can specify specific locations for all output, just remember the JSON file needs to be in the folder where you execute the main sonnar_calendar script.
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
| `sonarr_calendar_config.py` | **Form based** – Is a GUI based form. Input the valuesin order to setup the configuration.|

Both scripts produce the same configuration file – you can run either one depending on your preference.

---

## 🚀 How to use

### 1. Open a terminal / command prompt
Navigate to the folder containing the scripts.


### 2. Run the script of your choice
Remember you may need to use python3 on Linux OS's

- CLI or GUI
  ```bash

  python sonarr_config_cli.py or python sonarr_calendar_config.py

