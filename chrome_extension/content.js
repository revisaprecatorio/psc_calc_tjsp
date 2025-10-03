// Content Script - Injeta funcionalidade no e-SAJ

console.log('🔌 Web Signer Custom - Content Script carregado');

// Injetar script na página
const script = document.createElement('script');
script.src = chrome.runtime.getURL('injected.js');
script.onload = function() {
  this.remove();
};
(document.head || document.documentElement).appendChild(script);

// Listener de mensagens da página
window.addEventListener('message', async (event) => {
  // Apenas mensagens da mesma origem
  if (event.source !== window) return;
  
  const message = event.data;
  
  if (message.type === 'WEB_SIGNER_GET_CERTIFICATES') {
    console.log('📋 Solicitação de certificados da página');
    
    // Buscar certificados do background
    chrome.runtime.sendMessage({ type: 'get_certificates' }, (response) => {
      window.postMessage({
        type: 'WEB_SIGNER_CERTIFICATES',
        certificates: response.certificates
      }, '*');
    });
  }
  
  if (message.type === 'WEB_SIGNER_SIGN') {
    console.log('✍️ Solicitação de assinatura da página');
    
    // Assinar dados via background
    chrome.runtime.sendMessage({
      type: 'sign_data',
      data: message.data
    }, (response) => {
      if (response.success) {
        window.postMessage({
          type: 'WEB_SIGNER_SIGNATURE',
          signature: response.result.signature,
          certificate: response.result.certificate
        }, '*');
      } else {
        window.postMessage({
          type: 'WEB_SIGNER_ERROR',
          error: response.error
        }, '*');
      }
    });
  }
});

// Listener de mensagens do background
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'certificates_loaded') {
    console.log('📋 Certificados carregados:', message.certificates);
    
    // Notificar página
    window.postMessage({
      type: 'WEB_SIGNER_CERTIFICATES',
      certificates: message.certificates
    }, '*');
  }
});

console.log('✅ Web Signer Custom - Pronto para uso');
