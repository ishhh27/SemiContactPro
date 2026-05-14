# SemiContact Pro
### Semiconductor Contact Resistance Analysis Workstation  
*CTLM · LTLM · TLM — Fully Offline Desktop Application*

---

## Quick Start

### Prerequisites
- Python 3.11+ (64-bit)
- Windows 10 / 11

### Install & Run
```bash
# 1. Clone / extract the project
cd SemiContactPro

# 2. Install dependencies
pip install -r requirements.txt

# 3. Launch the application
python main.py
```

### Build Windows EXE
```bash
# Double-click or run from command prompt:
build_exe.bat

# Output: dist\SemiContactPro.exe
```

---

## Project Structure
```
SemiContactPro/
│
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── SemiContactPro.spec      # PyInstaller EXE build spec
├── build_exe.bat            # One-click Windows EXE builder
│
├── ui/
│   ├── splash.py            # Animated splash screen
│   ├── dashboard.py         # Landing dashboard (CTLM / LTLM selector)
│   ├── analysis_window.py   # Main 3-panel analysis workstation
│   ├── input_panel.py       # Left panel — dataset inputs
│   ├── output_panel.py      # Right panel — extracted parameter cards
│   └── data_table.py        # Centre-bottom — d/R/CF/Rnew data table
│
├── analysis/
│   ├── models.py            # AnalysisSession, Dataset, DataPoint
│   ├── ctlm_engine.py       # CTLM correction-factor + linear fit
│   └── ltlm_engine.py       # LTLM probe-correction + linear fit
│
├── graphs/
│   └── plot_canvas.py       # Matplotlib canvas (dark theme, multi-dataset)
│
├── exports/
│   └── exporter.py          # PNG and PDF export engine (ReportLab)
│
├── themes/
│   └── dark_theme.py        # Global Qt stylesheet
│
├── utils/
│   └── helpers.py           # fmt() / safe_float() utilities
│
├── assets/                  # Icons, images (add icon.ico for EXE)
└── data/                    # Reserved for saved session files
```

---

## Analysis Modes

### CTLM — Circular Transmission Line Method
| Parameter | Formula |
|-----------|---------|
| Rnew | `(R − Rp) / CF(d)` |
| RSH  | `slope × 314` |
| LT   | `intercept / (2 × slope)` |
| Rc   | `intercept / 2` |
| FOM  | `Rc × 0.314` |

**Correction Factors:**
| d (µm) | CF |
|--------|-----|
| 4  | 0.96 |
| 8  | 0.93 |
| 12 | 0.90 |
| 24 | 0.82 |
| 32 | 0.77 |
| 40 | 0.73 |

### LTLM — Linear Transmission Line Method
| Parameter | Formula |
|-----------|---------|
| Rnew | `R − Rp` |
| Rc   | `intercept / 2` |
| RSH  | `slope × W` |
| LT   | `Rc / slope` |
| FOM  | `Rc × 0.314` |

---

## Export
- **PNG** — high-resolution graph (200 dpi)
- **PDF** — full branded report including:
  - Session metadata (wafer, product, timestamp)
  - Embedded analysis graph
  - Extracted parameter table
  - Input data tables (per dataset)

---

## Dependencies
| Package | Purpose |
|---------|---------|
| PyQt6 | Desktop UI framework |
| matplotlib | Scientific graph plotting |
| numpy | Numerical arrays |
| scipy | Linear regression (`stats.linregress`) |
| reportlab | PDF report generation |
| Pillow | Image handling |
| pyinstaller | EXE packaging |
