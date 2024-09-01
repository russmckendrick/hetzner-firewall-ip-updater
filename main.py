import requests
import json
import os
from dotenv import load_dotenv

def load_env_variables():
    # First, try to load from .env file
    load_dotenv()

    # Define the variables we need
    variables = {
        "API_BASE_URL": "https://robot-ws.your-server.de",  # Default value
        "HETZNER_SERVER_ID": None,
        "HETZNER_API_USER": None,
        "HETZNER_API_PASSWORD": None
    }

    # Try to get each variable from .env or OS environment
    for var in variables:
        variables[var] = os.getenv(var) or variables[var]

    # Check if all required variables are set
    missing_vars = [var for var, value in variables.items() if value is None]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

    return variables

# Load configuration
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

def get_public_ip():
    response = requests.get("https://api.ipify.org?format=json")
    return response.json()["ip"]

def get_firewall_rules(env_vars):
    url = f"{env_vars['API_BASE_URL']}/firewall/{env_vars['HETZNER_SERVER_ID']}"
    response = requests.get(url, auth=(env_vars['HETZNER_API_USER'], env_vars['HETZNER_API_PASSWORD']))
    response.raise_for_status()
    return response.json()

def update_firewall_rules(current_rules, new_ip, rule_names):
    updated = False
    for rule in current_rules["firewall"]["rules"]["input"]:
        if rule["name"] in rule_names:
            if rule["src_ip"] != f"{new_ip}/32":
                rule["src_ip"] = f"{new_ip}/32"
                updated = True
    return current_rules, updated

def submit_firewall_rules(updated_rules, env_vars, debug):
    url = f"{env_vars['API_BASE_URL']}/firewall/{env_vars['HETZNER_SERVER_ID']}"
    
    # Prepare the form data
    data = {
        "server_ip": updated_rules["firewall"]["server_ip"],
        "server_number": updated_rules["firewall"]["server_number"],
        "status": updated_rules["firewall"]["status"],
        "filter_ipv6": str(updated_rules["firewall"]["filter_ipv6"]).lower(),
        "whitelist_hos": str(updated_rules["firewall"]["whitelist_hos"]).lower(),
        "port": updated_rules["firewall"]["port"],
    }

    # Add input rules
    for i, rule in enumerate(updated_rules["firewall"]["rules"]["input"]):
        for key, value in rule.items():
            if value is not None:
                data[f"rules[input][{i}][{key}]"] = value

    # Add output rules
    for i, rule in enumerate(updated_rules["firewall"]["rules"]["output"]):
        for key, value in rule.items():
            if value is not None:
                data[f"rules[output][{i}][{key}]"] = value

    if debug:
        print("Data to be sent:")
        print(json.dumps(data, indent=2))
    
    response = requests.post(url, auth=(env_vars['HETZNER_API_USER'], env_vars['HETZNER_API_PASSWORD']), data=data)
    
    if debug:
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
    
    response.raise_for_status()
    return response.json()

def main():
    try:
        # Load environment variables
        env_vars = load_env_variables()

        # Load configuration
        config = load_config()
        rule_names = config["rule_names"]
        debug = config["debug"]

        # Get current public IP
        current_ip = get_public_ip()
        print(f"Current public IP: {current_ip}")

        # Get current firewall rules
        current_rules = get_firewall_rules(env_vars)
        if debug:
            print("Current firewall rules:")
            print(json.dumps(current_rules, indent=2))

        # Update firewall rules
        updated_rules, rules_changed = update_firewall_rules(current_rules, current_ip, rule_names)
        
        if rules_changed:
            # Submit updated rules
            result = submit_firewall_rules(updated_rules, env_vars, debug)
            print("Firewall rules updated successfully!")
            if debug:
                print("Updated firewall rules:")
                print(json.dumps(result, indent=2))
        else:
            print("No update needed. Current IP already matches firewall rules.")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        if debug and hasattr(e, 'response') and e.response is not None:
            print(f"Response status code: {e.response.status_code}")
            print(f"Response content: {e.response.text}")
    except json.JSONDecodeError as e:
        print(f"Error reading config file: {e}")
    except FileNotFoundError:
        print("config.json file not found. Please make sure it exists in the same directory as the script.")
    except KeyError as e:
        print(f"Missing key in config file: {e}")
    except EnvironmentError as e:
        print(f"Environment error: {e}")

if __name__ == "__main__":
    main()