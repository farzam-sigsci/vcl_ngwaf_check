How to Run
Follow these steps to run the fastly_vcl_ngwaf_checker.py_services.py script and check your fastly_vcl_ngwaf_checker.py services for the ngwaf_config_init snippet.

Prerequisites
Python 3: Ensure Python 3 is installed. Check with:

python3 --version
Dependencies: Install the required requests library:

pip install requests
Steps
Prepare the Config File
Create a file named config.json in the same directory as the script.
Add your fastly_vcl_ngwaf_checker.py API token and Customer ID:

{
    "api_token": "Ey7XfWFY007M3Tn2QZCRg-foo",
    "customer_id": "54Uvll8vVLQeqXODMD8k6d"
}
Replace "Ey7XfWFY00073Tn2QZCRg-foo" with your actual fastly_vcl_ngwaf_checker.py API token (must have global:read scope or equivalent).
Clone or Download the Script
Clone this repository or download fastly_vcl_ngwaf_checker.py_vcl_ngwaf_checker.py:

git clone <repository-url>
cd <repository-directory>
Run the Script
Open a terminal in the script’s directory.
Execute:

python3 fastly_vcl_ngwaf_checker.py_services.py

Check the Output
Console: Displays service details (Service ID, Name, Active Version, WAF Status) as the script runs.

Checking Customer ID: 54Uvll8vVLQeqXODMD8k6d

Processing Service ID: 8gWaTOqVyDZofjEA52HIE2
  Service Name: EdgeNGWAF33
  Active VCL Version: 3
  WAF Status: ✅

Report saved as: account_report_20231001_123456.csv
Fixed report saved as: cid_ngwaf_results.csv
CSV Files:
account_report_{timestamp}.csv (e.g., account_report_20231001_123456.csv): Timestamped results for each run.
cid_ngwaf_results.csv: Latest results, overwritten each run.

Service Name,Service ID,Active Version,WAF Status
EdgeNGWAF33,8gWaTOqVyDZofjEA52HIE2,3,✅
