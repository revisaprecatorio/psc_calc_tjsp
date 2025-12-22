# -*- coding: utf-8 -*-
import os
import sys
import psycopg2
import json
import subprocess
import time
import shutil
from dotenv import load_dotenv

# Garante encoding UTF-8 no console do Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

# --- CONFIGURAÇÕES ---
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

CERT_SUBJECT_CN = os.getenv("CERT_SUBJECT_CN", "")
CERT_ISSUER_CN = os.getenv("CERT_ISSUER_CN", "")
CAS_USUARIO = os.getenv("CAS_USUARIO", "")
CAS_SENHA = os.getenv("CAS_SENHA", "")

# Pasta raiz onde os arquivos finais devem ficar
BASE_DOWNLOAD_DIR = r"C:\Temp\RevisaDownloads"

def fetch_precatorios_from_db():
    """Busca o próximo job pendente no banco."""
    precatorios_para_consultar = []
    job_id = None
    conn = None
    try:
        print("Conectando ao banco de dados PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        # Pega o próximo ID pendente
        query = """
            SELECT id, cpf, processos 
            FROM consultas_esaj 
            WHERE status = false 
            AND current_state='PAYMENT_APPROVED'
            ORDER BY id 
            LIMIT 1;
        """
        
        print("Buscando próximo item da fila...")
        cur.execute(query)
        result = cur.fetchone()
        
        if result:
            job_id, cpf, processos_data = result
            print(f"Job encontrado: ID={job_id}, CPF={cpf}")
            
            try:
                # Trata JSON ou Dict
                lista_de_processos = json.loads(processos_data) if isinstance(processos_data, str) else processos_data
                # Aceita estrutura {lista: [...]} ou lista direta [...]
                processos = lista_de_processos.get('lista', []) if isinstance(lista_de_processos, dict) else lista_de_processos

                for processo in processos:
                    if isinstance(processo, dict) and 'numero' in processo:
                        classe = processo.get('classe', '').strip()
                        # Filtra apenas Precatórios (com e sem acento)
                        if classe in ['Precatório', 'Precatorio']:
                            precatorios_para_consultar.append({
                                'cpf': cpf,
                                'numero': processo['numero'],
                            })
            except Exception as e:
                print(f"AVISO: Erro ao processar JSON do CPF {cpf}: {e}")
        
        cur.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERRO DE BANCO: {error}")
        return None, None
    finally:
        if conn is not None: conn.close()
    
    return job_id, precatorios_para_consultar

def update_status_in_db(job_id):
    """Marca o job como concluído."""
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        query = "UPDATE consultas_esaj SET status = true, current_state='PDF_DOWNLOADED', state_updated_at=NOW() WHERE id = %s;"
        cur.execute(query, (job_id,))
        conn.commit()
        cur.close()
        print(f"[SUCESSO] Job ID {job_id} marcado como concluído.")
    except Exception as error:
        print(f"[ERRO] Falha ao atualizar Job ID {job_id}: {error}")
    finally:
        if conn is not None: conn.close()

def mover_arquivos_para_raiz(pasta_temp, pasta_final):
    """
    Move arquivos da pasta temporária isolada para a pasta final do CPF.
    Evita sobrescrita acidental durante o download.
    """
    try:
        if not os.path.exists(pasta_temp):
            return

        arquivos = os.listdir(pasta_temp)
        for arquivo in arquivos:
            origem = os.path.join(pasta_temp, arquivo)
            destino = os.path.join(pasta_final, arquivo)
            
            # Move apenas arquivos (ignora subpastas se houver)
            if os.path.isfile(origem):
                # Se o arquivo já existe no destino, remove antes para atualizar
                if os.path.exists(destino):
                    try: os.remove(destino)
                    except: pass
                
                shutil.move(origem, destino)
                print(f"   -> Arquivo salvo: {arquivo}")
        
        # Remove a pasta temporária vazia
        try: os.rmdir(pasta_temp)
        except: pass
        
    except Exception as e:
        print(f"   [ERRO AO MOVER ARQUIVO] {e}")

def main():
    # Cria a pasta base se não existir
    os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)

    while True:
        job_id, lista_de_precatorios = fetch_precatorios_from_db()
        
        if job_id is None:
            print("Fila vazia. Encerrando worker.")
            break

        if not lista_de_precatorios:
            print(f"[AVISO] Job ID={job_id} sem precatórios válidos. Pulando.")
            update_status_in_db(job_id)
            continue

        total = len(lista_de_precatorios)
        print(f"--- Iniciando Job ID={job_id} ({total} processos) ---")
        
        todos_sucesso = True

        for i, item in enumerate(lista_de_precatorios):
            proc_numero = item['numero']
            cpf = item['cpf']

            print(f"\n>> Processando {i+1}/{total}: {proc_numero} (CPF {cpf})")

            # 1. Define a pasta FINAL do CPF (onde queremos os arquivos)
            # Ex: C:\Temp\RevisaDownloads\12345678900
            pasta_cpf_final = os.path.join(BASE_DOWNLOAD_DIR, cpf)
            os.makedirs(pasta_cpf_final, exist_ok=True)

            # 2. Define uma pasta TEMPORÁRIA exclusiva para ESTE download
            # Isso impede que o download do processo A apague o do processo B se tiverem nomes parecidos
            # Ex: C:\Temp\RevisaDownloads\12345678900\temp_0000000-00.2024...
            pasta_temp_isolada = os.path.join(pasta_cpf_final, f"temp_{proc_numero}")
            os.makedirs(pasta_temp_isolada, exist_ok=True)

            # 3. Monta o comando chamando o Crawler
            # --download-dir aponta para a PASTA TEMPORÁRIA
            command = [
                sys.executable, "crawler_full.py",
                "--doc", proc_numero,
                "--attach",                       
                "--debugger-address", "127.0.0.1:9222", 
                "--abrir-autos", 
                "--baixar-pdf", 
                "--turbo-download",
                "--download-dir", pasta_temp_isolada 
            ]

            if CAS_USUARIO: command.extend(["--cas-usuario", CAS_USUARIO])
            if CAS_SENHA: command.extend(["--cas-senha", CAS_SENHA])

            try:
                # Executa o crawler
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    check=True,
                    encoding="utf-8",
                    errors="replace",
                )
                
                # Log resumido (opcional: imprimir stdout se quiser debugar)
                # print(result.stdout)

                # 4. CONSOLIDAÇÃO
                # Move o PDF baixado da pasta TEMP para a pasta FINAL
                mover_arquivos_para_raiz(pasta_temp_isolada, pasta_cpf_final)

            except subprocess.CalledProcessError as e:
                print(f"[FALHA] Erro no crawler para {proc_numero}. Código: {e.returncode}")
                if e.stderr: print(f"STDERR: {e.stderr}")
                todos_sucesso = False 
            except Exception as e:
                print(f"[ERRO GERAL] {e}")
                todos_sucesso = False
                break
            
            # 5. PAUSA TÁTICA
            # Dá 5 segundos para o Chrome "respirar" e evitar bloqueios ou sessões presas
            print("Aguardando 5s para o próximo processo...")
            time.sleep(5)

        if todos_sucesso:
            update_status_in_db(job_id)
        else:
            print(f"[AVISO] Job ID={job_id} concluído com falhas parciais. Status não atualizado (ou ajuste conforme necessidade).")
            # Se quiser atualizar mesmo com erro parcial, descomente:
            # update_status_in_db(job_id)

if __name__ == "__main__":
    main()