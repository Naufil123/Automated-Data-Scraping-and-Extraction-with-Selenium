from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import csv
import re


def scroll_to_element(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)


def scrape_and_write_to_file(driver, processed_emails, output_file):
    contact_tab_clicks = 0
    while True:
        email_elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//div[@class="zp_GRRim zp_CRz5O zp_oFG5l"]'))
        )
        for index, email_element in enumerate(email_elements):
            scroll_to_element(driver, email_element)
            email_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.XPATH, '//div[@class="zp_GRRim zp_CRz5O zp_oFG5l"]'))
            )
            email_element = email_elements[index]
            if email_element.text in processed_emails:
                continue
            driver.execute_script("arguments[0].click();", email_element)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'zp_w7a38')))
            personalize_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-cy="signal-based-personalization"]'))
            )
            personalize_button.click()
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            contact_tab = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, 'Contact'))
            )
            contact_tab.click()
            contact_tab_clicks += 1  # Increment the counter
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            html_source = driver.page_source
            soup = BeautifulSoup(html_source, 'html.parser')
            text_content = soup.get_text(strip=True)
            output_file.write(text_content + "\n")
            processed_emails.add(email_element.text)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)
        if contact_tab_clicks >= 10:
            break
def process_output_content(content):
    lines = content.split('\n')
    found_data = False
    data_list = []
    current_entry = {}
    for line in lines:
        if 'UniversityIndustry' in line:
            found_data = True
            continue
        if 'Name' in line and found_data:
            name_parts = line.split('Name')[1].split('Title')[0].strip().split()
            name = ' '.join(name_parts)
            current_entry = {'Name': name}
        if 'Title' in line and found_data:
            title = line.split('Title')[1].split('Duration')[0].strip()
            current_entry['Title'] = title
        if 'Company Description' in line and found_data:
            company_description = line.split('Company Description')[1].split('Professional Summary')[0].strip()
            first_four_words = ' '.join(company_description.split()[:4])
            current_entry['Company Name'] = first_four_words

        if 'To:' in line:
            found_data = False
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            file_path = r'C:\Users\HP\Desktop\Data Scrapping\output.txt'
            with open(file_path, 'r') as file:
                text = file.read()
                emails = re.findall(email_pattern, text)
                if emails:
                    print(f"Found emails in {file_path}:")
                    for email in emails:
                        print(email)
                        if current_entry:
                            current_entry['Email'] = email
                            data_list.append(current_entry.copy())
                        else:
                            print("No data in current_entry to attach the email.")
    return data_list
def write_to_csv(data_list):
    with open('final_result.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Name', 'Title', 'Company Name', 'Email']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            writer.writerow(data)
if __name__ == "__main__":
    login_email = 'awsdytu@getsingspiel.com'
    login_password = 'ss01730aa@@'
    target_url = 'https://app.apollo.io/#/emails?finderViewId=5a205be89a57e40c095e1d65'
    chrome_options = Options()
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(target_url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, 'email')))
    email_field = driver.find_element(By.NAME, 'email')
    password_field = driver.find_element(By.NAME, 'password')
    email_field.send_keys(login_email)
    password_field.send_keys(login_password)
    password_field.send_keys(Keys.RETURN)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
    print("Login successful")
    processed_emails = set()
    with open("output.txt", "a", encoding="utf-8") as output_file:
        try:
            scrape_and_write_to_file(driver, processed_emails, output_file)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            driver.quit()
    with open("output.txt", "r", encoding="utf-8") as output_file:
        content = output_file.read()
        print(f"Read content from the file:\n{content}")
    data_list = process_output_content(content)
    write_to_csv(data_list)
    print("Data written to final_result.csv")

