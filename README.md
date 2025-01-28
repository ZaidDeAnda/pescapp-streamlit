<div align='center'>
   <img src='https://github.com/user-attachments/assets/1c540dd9-7824-4921-8872-e1aef2c407b5' width='500px' />
</div>

---

# Pescapp 🎣

Pescapp is a web application built with Streamlit that visualizes fishing routes on an interactive map. The application connects to Firebase to fetch and display route data.

## Technologies Used

- Python 3.8+
- Streamlit
- Firebase Admin SDK
- Folium (for map visualization)
- Pandas

## Prerequisites

Before running this project, make sure you have:

- Python 3.8 or higher installed
- A Firebase project set up with Firestore
- Firebase credentials (service account key)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pescapp-streamlit.git
cd pescapp-streamlit
```

2. Create and activate a virtual environment:

```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up Firebase credentials:
   - Create a `creds.json` file in the root directory
   - Add your Firebase service account credentials to this file

## Environment Setup

The application expects Firebase credentials to be available as Streamlit secrets. You can set these up by:

1. Creating a `.streamlit/secrets.toml` file with your Firebase credentials:
```toml
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "your-private-key"
client_email = "your-client-email"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-client-cert-url"
universe_domain = "googleapis.com"
```

## Running the Application

To run the application locally:

```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Project Structure
```
pescapp-streamlit/
├── app.py # Main Streamlit application
├── requirements.txt # Python dependencies
├── .gitignore # Git ignore file
├── README.md # Project documentation
├── assets/ # Static assets
│ └── Elipse.png # Map marker icon
├── utils/ # Utility functions
│ └── database.py # Firebase database operations
├── .streamlit/ # Streamlit configuration
│ └── secrets.toml # Secrets configuration
└── creds.json # Firebase credentials
```


## Features

- Display of fishing routes on an interactive map
- Selection of different fishing trips by date
- Visualization of route points with custom markers
- Route paths shown as connected lines
- Firebase integration for data storage and retrieval

## Firebase Database Structure

The application expects the following collections in Firestore:

- `travels`: Contains documents with travel information
  - Fields: `travel_id`, `timestamp`
- `coords`: Contains coordinate information for each travel
  - Fields: `travel_id`, `coords` (with `lat` and `lon`), `timestamp`

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
