# Simple Flask Loads API

This small project provides a Flask server with one endpoint to return "loads" from a csv.
Part of an integration with the HappyRobot platform

Files:
- `app.py` - Flask application exposing GET /loads
- `db_init.py` - Initializes `loads.db` and seeds sample data
- `requirements.txt` - Python dependencies

Quick start (Windows PowerShell):

1. Create a virtual environment and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Initialize the database:

```powershell
python db_init.py
```

3. Run the server:

```powershell
python app.py
```

4. Request loads:

```powershell
curl http://127.0.0.1:5000/loads
```

API key and optional response encryption
---------------------------------------

You can secure the API with a simple API key and optionally enable encrypted responses using Fernet symmetric encryption.

Server-side:

- Set an `API_KEY` environment variable to require clients to include `X-API-Key` on each request.
- (Optional) Set a `RESPONSE_ENCRYPTION_KEY` environment variable with a Fernet key to enable server-side encryption support.

Example (PowerShell):

```powershell
$env:API_KEY = 'your-api-key-here'
# generate a Fernet key (Python) and set it for the server
# python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
$env:RESPONSE_ENCRYPTION_KEY = '...fernet-key...'

# Run server
python app.py
```

Client usage:

- Plain JSON: include header `X-API-Key: your-api-key`.
- Encrypted response: include headers `X-API-Key` and `X-Response-Encrypt: 1`. The server will return `{ "payload": "<fernet-token>" }` — decrypt with the same Fernet key.

