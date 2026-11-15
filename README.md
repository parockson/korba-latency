# Korba Latency — Transaction Turnaround & Latency Analytics

An enterprise-grade transaction turnaround and latency intelligence platform built with **Streamlit**, **Pandas**, and **Plotly**. Designed to evaluate payment completion speed, gateway latency, SLA compliance, and reconciliation impact across millions of transaction records.

---

## ⚡ Overview & Objective

In digital payment platforms, knowing **how long it takes to complete a transaction** is critical for maintaining SLA commitments, identifying sluggish third-party gateways, and evaluating customer experience.

This project ingests multi-batch transaction datasets, calculates true turnaround latency directly from timestamp deltas (`Time Completed - Time Created`), isolates in-flight transactions to protect SLA accuracy, and provides deep visual analytics across clients, response codes, and reconciliation workflows.

---

## 🚀 Key Features

* **Dynamic Multi-Batch Ingestion**: Automatically detects and consolidates all partitioned CSV files located in `data/` (`set1.csv`, `set2.csv`, `set3.csv`, etc.) into a unified DataFrame.
* **Granular Duration Banding**: Categorizes turnaround latency into user-defined operational brackets:
  * `1-5 seconds`
  * `6-10 seconds`
  * `11-15 seconds`
  * `16-20 seconds`
  * `21-25 seconds`
  * `26-30 seconds`
  * `Above 30 seconds`
* **Strict Resolution Separation**: In-flight `pending` records are tracked in isolation, ensuring completion velocity curves, success rates, and failure analyses exclusively reflect terminal outcomes (`success` vs `failed`).
* **7 Comprehensive Analytics Views**:
  1. **Turnaround & SLA Overview**: Empirical Cumulative Distribution Function (CDF), P50/P75/P90 percentile thresholds, and SLA compliance metrics.
  2. **Duration Bands Deep Dive**: Volume distributions, success vs failure breakdowns, and 100% normalized resolution proportions per duration band.
  3. **Gateway Speed Ranking**: Fast-track vs bottleneck gateway leaderboards with average/median latency benchmarks and failure correlations.
  4. **Client & Merchant Analysis**: Transaction turnaround SLA, volume, and failure rates across 98 client accounts.
  5. **Daily Completion Trends**: Time-series tracking of transaction throughput, daily median latency shifts, and long-tail delay spikes.
  6. **Recon Action Impact**: Detailed statistical assessment (Min, Median, Mean, Max, Std Dev, and Count) of turnaround times across various reconciliation actions.
  7. **Transaction Explorer & Latency Extrema**:
     * **Top 100 Fastest Transactions**: Sub-millisecond to ~1.4 ms completions with 100% success rate.
     * **Top 100 Slowest Transactions**: Extreme latency outliers (4.2 days to 104.4 days) highlighting delayed reconciliation and gateway timeout sweeps.
     * **Custom Explorer**: Search by ID, sort by duration/amount, and export filtered extracts to CSV.

---

## 📦 Data Sources & Git Large File Storage (Git LFS)

The transaction datasets (`data/set1.csv`, `data/set2.csv`, `data/set3.csv`) exceed standard Git file size limits (~135 MB each, totaling over 3.1 million records). These files are managed and tracked using **Git LFS**.

To clone the repository and retrieve the dataset files:

```bash
# 1. Install Git LFS
git lfs install

# 2. Clone the repository
git clone https://github.com/parockson/korba-latency.git
cd korba-latency

# 3. Pull LFS data objects
git lfs pull
```

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.10 or higher
* Git and Git LFS

### Setup Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On macOS/Linux:
source venv/bin/activate

# Install required dependencies
pip install -r requirements.txt
```

---

## 🖥️ Running the Application

### 1. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
Open your browser and navigate to `http://localhost:8501`.

### 2. Run the Jupyter Notebook
For interactive exploratory data analysis and script prototyping:
```bash
jupyter notebook workbook.ipynb
```

---

## 📂 Repository Structure

```
korba-latency/
├── data/                       # Transaction dataset partitions (Tracked with Git LFS)
│   ├── set1.csv
│   ├── set2.csv
│   └── set3.csv
├── .gitattributes              # Git LFS tracking rules
├── .gitignore                  # Git ignore rules for environments and temporary files
├── app.py                      # Main Streamlit analytics application
├── requirements.txt            # Python dependencies
├── workbook.ipynb              # Jupyter notebook with end-to-end data processing
├── LICENSE                     # MIT License
└── README.md                   # Project documentation
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

