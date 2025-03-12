#!/usr/bin/env python3
import requests
import json
import sys
import csv
from datetime import datetime

# Base URL for Fastly API
FASTLY_API_URL = "https://api.fastly.com"

# Load configuration from config.json
def load_config(config_file="config.json"):
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        api_token = config.get("api_token")
        customer_id = config.get("customer_id")
        if not api_token or not customer_id:
            raise ValueError("API token or Customer ID missing in config.json")
        return api_token, customer_id
    except FileNotFoundError:
        print(f"Error: Config file '{config_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in '{config_file}'.")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

# Make an authenticated API request
def make_api_request(endpoint, api_token):
    headers = {
        "Fastly-Key": api_token,
        "Accept": "application/json"
    }
    url = f"{FASTLY_API_URL}{endpoint}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json(), response.status_code
    except requests.RequestException as e:
        print(f"API Request Failed: {e}")
        return None, getattr(e.response, 'status_code', None)

# Get all services for a customer
def get_services(api_token, customer_id):
    endpoint = f"/services?filter[customer_id]={customer_id}"
    services, status_code = make_api_request(endpoint, api_token)
    if services is None:
        print(f"Failed to fetch services (Status: {status_code})")
        return []
    if isinstance(services, dict):
        return services.get("data", [])
    elif isinstance(services, list):
        return services
    else:
        print(f"Unexpected response format from {endpoint}: {services}")
        return []

# Get service details (active version and name)
def get_service_details(api_token, service_id):
    endpoint = f"/service/{service_id}/details"
    details, status_code = make_api_request(endpoint, api_token)
    if details and status_code == 200:
        active_version = details.get("active_version", {})
        version_number = str(active_version.get("number", "None")) if isinstance(active_version, dict) else str(active_version or "None")
        return {
            "name": details.get("name", "Unnamed Service"),
            "active_version": version_number
        }
    print(f"  Failed to retrieve details for Service ID: {service_id} (Status: {status_code})")
    return {"name": "Unnamed Service", "active_version": "Unknown"}

# Check for a specific snippet
def check_snippet(api_token, service_id, version, snippet_name="ngwaf_config_init"):
    endpoint = f"/service/{service_id}/version/{version}/snippet/{snippet_name}"
    response, status_code = make_api_request(endpoint, api_token)
    if status_code == 200:
        return "✅"
    elif status_code == 404:
        return "❌"
    else:
        return f"Error: {response or 'Unknown'} (Status: {status_code})"

# Main function
def main():
    api_token, customer_id = load_config()
    print(f"Checking Customer ID: {customer_id}")

    services = get_services(api_token, customer_id)
    if not services:
        print("No services found or API request failed.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"account_report_{timestamp}.csv"
    fixed_report_file = "cid_ngwaf_results.csv"

    # Write to both CSV files
    for filename in [report_file, fixed_report_file]:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Service Name", "Service ID", "Active Version", "WAF Status"])

            for service in services:
                service_id = service.get("id")
                if not service_id:
                    continue

                print(f"\nProcessing Service ID: {service_id}")

                details = get_service_details(api_token, service_id)
                service_name = details["name"]
                active_version = details["active_version"]

                print(f"  Service Name: {service_name}")
                print(f"  Active VCL Version: {active_version}")

                waf_status = "No active version"
                if active_version and active_version != "None" and active_version != "Unknown":
                    waf_status = check_snippet(api_token, service_id, active_version)

                print(f"  WAF Status: {waf_status}")

                writer.writerow([service_name, service_id, active_version, waf_status])

    print(f"\nReport saved as: {report_file}")
    print(f"Fixed report saved as: {fixed_report_file}")

if __name__ == "__main__":
    main()
