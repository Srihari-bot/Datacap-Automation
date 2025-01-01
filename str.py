# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 10:33:19 2024

@author: SBA
"""

#-------------------------------------------------------------------------------

import requests
import os
import time
import xml.etree.ElementTree as ET
import sys

# Start a session to persist cookies
session = requests.Session()

# Logon Request
url = "http://localhost:82/service/Session/Logon"
payload = """<LogonProperties>
  <application>text</application>
  <password>admin</password>
  <station>1</station>
  <user>admin</user>
</LogonProperties>"""
headers = {
  'Content-Type': 'application/xml',
}

response = session.post(url, headers=headers, data=payload)

# Check if login was successful
if response.status_code == 200:
    print("Login successful")
    print(response.text)
else:
    print(f"Login failed with status code {response.status_code}")
    sys.exit(1)  # Exit if login failed

time.sleep(5)

#-------------------------------------------------------------------------------

# Create Batch Request
url = "http://localhost:82/service/Queue/CreateBatch"
payload = """<createBatchAttributes>
    <application>text</application>
    <job>Demo_MultiFormat</job>
</createBatchAttributes>"""
headers = {
  'Content-Type': 'application/xml',
}

response = session.post(url, headers=headers, data=payload)

# Check if batch creation was successful
if response.status_code == 201:  # 201 Created status code
    print("Batch created successfully")
else:
    print(f"Batch creation failed with status code {response.status_code}")
    sys.exit(1)  # Exit if batch creation failed

# Parse the response XML and extract Queue ID
response_xml_as_string = response.text
root = ET.fromstring(response_xml_as_string)
queueId_element = root.find(".//queueId")  # Adjusted based on your response structure
queueId = queueId_element.text if queueId_element is not None else None

batchId = root.find(".//batchId")
print(batchId)

if queueId:
    print(f"Queue ID: {queueId}")
else:
    print("Queue ID not found in response")
    sys.exit(1)  # Exit if Queue ID is not found

time.sleep(5)

#-------------------------------------------------------------------------------

# Upload Files (Automatically load all PDFs from the 'tifimages' folder)
url3 = "http://localhost:82/service/Queue/UploadFile/text/"+queueId
print(f"Uploading files to {url3}")

base_dir = os.getcwd()

#-------------------------------------------------------------------------------

tifimages_dir = os.path.join("C:\\Datacap\\text\\images\\Input_MultiFormat\\")



# Loop through all files in the tifimages directory
for filename in os.listdir(tifimages_dir):
    # Check if the file is a PDF
    print(filename)
    if filename.lower().endswith(".pdf"):
        # Full path to the file
        filepath = os.path.join(tifimages_dir, filename)
        print(f"Uploading {filepath}...")
        
        # Open the PDF file in binary mode
        with open(filepath, 'rb') as file:
            files = {'file': (filename, file, 'application/pdf')}
            
            # Sending POST request with the file
            response3 = session.post(url3, files=files)

            # Check if file upload was successful
            if response3.status_code == 200 or response3.status_code == 201:
                print(f"File {filename} uploaded successfully")
            else:
                print(f"File {filename} upload failed with status code {response3.status_code}")
        print(filename)

time.sleep(5)

#-------------------------------------------------------------------------------

# Replace hardcoded 39 with actual queueId
url = "http://localhost:82/service/Queue/ReleaseBatch/text/"+queueId+"/finished"


# Debugging: Print out the URL to ensure it's correctly formatted
print(f"Releasing batch with URL: {url}")

# Make the PUT request to release the batch
response = session.put(url)

# Check if batch release was successful
if response.status_code == 200:
    print("Batch released successfully")
else:
    print(f"Batch release failed with status code {response.status_code}")
    print("Server Response:", response.text)  # Print the server's response for further debugging
    sys.exit(1)  # Exit if batch release failed
