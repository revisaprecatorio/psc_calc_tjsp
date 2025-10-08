# -*- coding: utf-8 -*-
import os
import sys
import psycopg2
import json
import subprocess
from dotenv import load_dotenv
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

# Configurações de certificado digital
CERT_SUBJECT_CN = os.getenv("CERT_SUBJECT_CN", "")
CERT_ISSUER_CN = os.getenv("CERT_ISSUER_CN", "")
CAS_USUARIO = os.getenv("CAS_USUARIO", "")
CAS_SENHA = os.getenv("CAS_SENHA", "")

# --- ALTERADO: A função agora busca apenas itens não processados e retorna o ID ---
def fetch_precatorios_from_db():
    """
    Conecta ao PostgreSQL e busca o próximo item não processado.
    Retorna uma tupla com o ID da linha e a lista de precatórios a consultar.
    """
    precatorios_para_consultar = []
    job_id = None
    conn = None
    try:
        print("Conectando ao banco de dados PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # ALTERADO: A query agora busca o ID e filtra por `processado = FALSE` (ou NULL).
        # Isso transforma o script em uma "fila" de processamento.
        query = """
            SELECT id, cpf, processos 
            FROM consultas_esaj 
            WHERE status = FALSE OR status IS NULL
            ORDER BY id 
            LIMIT 1;
        """
        
        print(f"Executando a query para buscar o próximo item da fila...")
        cur.execute(query)
        
        # Pega apenas um resultado
        result = cur.fetchone()
        
        if result:
            job_id, cpf, processos_data = result
            print(f"Item encontrado para processar: ID={job_id}, CPF={cpf}")
            
            try:
                lista_de_processos = json.loads(processos_data) if isinstance(processos_data, str) else processos_data
                processos = lista_de_processos.get('lista', []) if isinstance(lista_de_processos, dict) else lista_de_processos

                for processo in processos:
                    if isinstance(processo, dict) and processo.get('classe') == 'Precatório' and 'numero' in processo:
                        precatorios_para_consultar.append({
                            'cpf': cpf,
                            'numero': processo['numero'],
                        })
            except Exception as e:
                print(f"AVISO: Erro ao processar dados para o CPF {cpf}. Erro: {e}")
        
        cur.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERRO: Falha ao conectar ou buscar dados no PostgreSQL: {error}")
        return None, None
    finally:
        if conn is not None:
            conn.close()
            print("Conexão com o banco de dados fechada.")
    
    return job_id, precatorios_para_consultar

# --- NOVO: Função para atualizar o status no banco de dados ---
def update_status_in_db(job_id_to_update):
    """
    Conecta ao banco de dados e atualiza a coluna 'processado' para TRUE
    para o ID fornecido.
    """
    conn = None
    try:
        print(f"\nAtualizando status para 'processado = TRUE' para o ID: {job_id_to_update}")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        query = "UPDATE consultas_esaj SET status = TRUE WHERE id = %s;"
        
        cur.execute(query, (job_id_to_update,))
        
        # Confirma a transação
        conn.commit()
        
        cur.close()
        print(f"[SUCESSO] Status atualizado para o ID {job_id_to_update}.")
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"[ERRO] Falha ao atualizar o status para o ID {job_id_to_update}: {error}")
    finally:
        if conn is not None:
            conn.close()

def main():
    """
    Orquestra a execução do crawler.
    """
    chrome_profile_path = os.getenv("CHROME_USER_DATA_DIR")
    if not chrome_profile_path:
        print("\nERRO: A variável CHROME_USER_DATA_DIR não está definida no .env. Encerrando.")
        return

    # Garante que o diretório do perfil exista
    try:
        os.makedirs(chrome_profile_path, exist_ok=True)
    except Exception as e:
        print(f"[AVISO] Não consegui criar '{chrome_profile_path}': {e}")

    while True:
        job_id, lista_de_precatorios = fetch_precatorios_from_db()
        if not lista_de_precatorios:
            print("Nenhum precatório novo para processar encontrado. Encerrando o worker.")
            break

        total = len(lista_de_precatorios)
        todos_sucesso = True

        for i, precatorio_info in enumerate(lista_de_precatorios):
            processo_cnj = precatorio_info['numero']
            cpf_associado = precatorio_info['cpf']

            print("\n" + "=" * 80)
            print(f"Processando item {i+1}/{total} do Job ID={job_id}: Processo {processo_cnj}")
            print("=" * 80)

            caminho_download = os.path.abspath(f"downloads/{cpf_associado}")

            # Fecha Chrome/ChromeDriver anteriores para liberar o perfil
            try:
                if os.name == "nt":
                    # Windows
                    subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], capture_output=True)
                    subprocess.run(["taskkill", "/F", "/IM", "chromedriver.exe"], capture_output=True)
                else:
                    # Linux
                    subprocess.run(["pkill", "-9", "chrome"], capture_output=True, timeout=5)
                    subprocess.run(["pkill", "-9", "chromium"], capture_output=True, timeout=5)
                    subprocess.run(["pkill", "-9", "chromedriver"], capture_output=True, timeout=5)
            except Exception:
                pass  # ok se não tiver nada pra matar

            # 👇 AQUI ESTÁ O PONTO-CHAVE: usar o mesmo perfil do Chrome
            command = [
                sys.executable, "crawler_full.py",
                "--doc", processo_cnj,
                "--abrir-autos", "--baixar-pdf", "--turbo-download",
                "--download-dir", caminho_download,
                "--user-data-dir", chrome_profile_path,   # <— usa o perfil com certificado/políticas
            ]

            # Certificado (auto-seleção)
            if CERT_SUBJECT_CN:
                command.extend(["--cert-subject-cn", CERT_SUBJECT_CN])
            if CERT_ISSUER_CN:
                command.extend(["--cert-issuer-cn", CERT_ISSUER_CN])

            # Fallback CPF/senha se houver (não atrapalha o fluxo por certificado)
            if CAS_USUARIO:
                command.extend(["--cas-usuario", CAS_USUARIO])
            if CAS_SENHA:
                command.extend(["--cas-senha", CAS_SENHA])

            try:
                print(f"Executando comando: {' '.join(command)}")
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding="utf-8",
                    errors="replace",
                )

                if result.stdout:
                    print("\n--- Output do Crawler ---")
                    print(result.stdout)
                    print("--- Fim do Output ---\n")

            except subprocess.CalledProcessError as e:
                print("\n" + "*" * 80)
                print(f"ERRO CRÍTICO: O script crawler_full.py falhou para o processo {processo_cnj}.")
                print("\n--- Saída de Erro (stderr) ---")
                print(e.stderr)
                if e.stdout:
                    print("\n--- Saída Padrão (stdout) ---")
                    print(e.stdout)
                print("*" * 80)
                todos_sucesso = False
            except FileNotFoundError:
                print("\nERRO: Não foi possível encontrar 'crawler_full.py'.")
                todos_sucesso = False
                break

        # Atualiza status do job somente se todos os itens foram sucesso
        if todos_sucesso:
            update_status_in_db(job_id)
        else:
            print(f"\n[AVISO] O status do Job ID={job_id} não será atualizado porque um ou mais subprocessos falharam.")


if __name__ == "__main__":
    main()
