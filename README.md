# Auto Certificate Generation

An automated tool that uses Selenium to generate bulk certificates through Canva without requiring API access.

## Overview

This project automates the process of creating multiple certificates at once using Canva's bulk create feature. Since Canva doesn't provide a public API for this functionality, the tool uses Selenium to automate browser interactions, allowing you to generate certificates for a large number of recipients without manual intervention.

## Features

- Automates Canva login (supports both Google and Email authentication)
- Uploads CSV data containing certificate recipient information
- Maps CSV columns to Canva template elements
- Automatically triggers the bulk generation process
- Downloads all certificates as a single PDF file
- Supports handling of 2FA authentication when required

## Requirements

- Python 3.x
- Chrome browser
- Required Python packages (see requirements.txt):
  - python-dotenv
  - undetected-chromedriver
  - selenium

## Project Structure

- `src/main.py`: Core application file that handles the automation process
- `modular.py`: Alternative implementation with detailed logging
- `test.csv`: Sample CSV file with recipient data
- `requirements.txt`: Python dependencies
- `install_modules.sh`: Script to install required Python packages
- `run.sh`: Script to run the application
- `chrome/`: Contains Chrome browser and chromedriver executables
- `downloads/`: Default location for downloaded certificate PDFs
- `experimental/`: Contains experimental features (zenDriver.py)

## Setup

1. Install the required Python packages:
   ```
   ./install_modules.sh
   ```

2. Create a `.env` file with the following variables:
   ```
   EMAIL=your_canva_email
   PASSWORD=your_canva_password
   LINK_TO_CANVA_CERTIFICATE=https://canva.com/link/to/your/certificate/template
   CSV_FILE=path/to/your/csv/file
   ```

3. Prepare your CSV file with headers matching the mapping in the constants setup

## Usage

Run the application using:
```
./run.sh
```

Or directly with Python:
```
python src/main.py
```

For email login that requires OTP, the program will pause and prompt you to enter the code received via email.

## How It Works

1. The script uses undetected-chromedriver to launch a Chrome browser instance
2. It logs into Canva using your credentials
3. Navigates to your certificate template
4. Accesses the bulk creation tool
5. Uploads your CSV file with recipient data
6. Maps the CSV columns to the template fields (e.g., name)
7. Triggers the certificate generation process
8. Downloads the generated certificates as a PDF file

## Notes

- The Chrome browser will run visibly (not in headless mode) so you can monitor the process
- You may need to manually complete 2FA authentication if required by your Canva account
- The script includes waits and delays to accommodate Canva's page loading times
