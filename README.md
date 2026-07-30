# 📡 Telemetry & Station Hex Data Transformation Suite

A lightweight Python tool designed to read, sanitize, and convert telemetry station CSV exports containing hex-encoded values (e.g., coordinates, threshold levels, and server logs) into human-readable CSV files or SQL database dumps.

---

## 🛠️ Problem & Background

When exporting station metadata or telemetry readings directly from database dumps or legacy FTP/SCADA servers, string data like thresholds (`alert_threshold`, `danger_threshold`) or GPS coordinates (`latitude`, `longitude`) are often represented as raw hex strings or truncated fields.

Common issues during manual processing include:
* **Excel Scientific Notation Corruption:** Hex strings containing letters like `e` (e.g., `312e3930`) are misidentified by spreadsheet editors as scientific notation, causing values to overflow into `inf` or become corrupted.
* **Header & Format Truncation:** Exported headers like `latitude_hex` or `warning_threshold_hex` get cut off (`latitude_h`, `warning_t`).
* **Delimiter Mismatches:** Inconsistent CSV exports using semi-colons (`;`), tabs (`\t`), or standard commas (`,`).

---

## ✨ Features & Solution

This tool automates the cleanup pipeline with zero manual intervention required:

* **Strict Raw String Ingestion:** Forces full-text string reading (`dtype=str`) on ingestion to completely prevent Excel / Pandas scientific notation and floating-point `inf` parsing bugs.
* **Auto-Delimiter Detection:** Automatically inspects incoming `.csv` files to detect whether fields are separated by commas, tabs, or semicolons.
* **Resilient Hex Decoding Engine:** Safely converts hex-encoded UTF-8 strings into plain text numbers and coordinates while gracefully preserving non-hex fallback values.
* **Dynamic Header Resolution:** Intelligently identifies and cleans truncated header names (e.g., `latitude_h` ➡️ `latitude`, `normal_th` ➡️ `normal_threshold`).
* **Dual Output Modes:**
  * **Option 1 (CSV ➡️ Clean CSV):** Produces a fully decoded, standardized CSV file with trailing zero cleanups (e.g., `1.9000` ➡️ `1.9`).
  * **Option 2 (CSV ➡️ SQL Dump):** Generates ready-to-execute MySQL/MariaDB database scripts with automatic schema generation (`CREATE TABLE` and formatted `INSERT` statements).

---

## 🚀 Getting Started

### Prerequisites

* Python 3.8 or higher
* Pandas

Install dependencies via terminal:
```bash
pip install pandas
