Music Rights Analysis System
An automated system that cross-references artist music catalogs from Spotify with unclaimed musical works data to identify potential rights management issues and missing royalty claims.

🎯 Overview
This project analyzes music rights data by:

Processing large datasets of unclaimed musical works

Integrating with Spotify API to retrieve artist catalogs

Matching ISRC codes to identify potential unclaimed works

Generating professional Excel reports with analysis results

🚀 Features
Large Data Processing: Handles 7.2GB+ TSV files efficiently

Spotify API Integration: Retrieves artist catalogs with ISRC codes

Intelligent Matching: Cross-references datasets using ISRC codes

Professional Reporting: Generates multi-sheet Excel reports

Multi-Artist Support: Batch processing for multiple artists

Error Resilience: Robust error handling and rate limiting

🛠️ Installation
Prerequisites
Python 3.8+

Spotify Developer Account

Dependencies
bash
pip install pandas requests openpyxl
Spotify API Setup
Create a Spotify Developer account at Spotify Developer Dashboard

Create a new app and get your Client ID and Client Secret

Update the credentials in the code:

python
CLIENT_ID = "your_spotify_client_id"
CLIENT_SECRET = "your_spotify_client_secret"
📁 Project Structure
text
Music-Rights-Analysis/
├── main.py                 # Main analysis script
├── requirements.txt        # Project dependencies
├── README.md              # Project documentation
├── samples/               # Example outputs
│   ├── The_Weeknd_analysis.xlsx
│   └── Taylor_Swift_analysis.xlsx
└── docs/                  # Additional documentation
    └── technical_specs.md
🎵 Usage
Basic Analysis
python
# Run the main analysis
python main.py
The system will:

Load the unclaimed works dataset

Authenticate with Spotify API

Analyze The Weeknd's catalog

Generate Excel report with results

Custom Artist Analysis
Modify the main() function in main.py to analyze different artists:

python
# Change this line to analyze different artists
artist = search_artist(token, "Artist Name Here")
📊 Output
The system generates Excel reports with three sheets:

Artist Catalog: Complete track list with ISRC codes

Matches: Any identified unclaimed works

Process Notes: Technical details and analysis summary

Sample Output Structure
text
The_Weeknd_analysis.xlsx
├── Artist_Catalog (Sheet 1)
├── Matches (Sheet 2) 
└── Process_Notes (Sheet 3)
🔧 Technical Details
Data Processing
Processes 50,000+ records with memory optimization

Handles TSV files with comment headers

Validates ISRC code formats

Implements efficient dictionary lookup

API Integration
Uses Spotify Web API with Client Credentials flow

Implements rate limiting (0.1s between requests)

Handles authentication errors gracefully

Retrieves top tracks with ISRC codes

Matching Algorithm
Exact ISRC code matching between datasets

Case-insensitive comparison

Handles missing/invalid ISRC codes

Batch processing capability

📈 Results Interpretation
Matches Found: Potential unclaimed works requiring verification

Zero Matches: Proper rights management (common for mainstream artists)

Partial Matches: May indicate partial rights issues

🐛 Troubleshooting
Common Issues
Memory Errors

Solution: The code automatically limits to 50,000 records

Reduce nrows parameter for lower memory usage

Spotify Authentication Failed

Verify Client ID and Secret are correct

Check Spotify App has Web API access enabled

File Not Found

Ensure unclaimedmusicalworkrightshares.tsv is in project directory

Check file permissions

Excel Permission Errors

Close any open Excel files before running

Code includes fallback to Desktop directory

🔮 Future Enhancements
Web interface for non-technical users

Batch processing for multiple artists

Advanced fuzzy matching algorithms

Integration with additional music databases

Real-time monitoring and alerts

Docker containerization

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/AmazingFeature)

Commit your changes (git commit -m 'Add some AmazingFeature')

Push to the branch (git push origin feature/AmazingFeature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

👨‍💻 Developer
Rohit Yadav

Email: rohityadav00619@gmail.com

GitHub: @krissi0619

🙏 Acknowledgments
Spotify Web API for music catalog data

Music rights organizations for dataset availability

Open source community for Python libraries
