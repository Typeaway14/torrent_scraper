import sys
import time
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from textual.app import App, ComposeResult
from textual.widgets import Static, DataTable
from textual import events
from rich.table import Table


def get_working_url(driver):
    driver.get("https://piratebayproxy.net/")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME,'hscroll')))

    rows = driver.find_elements(By.XPATH, "//table/tbody/tr/td[contains(@class, 'tableurl')]")
    hrefs = []
    for row in rows:
        link_element = row.find_element(By.TAG_NAME, "a")
        href = link_element.get_attribute("href")
        hrefs.append(href)
    working_hrefs=[]
    for href in hrefs:
        try:
            result = subprocess.run(['curl', '-Is', href], capture_output=True, text=True)
            if result.returncode == 0 and '200' in result.stdout:
                working_hrefs.append(href)
        except Exception as e:
            print("Exception has occured")
    
    return working_hrefs


search_term = input("Enter search term:\n")

options = Options()
options.add_argument('--headless')
try:
    driver = webdriver.Firefox(options=options)
except:
    print("Driver failed to init")
    sys.exit(1)

print("Got firefox driver")

urls = get_working_url(driver)
print(f"Got working urls:\n{urls}")

if not urls:
    print("No url work L")
    sys.exit(1)

driver.get(urls[0])

#Default uses only first one. Cant be bothered checking for all links bruh
wait = WebDriverWait(driver, 5)

try:
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'https_form')))
    search_bar = driver.find_element(By.CLASS_NAME, "https_form")
    search_bar.clear()
    search_bar.send_keys(search_term)  
except TimeoutException:
    print("Search bar not found")
    driver.quit()
    sys.exit(1)

try:
    search_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="submit"][value="Pirate Search"]')))
    search_button.click()  
except TimeoutException:
    print("Search button not found ")
    driver.quit()
    sys.exit(1)

try:
    table = wait.until(EC.presence_of_element_located((By.ID, 'searchResult')))
except TimeoutException:
    print("Search result table ")
    driver.quit()
    sys.exit(1)

try:
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')
    top_10_rows_data = []
    for row in rows[:10]:
        det_link = row.find_element(By.CSS_SELECTOR, 'a.detLink')
        href = det_link.get_attribute('href')
        title = det_link.get_attribute('title').replace('Details for ', '')
        det_desc = row.find_element(By.CSS_SELECTOR, 'font.detDesc').text
        seeders = row.find_elements(By.TAG_NAME, 'td')[-2].text
        leechers = row.find_elements(By.TAG_NAME, 'td')[-1].text

        try:
            magnet_link = row.find_element(By.CSS_SELECTOR, 'a[href^="magnet:?"]').get_attribute('href')
        except:
            magnet_link = "No magnet link found"
        
        det_desc = det_desc.split(',')
        udate = det_desc[0][8:]
        size = det_desc[1][5:]
        uploader = det_desc[2][8:]
        row_data = {
            'href': href,
            'title': title,
            'size':size,
            'udate':udate,
            'uploader': uploader,
            'seeders': seeders,
            'leechers': leechers,
            'magnet_link': magnet_link
        }
        
        top_10_rows_data.append(row_data)

    driver.quit()
except:
    print("Error has arrived woops")
    sys.exit(1)


class TorrentTUI(App):
    def compose(self) -> ComposeResult:
        table_widget = DataTable(id="torrent_table")
        self.set_data_table(table_widget)
        yield table_widget

    def set_data_table(self, table_widget):
        table_widget.add_columns("Name", "Seeders", "Leechers", "Size", "UDate","Uploader")
        
        for row in top_10_rows_data:
            table_widget.add_row(row['title'], row['seeders'], row['leechers'], row['size'],row['udate'],row['uploader'])
        
        table_widget.cursor_type = "row"
        table_widget.focus()

    async def on_key(self, event: events.Key) -> None:
        selected_row_index = self.query_one("#torrent_table").cursor_row
        selected_row = top_10_rows_data[selected_row_index]
        if event.key == "enter":
            subprocess.Popen(['xdg-open',selected_row['magnet_link']])
            sys.exit(0)  
        elif event.key == "o":
            subprocess.Popen(['firefox',selected_row['href']])
            sys.exit(0)  


if __name__ == "__main__":
    TorrentTUI().run()

