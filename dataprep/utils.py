from docling.document_converter import DocumentConverter
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd
import os
import re

def extract_report(source):
    converter = DocumentConverter()
    result = converter.convert(source)
    try:
        # Extract image URLs
        response = requests.get(source)
        soup = BeautifulSoup(response.content, 'html.parser')
        image_urls = [img['src'] for img in soup.find_all('img') if 'src' in img.attrs]
    except:
        image_urls = []
    
    image_urls = "\n".join(image_urls)

    if image_urls:
        final_result = f"{result.document.export_to_markdown()}\n\n# Image URLs #\n\n{image_urls}"
    else:
        final_result = result.document.export_to_markdown()

    return final_result

def get_soup_object(url, use_table_counter=True):
    try:
        options = Options()
        #options.add_argument('--headless')  # Run in headless mode (no window)
        options.add_argument('--disable-gpu')
        
        # 1. Initialize Selenium WebDriver (adjust path to your webdriver)
        driver = webdriver.Chrome(options=options)  # Or any other browser driver
        
        # 2. Navigate to the webpage containing the table
        driver.get(url)

        if use_table_counter:

            # # 3. Locate the <select> element that controls the number of items
            # select_element = WebDriverWait(driver, 10).until(
            #     EC.presence_of_element_located((By.ID, "count"))  # Replace with the actual ID
            #     # Or use other locators like By.NAME, By.XPATH, By.CSS_SELECTOR
            # )

            select_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, "count"))
            )
            
            item_selector = Select(select_element)

            # 4. Select the desired number of items
            desired_item_count = "100"  # Replace with the value you want to select (e.g., "50", "All")
            item_selector.select_by_value(desired_item_count)  # Or select_by_visible_text() or select_by_index()

            # 5. Wait for the table to load/update after the selection (important!)
            WebDriverWait(driver, 10)
            # .until(
            #     EC.presence_of_element_located((By.XPATH, "//table[@id='your_table_id']/tbody/tr"))  # Adjust XPath to target a row in the table
            # )
            time.sleep(2)  # Add an extra small delay if needed for rendering

        # 6. Get the updated HTML source
        html_source = driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
    finally:
        # 8. Close the browser
        driver.quit()
    return soup

def extract_alienvault_report(url, use_table_counter=True):

    soup = get_soup_object(url, use_table_counter)
    
    # Get title
    title = soup.find("h1").get_text()

    # Get metadata
    metadata = soup.find("div", class_="pulse-meta").find('ul').get_text().strip()

    # Get contents
    contents = "\n\n".join(
        [tag.get_text().strip() for tag in soup.find("div", class_="pulse-general-details").find_all("div", class_="row col-md-12 col-flex detail-row ng-star-inserted")]
        )

    # Get table
    table_rows = soup.find("otx-table").find_all("tr")

    table_dict = {}
    for i, tr in enumerate(table_rows):
        if i==0:
            table_columns = []
            for tag in tr.find_all("div", class_="clickable"):
                table_dict.update({tag.get_text().strip():[]})
                table_columns.append(tag.get_text().strip())
        else:
            for j, tag in enumerate(tr.find_all("td", class_="ng-star-inserted")):
                k = table_columns[j]
                table_dict[k].append(tag.get_text().strip())

    if "" in table_dict.keys():
        table_dict.pop("")

    table_str = pd.DataFrame(table_dict).to_string(index=False, header=True, na_rep='--', col_space=2)

    alienvault_report = "# Title #\n{title}\n\n# Metadata #\n{metadata}\n\n# Contents #\n{contents}\n\n# Indicators of Compromise #\n{table}".format(
        title = title,
        metadata = metadata,
        contents = contents,
        table = table_str
    )
    return alienvault_report

def write_report(filepath, filename, data):
    with open(os.path.join(filepath, filename), mode="w", encoding="utf-8") as f:
        f.write(data)

def read_report(filepath, filename):
    with open(os.path.join(filepath, filename), mode="r", encoding="utf-8") as f:
        report = f.read()
    return report

def add_pictures_to_formatted_data(report_name, initial_data_path, formatted_data_path):

    unformatted_report = read_report(initial_data_path, report_name + ".txt")

    # Match text between <image>...</image>
    images = re.findall(r'(<image>.*?</image>)', unformatted_report, re.DOTALL)

    folderpath = os.path.join(formatted_data_path, report_name)
    formatted_report = read_report(folderpath, "report")

    if images:
        image_descs = "\n\n".join(images)

        formatted_report += f"### Image Descriptions ###\n\n\n{image_descs}"
    
    return formatted_report
        

def create_final_dataset(report_names, 
                         initial_data_path, 
                         formatted_data_path, 
                         alienvault_data_path, 
                         final_data_path):
    for rn in report_names:

        exist_unformatted = rn + ".txt" in os.listdir(initial_data_path)
        exist_formatted = rn in os.listdir(formatted_data_path)
        exist_alienvault = rn in os.listdir(alienvault_data_path)

        if exist_unformatted and exist_formatted:
            final_report = add_pictures_to_formatted_data(rn, initial_data_path, formatted_data_path)
        elif exist_formatted:
            folderpath = os.path.join(formatted_data_path, rn)
            final_report = read_report(folderpath, "report")
        elif exist_unformatted:
            final_report = read_report(initial_data_path, rn + ".txt")
        else:
            continue

        if exist_alienvault:
            folderpath = os.path.join(alienvault_data_path, rn)
            alienvault_report = read_report(folderpath, "report")
            final_report += f"\n\n\n{'#'*200}\n\n\n{alienvault_report}"

        write_report(final_data_path, rn + ".txt", final_report)