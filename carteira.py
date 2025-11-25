import sqlite3
import database
import ativos

def adicionar_posicao(id_usuario_logado, id_ativo_comprado, valor_investido, data_compra, tipo_rendimento, taxa):
    try:
        valor_final = float(valor_investido)
        id_user_final = int(id_usuario_logado)
        id_ativo_final = int(id_ativo_comprado)
        
        if taxa and taxa != '':
            taxa_final = float(taxa)
        else:
            taxa_final = None
            
    except ValueError:
        print("[ERRO] Valor ou taxa não são números válidos.")
        return False
    
    if not data_compra:
        print("[ERRO] Data não pode ser vazia.")
        return False

    if not tipo_rendimento:
        tipo_rendimento = None

    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        
        sql_insert = """
        INSERT INTO posicoes (id_usuario, id_ativo, valor_investido, data_compra, tipo_rendimento, taxa)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        
        cursor.execute(sql_insert, (id_user_final, id_ativo_final, valor_final, data_compra, tipo_rendimento, taxa_final))
        
        db.commit()
        db.close()
        
        print("[SUCESSO] Ativo adicionado à carteira!")
        return True
        
    except Exception as e:
        print(f"[ERRO] Não foi possível adicionar o ativo: {e}")
        return False
          
def deletar_posicao_web(id_posicao, id_usuario_logado):
    
    try:
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        sql_delete = "DELETE FROM posicoes WHERE id = ? AND id_usuario = ?"
        
        cursor.execute(sql_delete, (id_posicao, id_usuario_logado))
        
        if cursor.rowcount == 0:
            print("Falha ao deletar: Posição não encontrada ou não pertence ao usuário.")
            db.close()
            return False
        else:
            db.commit()
            db.close()
            print("Sucesso: Posição deletada.")
            return True
            
    except Exception as e:
        print(f"Erro ao deletar posição: {e}")
        return False

def get_posicao_por_id(id_posicao, id_usuario):
    db = sqlite3.connect(database.DB_NOME)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    
    sql = """
    SELECT posicoes.*, ativos.nome, ativos.tipo 
    FROM posicoes 
    JOIN ativos ON posicoes.id_ativo = ativos.id
    WHERE posicoes.id = ? AND posicoes.id_usuario = ?
    """
    cursor.execute(sql, (id_posicao, id_usuario))
    posicao = cursor.fetchone()
    db.close()
    return posicao

def editar_posicao(id_posicao, id_usuario, valor_investido, data_compra):
    try:
        val_final = float(valor_investido)
        
        db = sqlite3.connect(database.DB_NOME)
        cursor = db.cursor()
        
        sql = """
        UPDATE posicoes 
        SET valor_investido = ?, data_compra = ?
        WHERE id = ? AND id_usuario = ?
        """
        
        cursor.execute(sql, (val_final, data_compra, id_posicao, id_usuario))
        
        if cursor.rowcount == 0:
            db.close()
            return False
            
        db.commit()
        db.close()
        return True
        
    except Exception as e:
        print(f"Erro ao editar posição: {e}")
        return False