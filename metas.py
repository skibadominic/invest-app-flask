import sqlite3
import database

def criar_meta(id_usuario, titulo, valor_alvo, data_limite):
    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        cursor.execute("INSERT INTO metas (id_usuario, titulo, valor_alvo, data_limite) VALUES (?, ?, ?, ?)",
                       (id_usuario, titulo, float(valor_alvo), data_limite))
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"Erro ao criar meta: {e}")
        return False

def listar_metas(id_usuario):
    db = sqlite3.connect(database.DB_NOME)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM metas WHERE id_usuario = ?", (id_usuario,))
    metas = cursor.fetchall()
    db.close()
    return metas

def get_meta_por_id(id_meta, id_usuario):
    db = sqlite3.connect(database.DB_NOME)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute("SELECT * FROM metas WHERE id = ? AND id_usuario = ?", (id_meta, id_usuario))
    meta = cursor.fetchone()
    db.close()
    return meta

def editar_meta(id_meta, id_usuario, titulo, valor_alvo, data_limite):
    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        cursor.execute("""
            UPDATE metas SET titulo = ?, valor_alvo = ?, data_limite = ?
            WHERE id = ? AND id_usuario = ?
        """, (titulo, float(valor_alvo), data_limite, id_meta, id_usuario))
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"Erro ao editar meta: {e}")
        return False

def deletar_meta(id_meta, id_usuario):
    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        cursor.execute("DELETE FROM metas WHERE id = ? AND id_usuario = ?", (id_meta, id_usuario))
        db.commit()
        db.close()
        return True
    except Exception as e:
        print(f"Erro ao deletar meta: {e}")
        return False