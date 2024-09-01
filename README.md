# Hetzner Firewall IP Updater

This Python script automatically updates the Hetzner firewall rules to allow access from your current public IP address. It's designed to be run periodically (e.g., via a cron job) to ensure your Hetzner server's firewall always allows access from your current IP, which is particularly useful for users with dynamic IP addresses.

## Features

- Automatically detects your current public IP address
- Updates specified Hetzner firewall rules with the new IP
- Configurable via a JSON file
- Supports both .env file and OS environment variables for sensitive information
- Debug mode for detailed logging
- Optimized to only update when necessary, reducing API calls

## Prerequisites

- Python 3.6 or higher
- `requests` library
- `python-dotenv` library

## Installation

1. Clone this repository or download the script files.
2. Install the required Python libraries:

   ```
   pip install requests python-dotenv
   ```

3. Create a `config.json` file in the same directory as the script with the following structure:

   ```json
   {
       "rule_names": ["Allow SSH"],
       "debug": false
   }
   ```

   Adjust the `rule_names` array to include the names of the firewall rules you want to update.

4. Create a `.env` file in the same directory with your Hetzner API credentials:

   ```
   HETZNER_SERVER_ID=your_server_id
   HETZNER_API_USER=your_api_username
   HETZNER_API_PASSWORD=your_api_password
   ```

   Alternatively, you can set these as environment variables in your operating system.

## Usage

Run the script with:

```
python main.py
```

The script will:
1. Detect your current public IP address
2. Fetch the current firewall rules from Hetzner
3. Update the specified rules if your IP has changed
4. Apply the new rules via the Hetzner API

If `debug` is set to `true` in `config.json`, the script will output detailed information about its operations.

## Cron Job Setup

To run this script automatically, you can set up a cron job. Here's an example that runs the script every hour:

1. Open your crontab file:

   ```
   crontab -e
   ```

2. Add the following line (adjust the path to your script):

   ```
   */10 * * * * /usr/bin/python3 /path/to/your/main.py >> /path/to/logfile.log 2>&1
   ```

   This will run the script every hour and log the output to `logfile.log`.

## Security Considerations

- Keep your `.env` file and `config.json` secure and don't share them publicly.
- Ensure that the directory containing these files has appropriate permissions.
- Regularly rotate your Hetzner API credentials for enhanced security.

## Troubleshooting

- If you encounter any issues, set `"debug": true` in your `config.json` file to get more detailed output.
- Ensure that your Hetzner API credentials are correct and have the necessary permissions.
- Check that the firewall rule names in `config.json` match exactly with the names in your Hetzner firewall configuration.

## Contributing

Contributions, issues, and feature requests are welcome. Feel free to check issues page if you want to contribute.

## License

[MIT](https://choosealicense.com/licenses/mit/)