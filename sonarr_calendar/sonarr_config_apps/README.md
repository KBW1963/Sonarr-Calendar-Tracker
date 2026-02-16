# Sonarr Calendar Tracker – Configuration Scripts

This folder contains two helper scripts to create the configuration file for the [Sonarr Calendar Tracker](https://github.com/yourusername/sonarr-calendar).  
Both scripts generate a `.sonarr_calendar_config.json` file in the same directory where they are run.

---

## 📋 Prerequisites

- **Python 3.8 or higher** installed on your system.
- Your **Sonarr URL** and **API key** (find the API key in Sonarr under **Settings → General**).

No additional Python packages are required – the scripts use only the standard library.

---

## 🔧 Which script should I use?

| Script | Description |
|--------|-------------|
| `sonarr_config_cli.py` | **Full interactive wizard** – asks for every possible setting, explains each option, and validates your inputs. Ideal for first‑time users or those who want full control. |
| `sonarr_calendar_config.py` | **Quick setup** – asks only for the essential information (URL, API key, output file) and uses sensible defaults for everything else. Perfect for experienced users or quick configurations. |

Both scripts produce the same configuration file – you can run either one depending on your preference.

---

## 🚀 How to use

### 1. Open a terminal / command prompt
Navigate to the folder containing the scripts.

### 2. Run the script of your choice

- For the full wizard:
  ```bash
  python sonarr_config_cli.py