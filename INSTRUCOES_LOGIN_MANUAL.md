# 📋 Instruções: Login Manual no Google via RDP

## 🎯 Objetivo
Fazer login no Google manualmente via RDP e salvar o perfil para uso posterior pelo Selenium.

---

## 📝 PASSO A PASSO

### **PASSO 1: Conectar via RDP**
1. Abra o RDP e conecte ao servidor
2. Faça login como usuário `root`

### **PASSO 2: Abrir Chrome com o Perfil Correto**
Execute no terminal do servidor:

```bash
# Parar ChromeDriver temporariamente
systemctl stop chromedriver

# Abrir Chrome com o perfil que o Selenium vai usar
DISPLAY=:99 google-chrome \
  --user-data-dir=/opt/crawler_tjsp/chrome_profile_revisa \
  --no-sandbox \
  --disable-dev-shm-usage \
  https://www.google.com &

# Aguardar Chrome abrir (5 segundos)
sleep 5
```

### **PASSO 3: Fazer Login no Google**
1. O Chrome vai abrir no display virtual (você verá via RDP)
2. Clique em "Fazer login" no canto superior direito
3. Digite: `revisaprecatorio@gmail.com`
4. Digite a senha: `R3v1s@2025`
5. Complete qualquer verificação de segurança se necessário
6. **IMPORTANTE:** Marque "Manter conectado" se aparecer

### **PASSO 4: Verificar Login**
1. Vá para: https://myaccount.google.com
2. Confirme que está logado
3. Vá para: chrome://extensions/
4. Ative o "Developer mode" (toggle no canto superior direito)

### **PASSO 5: Fechar Chrome**
```bash
# Fechar Chrome
pkill -f "google-chrome.*chrome_profile_revisa"

# Reiniciar ChromeDriver
systemctl start chromedriver
```

### **PASSO 6: Testar com Selenium**
Execute o script de verificação:

```bash
cd /opt/crawler_tjsp
python3 verify_google_login.py
```

---

## ✅ Resultado Esperado

Após seguir esses passos:
- ✅ Google estará logado no perfil
- ✅ Developer Mode estará ativado
- ✅ Selenium poderá usar esse perfil sem precisar fazer login novamente
- ✅ Poderemos instalar a extensão Web Signer

---

## 🔧 Script de Verificação

Vou criar um script `verify_google_login.py` que:
1. Abre o Chrome com o perfil salvo
2. Verifica se está logado no Google
3. Tira screenshots para confirmação
