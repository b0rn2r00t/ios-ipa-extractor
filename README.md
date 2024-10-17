# iOS IPA Extractor

![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)
![Python version](https://img.shields.io/badge/python-3.6%2B-blue)

## 📱 Extract IPA Files from iOS Devices Easily and Securely

The iOS IPA Extractor is a powerful, user-friendly Python script that allows you to extract IPA (iOS App Store Package) files directly from jailbroken iOS devices. This tool is perfect for app developers, security researchers, and iOS enthusiasts who need to analyze or backup iOS applications.

### 🌟 Key Features

- **Interactive SSH Connection**: Securely connect to your iOS device using SSH with interactive input.
- **Customizable Output**: Choose your preferred filename and location for extracted IPAs.
- **Interactive App Selection**: Choose from a list of installed applications.
- **Progress Visualization**: Real-time progress bars for extraction and download processes.
- **Automatic Cleanup**: Removes temporary files after successful extraction.
- **Cross-platform Compatibility**: Works on Windows, macOS, and Linux.

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- Jailbroken iOS device
- SSH access to the iOS device

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/b0rn2r00t/ios-ipa-extractor.git
   cd ios-ipa-extractor
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Usage

Run the script with the following command:

```
python ipa_extractor.py
```

Follow the interactive prompts to:
1. Enter your device's IP address and SSH port (default is 22)
2. Provide SSH username (default is 'root') and password
3. Select the app to extract
4. Choose output filename and location (or use defaults)

⚠️ This script is tested on iPhone X v16.0.3 only, issue might arise for different iOS version.

## 🛠 How It Works
1. **Connect**: The script establishes a secure SSH connection to your iOS device.
2. **List Apps**: It retrieves and displays a list of installed applications.
3. **Select App**: You choose which app's IPA you want to extract.
4. **Extract**: The script packages the selected app into an IPA file on the device.
5. **Download**: The IPA file is downloaded to your specified location with a progress bar.
6. **Cleanup**: Temporary files on the iOS device are removed automatically.

<img width="815" alt="01-Usage" src="https://github.com/user-attachments/assets/778c3f53-7b68-40df-8f05-16f248b2d022">

## 🔒 Security

The IPA Extractor script implements several security best practices:

- Uses paramiko for secure SSH connections with proper error handling.
- Implements input validation for IP addresses and port numbers.
- Utilizes secure random number generation for temporary file naming.
- Avoids command injection vulnerabilities by not using user input directly in system commands.
- Implements proper error handling and resource cleanup.
- Uses timeout mechanisms to prevent hanging on SSH operations.
- Securely handles file operations with appropriate permissions.
- Does not store or transmit device credentials beyond the current session.

While we strive to maintain high security standards, users should always exercise caution when using tools that interact with their devices. Ensure you're using this tool on devices you own or have permission to access.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/b0rn2r00t/ios-ipa-extractor/issues).

## 📜 License

This project is [MIT](https://choosealicense.com/licenses/mit/) licensed.

## 🙏 Acknowledgements

- [Paramiko](https://www.paramiko.org/) for SSH functionality
- [Rich](https://github.com/willmcgugan/rich) for beautiful terminal formatting

## 📞 Contact

B0rn2r00t - [@b0rn2r00t](https://x.com/b0rn2r00t)

Project Link: [https://github.com/b0rn2r00t/ios-ipa-extractor](https://github.com/b0rn2r00t/ios-ipa-extractor)

---

Keywords: iOS, IPA, extractor, jailbreak, SSH, Python, app extraction, iOS development, security research, app analysis, interactive CLI
