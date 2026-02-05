import os
import subprocess
import sqlite3
import hashlib

# 1. HARDCODED PASSWORD (CWE-798)
# O Bandit deve detectar isso imediatamente (B105).
# Risco: Deixar credenciais no código fonte é falha crítica.
DB_PASSWORD = "changeit123" 
AWS_SECRET_KEY = "AKIA1234567890"

def check_password(input_pass):
    # 2. WEAK HASHING (CWE-328)
    # O Bandit/CodeQL alertarão sobre uso de MD5 (inseguro para senhas).
    if hashlib.md5(input_pass.encode()).hexdigest() == "5f4dcc3b5aa765d61d8327deb882cf99":
        return True

def get_user_data(username):
    # 3. SQL INJECTION (CWE-89)
    # O CodeQL deve traçar o fluxo de dados e o Bandit (B608) detectará a construção da string.
    # Risco: Permite que atacantes manipulem a consulta ao banco.
    conn = sqlite3.connect("db.sqlite3")
    cursor = conn.cursor()
    
    # PERIGO: Format string sendo usada diretamente na query
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    
    return cursor.fetchall()

def ping_address(address):
    # 4. COMMAND INJECTION (CWE-78)
    # O Bandit detectará o uso de shell=True com input (B602).
    # Risco: Permite execução de comandos do sistema operacional.
    subprocess.call(f"ping -c 1 {address}", shell=True)
