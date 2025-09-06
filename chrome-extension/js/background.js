chrome.runtime.onInstalled.addListener(() => {
  console.log('LegalDify Page Capture Extension installed');
  
  chrome.storage.local.get(['apiUrl', 'authToken'], (result) => {
    if (!result.apiUrl) {
      chrome.storage.local.set({ apiUrl: 'http://localhost:8000' });
    }
    if (!result.authToken) {
      chrome.storage.local.set({ authToken: 'legal-dify-extension-2024' });
    }
  });
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'testConnection') {
    testAPIConnection(request.apiUrl, request.authToken)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true;
  }
});

async function testAPIConnection(apiUrl, authToken) {
  try {
    const response = await fetch(`${apiUrl}/api/v1/extension/verify-auth`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    });
    
    if (!response.ok) {
      throw new Error(`Connection failed: ${response.status}`);
    }
    
    const data = await response.json();
    return { success: true, data };
  } catch (error) {
    return { success: false, error: error.message };
  }
}