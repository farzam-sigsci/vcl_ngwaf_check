# How to Run
- Follow these steps to run the fastly_vcl_ngwaf_checker.py_services.py script 

# Prerequisites
Python 3: Ensure Python 3 is installed. 
- Check with:
    - % python3 --version

# Dependencies: Install the required requests library:

   - % pip install requests

# Prepare the Config File
- Create a file named config.json in the same directory as the script.
>   - Add your API token and Customer ID:

>>      {
  >>        "api_token": "API Key",
  >>        "customer_id": "Customer ID"
>>      }

# Clone or Download the Script
>- Clone this repository or download fastly_vcl_ngwaf_checker.py_vcl_ngwaf_checker.py:

# Run the Script
   - Open a terminal in the script’s directory.
      - Execute:

 >>>>  % python3 fastly_vcl_ngwaf_checker_ver2.py

# Check the Output
- Console: Displays service details (Service ID, Name, Active Version, WAF Status) as the script runs.
   - Example output :

   >>Processing Service ID: SID Listed
   >>Service Name: service name
   >>Active VCL Version: 3
   >>WAF Status: ✅

# Reports
 - Report saved as: account_report_20231001_123456.csv
 - Fixed report saved as: cid_ngwaf_results.csv

# CSV Files:
- account_report_{timestamp}.csv (e.g., account_report_20231001_123456.csv):
   - Timestamped results for each run.
- cid_ngwaf_results.csv: Latest results, overwritten each run.
