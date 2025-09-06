function extractPageText() {
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: function(node) {
        const parent = node.parentElement;
        if (!parent) return NodeFilter.FILTER_REJECT;
        
        const tagName = parent.tagName.toLowerCase();
        if (['script', 'style', 'noscript'].includes(tagName)) {
          return NodeFilter.FILTER_REJECT;
        }
        
        const text = node.textContent.trim();
        if (!text || text.length === 0) {
          return NodeFilter.FILTER_REJECT;
        }
        
        return NodeFilter.FILTER_ACCEPT;
      }
    }
  );

  const textContent = [];
  let node;
  while (node = walker.nextNode()) {
    const text = node.textContent.trim();
    if (text) {
      textContent.push(text);
    }
  }
  
  return textContent.join(' ').replace(/\s+/g, ' ').trim();
}

function getPageMetadata() {
  const metadata = {
    url: window.location.href,
    title: document.title || 'Untitled Page',
    description: '',
    keywords: '',
    author: '',
    timestamp: new Date().toISOString()
  };
  
  const metaTags = document.getElementsByTagName('meta');
  for (let meta of metaTags) {
    if (meta.name === 'description' && meta.content) {
      metadata.description = meta.content;
    } else if (meta.name === 'keywords' && meta.content) {
      metadata.keywords = meta.content;
    } else if (meta.name === 'author' && meta.content) {
      metadata.author = meta.content;
    }
  }
  
  const ogTitle = document.querySelector('meta[property="og:title"]');
  if (ogTitle && ogTitle.content && !metadata.title) {
    metadata.title = ogTitle.content;
  }
  
  const ogDescription = document.querySelector('meta[property="og:description"]');
  if (ogDescription && ogDescription.content && !metadata.description) {
    metadata.description = ogDescription.content;
  }
  
  return metadata;
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'extractContent') {
    try {
      const textContent = extractPageText();
      const metadata = getPageMetadata();
      
      sendResponse({
        success: true,
        data: {
          content: textContent,
          metadata: metadata,
          url: metadata.url,
          title: metadata.title
        }
      });
    } catch (error) {
      sendResponse({
        success: false,
        error: error.message
      });
    }
  }
  return true;
});