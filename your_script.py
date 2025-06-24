import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import time
import re

class FTHistoricalDataScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0',
            'Accept': 'text/html',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
    
    def get_historical_data(self, symbol, start_year, end_year):
        all_data = []
        for year in range(start_year, end_year + 1):
            start_date = f"{year}-01-01"
            end_date = f"{year}-12-31"
            url = f"https://markets.ft.com/data/etfs/tearsheet/historical?s={symbol}&startDate={start_date}&endDate={end_date}"
            try:
                response = self.session.get(url, timeout=30)
                print(f"[DEBUG] URL: {url}")
                print(f"[DEBUG] Status Code: {response.status_code}")
                print("[DEBUG] Response Preview:")
                print(response.text[:1000])

                soup = BeautifulSoup(response.content, 'html.parser')
                table = soup.find('table', {'class': 'mod-ui-table'})
                if table:
                    year_data = self.parse_table(table)
                    all_data.extend(year_data)
                else:
                    print(f"[DEBUG] No table found for year {year}")

                time.sleep(2)
            except Exception as e:
                print(f"[ERROR] Failed to fetch data for year {year}: {e}")
                continue

        if all_data:
            df = pd.DataFrame(all_data)
            df = df[df['Date'].str.len() >= 6]
            df = df[~df['Date'].str.contains("Date", case=False, na=False)]
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df = df.dropna(subset=['Date'])
            df = df.sort_values('Date', ascending=False)
            return df
        return pd.DataFrame()

    def parse_table(self, table):
        data = []
        rows = table.find_all('tr')
        headers = [th.get_text().strip() for th in rows[0].find_all('th')]
        for row in rows[1:]:
            cells = row.find_all('td')
            if len(cells) == len(headers):
                record = {headers[i]: cells[i].get_text(strip=True) for i in range(len(headers))}
                data.append(record)
        return data

    def save_to_excel(self, df, filename):
        try:
            with pd.ExcelWriter(filename, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='All Data', index=False)
                df['Year'] = df['Date'].dt.year
                for year in sorted(df['Year'].unique(), reverse=True):
                    df[df['Year'] == year].drop(columns='Year').to_excel(writer, sheet_name=f'Year {year}', index=False)
            return True
        except Exception as e:
            print(f"Error saving to Excel: {e}")
            return False
