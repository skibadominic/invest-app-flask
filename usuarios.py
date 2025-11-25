import sqlite3
import database
from werkzeug.security import generate_password_hash, check_password_hash

def cadastrar_usuario(nome_digitado, email_digitado, senha_digitada):

    nome = nome_digitado.strip().capitalize()
    email = email_digitado.strip().lower()
    
    if not nome or not email or not senha_digitada:
        return False
        
    if "@" not in email or "." not in email:
        return False
    
    hash_senha = generate_password_hash(senha_digitada)

    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        
        novo_usuario_sql = """
        INSERT INTO usuarios (nome, email, senha) 
        VALUES (?, ?, ?)
        """
        
        cursor.execute(novo_usuario_sql, (nome, email, hash_senha))
        
        db.commit()
        db.close()
        
        return True
        
    except sqlite3.IntegrityError:
        return False
    except Exception as e:
        return False

def login(email_digitado, senha_digitada):
    
    email = email_digitado.strip().lower()
    
    try:
        db = sqlite3.connect(database.DB_NOME)
        db.row_factory = sqlite3.Row
        cursor = db.cursor()
        
        login_sql = "SELECT * FROM usuarios WHERE email = ?"
        cursor.execute(login_sql, (email,))
        usuario_encontrado = cursor.fetchone()
        db.close()
        
        if usuario_encontrado:
            hash_salvo = usuario_encontrado['senha']
            if check_password_hash(hash_salvo, senha_digitada):
                return usuario_encontrado
        return None
        
    except Exception as e:
        print(f"Erro no login: {e}")
        return None

def atualizar_perfil(id_usuario, novo_perfil):
    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        
        sql_update = """
        UPDATE usuarios
        SET perfil = ?
        WHERE id = ?
        """
        
        cursor.execute(sql_update, (novo_perfil, id_usuario))
        
        db.commit()
        db.close()
        
        return True
        
    except Exception as e:
        print(f"[ERRO] Não foi possível atualizar o perfil: {e}")
        return False

def deletar_usuario_completo(id_usuario):
    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM posicoes WHERE id_usuario = ?", (id_usuario,))
        
        cursor.execute("DELETE FROM metas WHERE id_usuario = ?", (id_usuario,))
        
        cursor.execute("DELETE FROM usuarios WHERE id = ?", (id_usuario,))
        
        db.commit()
        db.close()
        print(f"Usuário {id_usuario} e todos os seus dados foram deletados.")
        return True
        
    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        return False