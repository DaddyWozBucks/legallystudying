# LegalDify Chrome Extension

This Chrome extension allows you to capture text content from any webpage and send it directly to your LegalDify system for analysis.

## Features

- Extract all text content from the current webpage
- Send content to LegalDify backend API
- Simple authentication with configurable token
- Clean, modern UI

## Installation

1. **Generate Icons** (one-time setup):
   - Open `chrome-extension/icons/generate_icons.html` in your browser
   - Right-click each canvas and save as:
     - icon16.png (16x16)
     - icon32.png (32x32)
     - icon48.png (48x48)
     - icon128.png (128x128)
   - Save all icons in the `chrome-extension/icons/` folder

2. **Load Extension in Chrome**:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" in the top right corner
   - Click "Load unpacked"
   - Select the `chrome-extension` folder
   - The extension will now appear in your extensions list

## Configuration

The extension comes pre-configured with:
- **API URL**: `http://localhost:8000`
- **Auth Token**: `legal-dify-extension-2024`

To change these settings:
1. Click the extension icon in Chrome
2. Click "Settings" at the bottom
3. Update the API URL and/or Auth Token
4. Click "Save Settings"

## Usage

1. **Start your LegalDify backend**:
   ```bash
   ./start-docker.sh
   ```

2. **Navigate to any webpage** you want to capture

3. **Click the LegalDify extension icon** in your browser toolbar

4. **Click "Capture Page Content"** button

5. The extension will:
   - Extract all text from the current page
   - Send it to your LegalDify backend
   - Display the document ID upon successful capture

## API Endpoint

The extension uses the following endpoint:
- `POST /api/v1/extension/ingest-page`

Request format:
```json
{
  "url": "https://example.com",
  "title": "Page Title",
  "content": "Extracted text content...",
  "metadata": {
    "description": "...",
    "keywords": "...",
    "author": "...",
    "timestamp": "2024-01-01T00:00:00Z"
  }
}
```

## Security

- The extension uses a bearer token for authentication
- Only works with locally running LegalDify instances
- No data is sent to external servers

## Troubleshooting

1. **"Cannot connect to API"**: Ensure your Docker container is running
2. **"Authentication failed"**: Check that the auth token matches the one in your backend
3. **"Cannot capture content from this page"**: Some pages (like chrome:// URLs) cannot be captured due to browser restrictions

## Development

To modify the extension:
1. Edit the files in the `chrome-extension` folder
2. Go to `chrome://extensions/`
3. Click the refresh icon on the LegalDify extension card
4. Test your changes