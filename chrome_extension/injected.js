// Script injetado na página - Emula API do Web Signer original

(function() {
  console.log('💉 Web Signer Custom - Script injetado');
  
  // API global que o e-SAJ espera
  window.WebSigner = {
    // Listar certificados disponíveis
    listCertificates: function() {
      return new Promise((resolve, reject) => {
        // Solicitar certificados
        window.postMessage({ type: 'WEB_SIGNER_GET_CERTIFICATES' }, '*');
        
        // Aguardar resposta
        const listener = (event) => {
          if (event.data.type === 'WEB_SIGNER_CERTIFICATES') {
            window.removeEventListener('message', listener);
            resolve(event.data.certificates);
          }
        };
        window.addEventListener('message', listener);
        
        // Timeout
        setTimeout(() => {
          window.removeEventListener('message', listener);
          reject(new Error('Timeout ao listar certificados'));
        }, 5000);
      });
    },
    
    // Assinar dados com certificado
    sign: function(data, certificateId) {
      return new Promise((resolve, reject) => {
        // Solicitar assinatura
        window.postMessage({
          type: 'WEB_SIGNER_SIGN',
          data: data,
          certificateId: certificateId
        }, '*');
        
        // Aguardar resposta
        const listener = (event) => {
          if (event.data.type === 'WEB_SIGNER_SIGNATURE') {
            window.removeEventListener('message', listener);
            resolve({
              signature: event.data.signature,
              certificate: event.data.certificate
            });
          }
          
          if (event.data.type === 'WEB_SIGNER_ERROR') {
            window.removeEventListener('message', listener);
            reject(new Error(event.data.error));
          }
        };
        window.addEventListener('message', listener);
        
        // Timeout
        setTimeout(() => {
          window.removeEventListener('message', listener);
          reject(new Error('Timeout ao assinar dados'));
        }, 10000);
      });
    },
    
    // Verificar se Web Signer está disponível
    isAvailable: function() {
      return Promise.resolve(true);
    },
    
    // Obter versão
    getVersion: function() {
      return Promise.resolve('1.0.0-custom');
    }
  };
  
  console.log('✅ Web Signer Custom API disponível');
  
  // Disparar evento para e-SAJ saber que Web Signer está pronto
  window.dispatchEvent(new Event('WebSignerReady'));
})();
