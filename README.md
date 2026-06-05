# 🚀 SemiContact Pro

### Advanced Semiconductor Contact Resistance Analysis Workstation

**CTLM • LTLM • TLM • Multi-Dataset Analysis • Publication-Ready Reports**

SemiContact Pro is a fully offline desktop application designed for semiconductor contact resistance characterization and analysis. It provides an integrated environment for CTLM and LTLM workflows, combining data processing, visualization, parameter extraction, and professional report generation within a single workstation.

---

## ✨ Key Features

* 📊 CTLM (Circular Transmission Line Method) Analysis
* 📈 LTLM (Linear Transmission Line Method) Analysis
* 📁 Multi-Dataset Support
* 🎨 Interactive Graph Customization
* 🌙 Modern Dark-Themed Scientific Workspace
* 📑 Automated PDF Report Generation
* 🖼️ High-Resolution PNG Export
* 📉 Residual Analysis & Deviation Visualization
* ⚡ Real-Time Parameter Extraction
* 💻 Fully Offline Desktop Application
* 📦 Windows Executable Build Support

---

## 🛠️ Technology Stack

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PyQt6-41CD52?style=for-the-badge&logo=qt&logoColor=white" />
  <img src="https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge" />
  <img src="https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white" />
  <img src="https://img.shields.io/badge/SciPy-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white" />
  <img src="https://img.shields.io/badge/ReportLab-FF6B35?style=for-the-badge" />
  <img src="https://img.shields.io/badge/PyInstaller-4B8BBE?style=for-the-badge" />
</p>
---

## ⚡ Quick Start

### Prerequisites

* Python 3.11+ (64-bit)
* Windows 10 / Windows 11

### Installation

```bash
# Clone the repository
git clone https://github.com/ishhh27/SemiContactPro.git

# Navigate to project directory
cd SemiContactPro

# Install dependencies
pip install -r requirements.txt

# Launch application
python main.py
```

---

## 🏗️ Build Windows Executable

```bash
build_exe.bat
```

Output:

```text
dist/SemiContactPro.exe
```

---

## 📂 Project Architecture

```text
SemiContactPro/
│
├── main.py
├── requirements.txt
├── SemiContactPro.spec
├── build_exe.bat
│
├── ui/
├── analysis/
├── graphs/
├── exports/
├── themes/
├── utils/
├── assets/
└── data/
```

---

## 🔬 Analysis Modes

### CTLM — Circular Transmission Line Method

| Parameter | Formula                 |
| --------- | ----------------------- |
| Rnew      | (R − Rp) / CF(d)        |
| RSH       | slope × 314             |
| LT        | intercept / (2 × slope) |
| Rc        | intercept / 2           |
| FOM       | Rc × 0.314              |

#### Correction Factors

| d (µm) | CF   |
| ------ | ---- |
| 4      | 0.96 |
| 8      | 0.93 |
| 12     | 0.90 |
| 24     | 0.82 |
| 32     | 0.77 |
| 40     | 0.73 |

---

### LTLM — Linear Transmission Line Method

| Parameter | Formula       |
| --------- | ------------- |
| Rnew      | R − Rp        |
| Rc        | intercept / 2 |
| RSH       | slope × W     |
| LT        | Rc / slope    |
| FOM       | Rc × 0.314    |

---

## 📑 Export Capabilities

### PNG Export

* High-resolution graph export
* Publication-ready visualization
* Theme-aware rendering

### PDF Export

Professional report generation including:

* Session metadata
* Wafer information
* Product details
* Embedded analysis graph
* Extracted parameter tables
* Input dataset tables
* Timestamped report generation

---

## 📊 Extracted Parameters

SemiContact Pro automatically computes:

| Parameter | Description          |
| --------- | -------------------- |
| Rc        | Contact Resistance   |
| RSH       | Sheet Resistance     |
| LT        | Transfer Length      |
| FOM       | Figure of Merit      |
| Slope     | Linear Fit Slope     |
| Intercept | Linear Fit Intercept |

---

## 🎯 Target Users

* Semiconductor Device Engineers
* Process Engineers
* Research Scientists
* Academic Laboratories
* University Researchers
* Materials Characterization Teams

---

## 👩‍💻 Author

### Isha Joshi

B.Tech Computer Science Engineering
Banasthali Vidyapith

Creator, Designer, and Developer of SemiContact Pro.

SemiContact Pro was conceived and developed as an original semiconductor characterization workstation focused on simplifying CTLM and LTLM analysis workflows through integrated visualization, automated parameter extraction, and publication-ready reporting.

GitHub: **@ishhh27**

---

## ⭐ Support

If you find this project useful, consider giving it a star on GitHub.
