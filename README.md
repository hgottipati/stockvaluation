# Tesla Stock Valuation Simulator

This is an interactive Streamlit app to simulate Tesla's future stock valuation based on customizable assumptions. Adjust the inputs in the sidebar and see how the valuation changes for 2025 and 2035.

## Features
- Adjust assumptions for each product line (Cars, Robotaxi, Optimus, Energy, Services)
- Customize Robotaxi Network parameters
- Toggle advanced calculations
- View results for 2025 and 2035
- Download results as CSV or JSON (optional)

## How to Use
1. Clone this repository:
   ```bash
   git clone https://github.com/hgottipati/stockvaluation.git
   cd stockvaluation
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run streamlit_app.py
   ```
4. Open the local URL (usually http://localhost:8501) in your browser.

## Deploy on Streamlit Community Cloud
1. Push your code to GitHub (already done if you're here!)
2. Go to [https://streamlit.io/cloud](https://streamlit.io/cloud)
3. Click "New app", select this repo, and set the main file to `streamlit_app.py`
4. Click "Deploy" and share your app's public link!

## Example
![screenshot](screenshot.png)

---

**Author:** [hgottipati](https://github.com/hgottipati) 