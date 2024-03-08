import re

def find_emails_in_file(file_path):
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    
    with open(file_path, 'r') as file:
        text = file.read()
        emails = re.findall(email_pattern, text)
        
        if emails:
            print(f"Found emails in {file_path}:")
            for email in emails:
                print(email)
        else:
            print(f"No emails found in {file_path}.")

file_path = r'C:\Users\HP\Desktop\Data Scrapping\output.txt'
find_emails_in_file(file_path)
