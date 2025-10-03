// Service Worker - Gerencia conexão WebSocket

let ws = null;
let certificados = [];

// Conectar ao servidor WebSocket
function conectarWebSocket() {
  console.log('🔌 Conectando ao servidor WebSocket...');
  
  ws = new WebSocket('ws://localhost:8765');
  
  ws.onopen = () => {
    console.log('✅ Conectado ao servidor WebSocket');
    // Solicitar lista de certificados
    listarCertificados();
  };
  
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('📨 Mensagem recebida:', data);
    
    if (data.action === 'list_certificates') {
      certificados = data.certificates;
      console.log('📋 Certificados disponíveis:', certificados);
      
      // Notificar content script
      chrome.runtime.sendMessage({
        type: 'certificates_loaded',
        certificates: certificados
      });
    }
    
    if (data.action === 'sign') {
      console.log('✍️ Assinatura recebida');
      // Notificar content script
      chrome.runtime.sendMessage({
        type: 'signature_ready',
        signature: data.signature,
        certificate: data.certificate
      });
    }
  };
  
  ws.onerror = (error) => {
    console.error('❌ Erro WebSocket:', error);
  };
  
  ws.onclose = () => {
    console.log('🔌 Conexão WebSocket fechada. Reconectando em 5s...');
    setTimeout(conectarWebSocket, 5000);
  };
}

// Listar certificados
function listarCertificados() {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ action: 'list_certificates' }));
  }
}

// Assinar dados
function assinarDados(dados) {
  return new Promise((resolve, reject) => {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      reject(new Error('WebSocket não conectado'));
      return;
    }
    
    // Listener temporário para resposta
    const listener = (message) => {
      if (message.type === 'signature_ready') {
        chrome.runtime.onMessage.removeListener(listener);
        resolve(message);
      }
    };
    chrome.runtime.onMessage.addListener(listener);
    
    // Enviar requisição
    ws.send(JSON.stringify({
      action: 'sign',
      data: dados
    }));
    
    // Timeout de 10 segundos
    setTimeout(() => {
      chrome.runtime.onMessage.removeListener(listener);
      reject(new Error('Timeout ao assinar dados'));
    }, 10000);
  });
}

// Listener de mensagens do content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'get_certificates') {
    sendResponse({ certificates: certificados });
  }
  
  if (request.type === 'sign_data') {
    assinarDados(request.data)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Mantém canal aberto para resposta assíncrona
  }
  
  if (request.type === 'reconnect') {
    conectarWebSocket();
    sendResponse({ success: true });
  }
});

// Iniciar conexão ao carregar
conectarWebSocket();

console.log('🚀 Web Signer Custom (WebSocket) - Service Worker iniciado');
