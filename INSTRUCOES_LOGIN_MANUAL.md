# 📋 Instruções: Login Manual no Google via RDP

## 🎯 Objetivo
Fazer login no Google manualmente via RDP usando o usuário `crawler` e salvar o perfil para uso posterior pelo Selenium.

## ⚠️ IMPORTANTE
- ChromeDriver e Xvfb agora rodam como usuário `crawler` (não mais como root)
- O perfil do Chrome usado é: `/home/crawler/.config/google-chrome`
- Você faz login via RDP como `crawler` e usa o Chrome normalmente

---

## 📝 PASSO A PASSO

### **PASSO 0: Reconfigurar Serviços (Execute UMA VEZ)**
```bash
cd /opt/crawler_tjsp
chmod +x reconfigure_as_crawler.sh
./reconfigure_as_crawler.sh
```

### **PASSO 1: Conectar via RDP**
1. Abra o RDP e conecte ao servidor
2. Faça login como usuário `crawler` (como você já faz!)

### **PASSO 2: Abrir Chrome Normalmente**
Via RDP, simplesmente:
1. Abra o Chrome (ícone na área de trabalho ou menu)
2. **OU** execute no terminal:

```bash
google-chrome https://www.google.com &
```

### **PASSO 3: Fazer Login no Google**
1. O Chrome vai abrir no display virtual (você verá via RDP)
2. Clique em "Fazer login" no canto superior direito
3. Digite: `revisaprecatorio@gmail.com`
4. Digite a senha: `R3v1s@2025`
5. Complete qualquer verificação de segurança se necessário
6. **IMPORTANTE:** Marque "Manter conectado" se aparecer

### **PASSO 3: Verificar Login**
1. Vá para: https://myaccount.google.com
2. Confirme que está logado
3. Vá para: chrome://extensions/
4. Ative o "Developer mode" (toggle no canto superior direito)

### **PASSO 4: Fechar Chrome**
Simplesmente feche o Chrome normalmente (X na janela)

### **PASSO 5: Testar com Selenium**
Execute no terminal (via SSH ou RDP):

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
