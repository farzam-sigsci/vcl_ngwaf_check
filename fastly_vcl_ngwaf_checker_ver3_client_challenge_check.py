#!/usr/bin/env python3
import requests
import json
import sys
import csv
import re
from datetime import datetime

# Fastly API base URL for robust and efficient API interactions
FASTLY_API_URL = "https://api.fastly.com"

def load_config(config_file="config.json"):
    """Load API token and Customer ID from configuration file with secure error handling."""
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        api_token = config.get("api_token")
        customer_id = config.get("customer_id")
        if not api_token or not customer_id:
            raise ValueError("API token or Customer ID missing in config.json")
        return api_token, customer_id
    except (FileNotFoundError, json.JSONDecodeError, ValueError) as e:
        print(f"Error: {e}")
        sys.exit(1)

def make_api_request(endpoint, api_token):
    """Execute a GET request to the Fastly API with comprehensive error handling."""
    headers = {"Fastly-Key": api_token, "Accept": "application/json"}
    url = f"{FASTLY_API_URL}{endpoint}"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        print(f"API call to {url} succeeded (Status: {response.status_code})")
        return response.json(), response.status_code
    except requests.RequestException as e:
        print(f"API Request Failed: {e}")
        if e.response:
            print(f"Response text: {e.response.text}")
        return None, getattr(e.response, 'status_code', None)

def get_services(api_token, customer_id):
    """Retrieve all services for a Customer ID with efficient pagination."""
    base_endpoint = f"/services?filter[customer_id]={customer_id}"
    all_services = []
    page = 1
    total_expected = 468  # Adjust based on API metadata or dynamic fetching
    while len(all_services) < total_expected:
        endpoint = f"{base_endpoint}&page[number]={page}&page[size]=100"
        services, status_code = make_api_request(endpoint, api_token)
        if not services or status_code != 200:
            print(f"Failed to fetch services page {page} (Status: {status_code})")
            break
        data = services.get("data", []) if isinstance(services, dict) else services
        all_services.extend(data)
        print(f"Fetched {len(data)} services from page {page} (Total so far: {len(all_services)})")
        if len(data) < 100:  # Last page
            break
        page += 1
    print(f"Total services found: {len(all_services)}")
    return all_services

def get_service_details(api_token, service_id):
    """Fetch service details, including active VCL version, with clear logging."""
    endpoint = f"/service/{service_id}/details"
    details, status_code = make_api_request(endpoint, api_token)
    if details and status_code == 200:
        active_version = details.get("active_version", {})
        version_number = str(active_version.get("number", "None")) if isinstance(active_version, dict) else str(active_version or "None")
        return {"name": details.get("name", "Unnamed Service"), "active_version": version_number}
    print(f"  Failed to retrieve details for Service ID: {service_id} (Status: {status_code}) - Response: {details}")
    return {"name": "Unnamed Service", "active_version": "Unknown"}

def check_snippet(api_token, service_id, version, snippet_name="ngwaf_config_init"):
    """Verify the presence of a specific VCL snippet, ensuring accurate NGWAF configuration checks."""
    endpoint = f"/service/{service_id}/version/{version}/snippet/{snippet_name}"
    response, status_code = make_api_request(endpoint, api_token)
    if status_code == 200:
        return "✅"
    elif status_code == 404:
        return "❌"
    else:
        return f"Error: {response or 'Unknown'} (Status: {status_code})"

def check_client_challenge(api_token, service_id, version):
    """Inspect the entire VCL configuration for 'pragma optional_param client_challenge_enabled true;' in main or compiled VCL."""
    exact_match = "pragma optional_param client_challenge_enabled true;"
    pattern = r'pragma\s+optional_param\s+client_challenge_enabled\s+true\s*(?:;)?'

    # Check all VCL files (main and snippets)
    vcl_endpoint = f"/service/{service_id}/version/{version}/vcl"
    vcl_data, vcl_status = make_api_request(vcl_endpoint, api_token)
    if vcl_status == 200:
        if isinstance(vcl_data, list):
            if not vcl_data:
                print(f"  Warning: Empty VCL response for Service ID: {service_id}, Version: {version}")
            for vcl in vcl_data:
                content = vcl.get("content", "")
                if exact_match in content:
                    print(f"  Client Challenge Enabled found in Service ID: {service_id}, Version: {version}, VCL: {vcl.get('name')} (Exact match)")
                    print(f"    Matched content: {exact_match}")
                    return True
                if re.search(pattern, content, re.IGNORECASE):
                    print(f"  Client Challenge Enabled found in Service ID: {service_id}, Version: {version}, VCL: {vcl.get('name')} (Regex match)")
                    print(f"    Matched content: {content.strip()[:100]}...")
                    return True
        else:
            print(f"  Unexpected VCL response format for Service ID: {service_id}, Version: {version}: {vcl_data}")
    else:
        print(f"  Failed to retrieve VCL for Service ID: {service_id}, Version: {version} (Status: {vcl_status}) - Response: {vcl_data}")

    # Fallback: Check compiled VCL
    generated_vcl_endpoint = f"/service/{service_id}/version/{version}/generated_vcl"
    generated_vcl_data, generated_vcl_status = make_api_request(generated_vcl_endpoint, api_token)
    if generated_vcl_status == 200 and isinstance(generated_vcl_data, dict):
        content = generated_vcl_data.get("content", "")
        if exact_match in content:
            print(f"  Client Challenge Enabled found in Service ID: {service_id}, Version: {version}, Generated VCL (Exact match)")
            print(f"    Matched content: {exact_match}")
            return True
        if re.search(pattern, content, re.IGNORECASE):
            print(f"  Client Challenge Enabled found in Service ID: {service_id}, Version: {version}, Generated VCL (Regex match)")
            print(f"    Matched content: {content.strip()[:100]}...")
            return True
        print(f"  Client Challenge Enabled NOT found in Service ID: {service_id}, Version: {version} (Generated VCL)")
        print(f"    Generated VCL content inspected: {content[:100]}...")
    else:
        print(f"  Failed to retrieve Generated VCL for Service ID: {service_id}, Version: {version} (Status: {generated_vcl_status}) - Response: {generated_vcl_data}")

    print(f"  Client Challenge Enabled NOT found in Service ID: {service_id}, Version: {version}")
    return False

def main():
    """Main function to audit NGWAF snippets and client challenge settings across all services."""
    api_token, customer_id = load_config()
    print(f"Analyzing services for Customer ID: {customer_id}")

    services = get_services(api_token, customer_id)
    if not services:
        print("No services found or API request failed.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"account_report_{timestamp}.csv"
    fixed_report_file = "cid_ngwaf_results.csv"

    # Exceptional CSV reporting structure for precise, actionable security insights
    for filename in [report_file, fixed_report_file]:
        with open(filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Service Name", "Service ID", "Active Version", "WAF Status", "Client Challenge Enabled"])

            for service in services:
                service_id = service.get("id")
                if not service_id:
                    print(f"Skipping service with no ID: {service}")
                    continue

                print(f"\nProcessing Service ID: {service_id}")
                details = get_service_details(api_token, service_id)
                service_name = details["name"]
                active_version = details["active_version"]

                print(f"  Service Name: {service_name}")
                print(f"  Active VCL Version: {active_version}")

                waf_status = "No active version"
                client_challenge_enabled = False
                if active_version and active_version != "None" and active_version != "Unknown":
                    waf_status = check_snippet(api_token, service_id, active_version)
                    client_challenge_enabled = check_client_challenge(api_token, service_id, active_version)

                print(f"  WAF Status: {waf_status}")
                print(f"  Client Challenge Enabled: {client_challenge_enabled}")
                writer.writerow([service_name, service_id, active_version, waf_status, str(client_challenge_enabled)])

    print(f"\nComprehensive audit report saved as: {report_file}")
    print(f"Consolidated report saved as: {fixed_report_file}")

if __name__ == "__main__":
    main()
