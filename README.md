# GitSimpleClient

This script automates the process of logging into GitHub, navigating to a specific repository, and downloading its ZIP archive. It utilizes Selenium WebDriver to interact with the GitHub website and BeautifulSoup for parsing HTML.

## Prerequisites

- Python 3.x
- Selenium WebDriver
- BeautifulSoup
- Chrome browser (for WebDriver)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/BSNIKYT/GitSimpleClient.git
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Ensure that you have provided your GitHub username and password in the `InitLogin` class initialization.
2. Run the script:
    ```bash
    python github_automation.py
    ```
3. The script will log in to GitHub using the provided credentials, navigate to the specified repository, and download its ZIP archive.

## Configuration

- The script can be customized to handle different login methods, such as two-factor authentication (2FA).
- Modify the `DownloadDriver` class to adjust the WebDriver download path and options.

## Contributors

- [BSNIKYT](https://github.com/BSNIKYT)

## License

This project is licensed under the [MIT License](LICENSE).
