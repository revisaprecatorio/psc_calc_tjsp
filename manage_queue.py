#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Gerenciamento da Fila de Processamento
Permite visualizar e resetar o status dos jobs na fila.

Uso:
    python manage_queue.py --status          # Ver estatísticas
    python manage_queue.py --list            # Listar jobs pendentes
    python manage_queue.py --reset-all       # Resetar todos
    python manage_queue.py --reset-last 10   # Resetar últimos 10
    python manage_queue.py --reset-id 30 31  # Resetar IDs específicos
    python manage_queue.py --reset-cpf 12345678900  # Resetar por CPF
"""

import os
import sys
import argparse
import psycopg2
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}


def get_connection():
    """Cria conexão com o banco de dados."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        sys.exit(1)


def show_statistics():
    """Mostra estatísticas da fila."""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            COUNT(*) as total,
            COUNT(*) FILTER (WHERE status = TRUE) as processados,
            COUNT(*) FILTER (WHERE status = FALSE OR status IS NULL) as pendentes
        FROM consultas_esaj;
    """
    
    cur.execute(query)
    result = cur.fetchone()
    
    print("\n" + "="*60)
    print("📊 ESTATÍSTICAS DA FILA")
    print("="*60)
    print(f"Total de registros:     {result[0]}")
    print(f"✅ Processados:         {result[1]}")
    print(f"⏳ Pendentes:           {result[2]}")
    print("="*60 + "\n")
    
    cur.close()
    conn.close()


def list_pending(limit=10):
    """Lista jobs pendentes."""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT id, cpf, status, 
               CASE 
                   WHEN processos::text LIKE '%Precatório%' THEN 'Sim'
                   ELSE 'Não'
               END as tem_precatorio
        FROM consultas_esaj 
        WHERE status = FALSE OR status IS NULL 
        ORDER BY id 
        LIMIT %s;
    """
    
    cur.execute(query, (limit,))
    results = cur.fetchall()
    
    if results:
        print(f"\n⏳ PRÓXIMOS {len(results)} JOBS PENDENTES:\n")
        headers = ["ID", "CPF", "Status", "Tem Precatório?"]
        print(tabulate(results, headers=headers, tablefmt="grid"))
    else:
        print("\n✅ Nenhum job pendente na fila!")
    
    print()
    cur.close()
    conn.close()


def list_processed(limit=10):
    """Lista últimos jobs processados."""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        SELECT id, cpf, status
        FROM consultas_esaj 
        WHERE status = TRUE 
        ORDER BY id DESC 
        LIMIT %s;
    """
    
    cur.execute(query, (limit,))
    results = cur.fetchall()
    
    if results:
        print(f"\n✅ ÚLTIMOS {len(results)} JOBS PROCESSADOS:\n")
        headers = ["ID", "CPF", "Status"]
        print(tabulate(results, headers=headers, tablefmt="grid"))
    else:
        print("\n⚠️  Nenhum job processado ainda!")
    
    print()
    cur.close()
    conn.close()


def reset_all():
    """Reseta TODOS os registros."""
    conn = get_connection()
    cur = conn.cursor()
    
    # Conta quantos serão afetados
    cur.execute("SELECT COUNT(*) FROM consultas_esaj WHERE status = TRUE;")
    count = cur.fetchone()[0]
    
    if count == 0:
        print("\n⚠️  Nenhum registro para resetar!")
        cur.close()
        conn.close()
        return
    
    print(f"\n⚠️  ATENÇÃO: Isso vai resetar {count} registros!")
    confirm = input("Digite 'SIM' para confirmar: ")
    
    if confirm.upper() == "SIM":
        cur.execute("UPDATE consultas_esaj SET status = FALSE;")
        conn.commit()
        print(f"✅ {count} registros resetados com sucesso!")
    else:
        print("❌ Operação cancelada.")
    
    cur.close()
    conn.close()


def reset_last(n):
    """Reseta os últimos N registros processados."""
    conn = get_connection()
    cur = conn.cursor()
    
    query = """
        UPDATE consultas_esaj 
        SET status = FALSE 
        WHERE id IN (
            SELECT id FROM consultas_esaj 
            WHERE status = TRUE 
            ORDER BY id DESC 
            LIMIT %s
        );
    """
    
    cur.execute(query, (n,))
    conn.commit()
    affected = cur.rowcount
    
    print(f"\n✅ {affected} registros resetados (últimos {n})!")
    
    cur.close()
    conn.close()


def reset_by_ids(ids):
    """Reseta registros específicos por ID."""
    conn = get_connection()
    cur = conn.cursor()
    
    placeholders = ','.join(['%s'] * len(ids))
    query = f"UPDATE consultas_esaj SET status = FALSE WHERE id IN ({placeholders});"
    
    cur.execute(query, ids)
    conn.commit()
    affected = cur.rowcount
    
    print(f"\n✅ {affected} registros resetados (IDs: {', '.join(map(str, ids))})!")
    
    cur.close()
    conn.close()


def reset_by_cpf(cpf):
    """Reseta todos os registros de um CPF específico."""
    conn = get_connection()
    cur = conn.cursor()
    
    query = "UPDATE consultas_esaj SET status = FALSE WHERE cpf = %s;"
    
    cur.execute(query, (cpf,))
    conn.commit()
    affected = cur.rowcount
    
    if affected > 0:
        print(f"\n✅ {affected} registros resetados para o CPF {cpf}!")
    else:
        print(f"\n⚠️  Nenhum registro encontrado para o CPF {cpf}!")
    
    cur.close()
    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Gerenciador da Fila de Processamento TJSP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python manage_queue.py --status
  python manage_queue.py --list
  python manage_queue.py --list-processed
  python manage_queue.py --reset-all
  python manage_queue.py --reset-last 10
  python manage_queue.py --reset-id 30 31 32
  python manage_queue.py --reset-cpf 07620857893
        """
    )
    
    parser.add_argument('--status', action='store_true', 
                       help='Mostra estatísticas da fila')
    parser.add_argument('--list', action='store_true', 
                       help='Lista jobs pendentes')
    parser.add_argument('--list-processed', action='store_true', 
                       help='Lista últimos jobs processados')
    parser.add_argument('--reset-all', action='store_true', 
                       help='Reseta TODOS os registros (cuidado!)')
    parser.add_argument('--reset-last', type=int, metavar='N', 
                       help='Reseta os últimos N registros processados')
    parser.add_argument('--reset-id', type=int, nargs='+', metavar='ID', 
                       help='Reseta registros específicos por ID')
    parser.add_argument('--reset-cpf', type=str, metavar='CPF', 
                       help='Reseta todos os registros de um CPF')
    
    args = parser.parse_args()
    
    # Se nenhum argumento foi passado, mostra help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)
    
    # Executa a ação solicitada
    if args.status:
        show_statistics()
    
    if args.list:
        list_pending()
    
    if args.list_processed:
        list_processed()
    
    if args.reset_all:
        reset_all()
    
    if args.reset_last:
        reset_last(args.reset_last)
    
    if args.reset_id:
        reset_by_ids(args.reset_id)
    
    if args.reset_cpf:
        reset_by_cpf(args.reset_cpf)


if __name__ == "__main__":
    main()
