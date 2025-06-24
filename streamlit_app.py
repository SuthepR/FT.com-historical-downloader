import streamlit as st
from your_script import FTHistoricalDataScraper

st.title("ETF Historical Data Downloader")

symbol = st.text_input("Enter ETF Symbol (e.g., EIMI:LSE:USD)", "EIMI:LSE:USD")
start_year = st.number_input("Start Year", value=2015, min_value=2000, max_value=2050)
end_year = st.number_input("End Year", value=2025, min_value=2000, max_value=2050)

if st.button("Download Historical Data"):
    with st.spinner("Fetching data..."):
        scraper = FTHistoricalDataScraper()
        df = scraper.get_historical_data(symbol, start_year, end_year)
        if not df.empty:
            filename = f"FT_Historical_Data_{symbol.replace(':', '_')}_{start_year}-{end_year}.xlsx"
            scraper.save_to_excel(df, filename)
            with open(filename, "rb") as f:
                st.download_button("📥 Download Excel File", f, file_name=filename)
        else:
            st.error("No data found or fetch failed.")
