let currentTab = null;

document.addEventListener('DOMContentLoaded', async () => {
  await loadSettings();
  await getCurrentTab();
  
  document.getElementById('captureBtn').addEventListener('click', capturePageContent);
  document.getElementById('settingsBtn').addEventListener('click', toggleSettings);
  document.getElementById('saveSettingsBtn').addEventListener('click', saveSettings);
  
  document.getElementById('apiUrl').addEventListener('input', onSettingsChange);
  document.getElementById('authToken').addEventListener('input', onSettingsChange);
});

async function loadSettings() {
  try {
    const result = await chrome.storage.local.get(['apiUrl', 'authToken']);
    if (result.apiUrl) {
      document.getElementById('apiUrl').value = result.apiUrl;
    }
    if (result.authToken) {
      document.getElementById('authToken').value = result.authToken;
    }
  } catch (error) {
    console.error('Error loading settings:', error);
  }
}

async function saveSettings() {
  const apiUrl = document.getElementById('apiUrl').value;
  const authToken = document.getElementById('authToken').value;
  
  try {
    await chrome.storage.local.set({ apiUrl, authToken });
    showStatus('Settings saved successfully!', 'success');
    document.getElementById('saveSettingsBtn').style.display = 'none';
    toggleSettings();
  } catch (error) {
    showStatus('Failed to save settings', 'error');
  }
}

function onSettingsChange() {
  document.getElementById('saveSettingsBtn').style.display = 'inline-block';
}

function toggleSettings() {
  const settings = document.querySelector('.settings');
  const settingsBtn = document.getElementById('settingsBtn');
  
  if (settings.classList.contains('active')) {
    settings.classList.remove('active');
    settingsBtn.textContent = 'Settings';
  } else {
    settings.classList.add('active');
    settingsBtn.textContent = 'Hide Settings';
  }
}

async function getCurrentTab() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    currentTab = tab;
    
    document.getElementById('pageTitle').textContent = tab.title || 'Untitled';
    document.getElementById('pageUrl').textContent = tab.url || '';
    document.getElementById('pageUrl').title = tab.url || '';
  } catch (error) {
    console.error('Error getting current tab:', error);
    showStatus('Failed to get current tab information', 'error');
  }
}

async function capturePageContent() {
  const captureBtn = document.getElementById('captureBtn');
  const spinner = captureBtn.querySelector('.spinner');
  const btnText = captureBtn.querySelector('.btn-text');
  
  captureBtn.disabled = true;
  spinner.style.display = 'block';
  btnText.textContent = 'Capturing...';
  
  try {
    const response = await chrome.tabs.sendMessage(currentTab.id, { action: 'extractContent' });
    
    if (!response || !response.success) {
      throw new Error(response?.error || 'Failed to extract content');
    }
    
    btnText.textContent = 'Sending to API...';
    
    const apiUrl = document.getElementById('apiUrl').value;
    const authToken = document.getElementById('authToken').value;
    
    const apiResponse = await fetch(`${apiUrl}/api/v1/extension/ingest-page`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authToken}`
      },
      body: JSON.stringify({
        url: response.data.url,
        title: response.data.title,
        content: response.data.content,
        metadata: response.data.metadata
      })
    });
    
    if (!apiResponse.ok) {
      const errorData = await apiResponse.json().catch(() => ({}));
      throw new Error(errorData.detail || `API Error: ${apiResponse.status}`);
    }
    
    const result = await apiResponse.json();
    showStatus(`Page content successfully captured! Document ID: ${result.id}`, 'success');
    
  } catch (error) {
    console.error('Capture error:', error);
    
    if (error.message.includes('Cannot access')) {
      showStatus('Cannot capture content from this page (browser restrictions)', 'error');
    } else if (error.message.includes('401')) {
      showStatus('Authentication failed. Please check your auth token.', 'error');
    } else if (error.message.includes('Failed to fetch')) {
      showStatus('Cannot connect to API. Please check the API URL and ensure the server is running.', 'error');
    } else {
      showStatus(`Error: ${error.message}`, 'error');
    }
  } finally {
    captureBtn.disabled = false;
    spinner.style.display = 'none';
    btnText.textContent = 'Capture Page Content';
  }
}

function showStatus(message, type) {
  const statusEl = document.getElementById('status');
  statusEl.textContent = message;
  statusEl.className = `status ${type}`;
  
  if (type === 'success') {
    setTimeout(() => {
      statusEl.className = 'status';
    }, 5000);
  }
}