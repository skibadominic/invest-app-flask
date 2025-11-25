from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages, session
from datetime import datetime 
import database
import usuarios 
import ativos 
import carteira
import buscador 
import gerador_grafico 
import calculadora
import metas

app = Flask(__name__, static_folder='static')
app.secret_key = "fP$92wK@z_qXv*8jN" 

database.iniciar_banco()

@app.route("/")
def homepage():
    return render_template("index.html")

@app.route("/cadastro", methods=["GET", "POST"])
def rota_cadastro():
    if request.method == "POST":
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        sucesso = usuarios.cadastrar_usuario(nome, email, senha)
        
        if sucesso:
            flash(f"Bem-vindo, {nome}! Sua conta foi criada com sucesso.", "success")
            usuario_logado = usuarios.login(email, senha)
            session['id_usuario'] = usuario_logado['id']
            session['email_usuario'] = usuario_logado['email']
            session['nome_usuario'] = usuario_logado['nome'] 
            session['perfil_usuario'] = usuario_logado['perfil'] 
            return redirect(url_for("dashboard"))
        else:
            flash("Erro ao cadastrar: e-mail inválido ou já em uso.", "error")
            return redirect(url_for("rota_cadastro"))
            
    return render_template("cadastro.html")

@app.route("/login", methods=["GET", "POST"])
def rota_login():
    messages = get_flashed_messages() 
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']
        usuario_logado = usuarios.login(email, senha)
        if usuario_logado:
            session['id_usuario'] = usuario_logado['id']
            session['email_usuario'] = usuario_logado['email']
            session['nome_usuario'] = usuario_logado['nome'] 
            session['perfil_usuario'] = usuario_logado['perfil'] 
            return redirect(url_for("dashboard"))
        else:
            flash("E-mail ou senha incorretos.", "error")
            return redirect(url_for("rota_login"))
    return render_template("login.html", messages=messages)

@app.route("/logout")
def rota_logout():
    session.pop('id_usuario', None)
    session.pop('email_usuario', None)
    session.pop('nome_usuario', None) 
    session.pop('perfil_usuario', None) 
    flash("Você foi desconectado.", "info")
    return redirect(url_for("rota_login"))

@app.route("/dashboard")
def dashboard():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para ver esta página.", "error")
        return redirect(url_for("rota_login"))
    
    nome = session['nome_usuario']
    perfil = session.get('perfil_usuario', None) 
    
    return render_template("dashboard.html", nome_usuario=nome, perfil_usuario=perfil)

@app.route("/quiz", methods=["GET", "POST"])
def rota_quiz():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para fazer o quiz.", "error")
        return redirect(url_for("rota_login"))
        
    id_usuario_logado = session['id_usuario']

    if request.method == "POST":
        try:
            p1_str = request.form.get('p1')
            p2_str = request.form.get('p2')
            p3_str = request.form.get('p3')
            p4_str = request.form.get('p4')
            p5_str = request.form.get('p5')

            if p1_str is None or p2_str is None or p3_str is None or p4_str is None or p5_str is None:
                flash("Você precisa responder TODAS as 5 perguntas.", "error")
                return redirect(url_for("rota_quiz"))

            pontos_p1 = int(p1_str)
            pontos_p2 = int(p2_str)
            pontos_p3 = int(p3_str)
            pontos_p4 = int(p4_str)
            pontos_p5 = int(p5_str)
            
            pontos_total = pontos_p1 + pontos_p2 + pontos_p3 + pontos_p4 + pontos_p5
            
            resultado_perfil = None
            if pontos_total <= 8: 
                resultado_perfil = "Conservador"
            elif pontos_total <= 12: 
                resultado_perfil = "Moderado"
            else: 
                resultado_perfil = "Arrojado"
            
            usuarios.atualizar_perfil(id_usuario_logado, resultado_perfil)
            session['perfil_usuario'] = resultado_perfil
            
            flash(f"Quiz concluído! Seu novo perfil é: {resultado_perfil}", "success")
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash(f"Ocorreu um erro ao processar seu quiz: {e}", "error")
            return redirect(url_for("rota_quiz"))

    return render_template("quiz.html")

@app.route("/carteira")
def rota_carteira():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para ver esta página.", "error")
        return redirect(url_for("rota_login"))
        
    id_usuario_logado = session['id_usuario']
    
    posicoes, total_invest, valor_atual, lucro_total = calculadora.calcular_desempenho_carteira(id_usuario_logado)
    
    return render_template("carteira.html", 
                           posicoes=posicoes, 
                           total_investido=total_invest,
                           valor_atual_total=valor_atual,
                           lucro_prejuizo_total=lucro_total)

@app.route("/acoes", methods=["GET", "POST"])
def rota_acoes():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para ver esta página.", "error")
        return redirect(url_for("rota_login"))
    
    lista_de_acoes = []
    
    if request.method == "POST":
        nome_empresa = request.form['nome_empresa']
        lista_de_acoes = buscador.buscar_ticker_por_nome(nome_empresa)
    else:
        lista_de_acoes = buscador.get_todos_os_tickers()
    
    return render_template("acoes.html", acoes=lista_de_acoes)

@app.route("/acao/<string:ticker_simbolo>", methods=["GET", "POST"])
def rota_acao_detalhe(ticker_simbolo):
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para ver esta página.", "error")
        return redirect(url_for("rota_login"))
    
    id_usuario_logado = session['id_usuario']
    
    ativo_info = ativos.get_or_create_ativo_by_ticker(ticker_simbolo)
    
    if not ativo_info:
        flash("Ativo não encontrado ou inválido.", "error")
        return redirect(url_for("rota_acoes"))

    if request.method == "POST":
        try:
            valor_investido_str = request.form['valor_investido']
            data_compra_str = request.form['data_compra']
            
            hoje = datetime.now().date()
            data_compra_obj = datetime.strptime(data_compra_str, '%Y-%m-%d').date()

            if data_compra_obj > hoje:
                flash("Erro: A data da compra não pode ser uma data futura.", "error")
                return redirect(url_for("rota_acao_detalhe", ticker_simbolo=ticker_simbolo))
                
            if float(valor_investido_str) <= 0:
                 flash("Erro: O valor investido deve ser maior que zero.", "error")
                 return redirect(url_for("rota_acao_detalhe", ticker_simbolo=ticker_simbolo))

            id_ativo_db = ativo_info['id']
            
            sucesso = carteira.adicionar_posicao(id_usuario_logado, id_ativo_db, valor_investido_str, data_compra_str, None, None)
            
            if sucesso:
                flash("Ação adicionada à carteira com sucesso!", "success")
                return redirect(url_for("rota_carteira"))
            else:
                flash("Erro ao adicionar ação.", "error")
                return redirect(url_for("rota_acao_detalhe", ticker_simbolo=ticker_simbolo))
                
        except Exception as e:
            flash(f"Erro ao processar: {e}", "error")
            return redirect(url_for("rota_acao_detalhe", ticker_simbolo=ticker_simbolo))

    caminho_grafico = gerador_grafico.gerar_grafico_anual(ativo_info['ticker'])
    
    return render_template("acao_detalhe.html", ativo=ativo_info, caminho_grafico=caminho_grafico)

@app.route("/editar/<int:id_posicao>", methods=["GET", "POST"])
def rota_editar_posicao(id_posicao):
    if 'id_usuario' not in session:
        return redirect(url_for("rota_login"))
    
    id_usuario = session['id_usuario']
    posicao_atual = carteira.get_posicao_por_id(id_posicao, id_usuario)
    
    if not posicao_atual:
        flash("Investimento não encontrado.", "error")
        return redirect(url_for("rota_carteira"))

    if request.method == "POST":
        try:
            valor = request.form['valor_investido']
            data = request.form['data_compra']
            
            hoje = datetime.now().date()
            data_obj = datetime.strptime(data, '%Y-%m-%d').date()
            if data_obj > hoje:
                flash("Erro: Data futura não permitida.", "error")
                return redirect(url_for("rota_editar_posicao", id_posicao=id_posicao))

            sucesso = carteira.editar_posicao(id_posicao, id_usuario, valor, data)
            
            if sucesso:
                flash("Investimento atualizado com sucesso!", "success")
                return redirect(url_for("rota_carteira"))
            else:
                flash("Erro ao atualizar.", "error")
                
        except ValueError:
            flash("Valores inválidos.", "error")

    return render_template("editar_posicao.html", posicao=posicao_atual)

@app.route("/vender_posicao/<int:id_posicao>")
def rota_vender_posicao(id_posicao):
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para ver esta página.", "error")
        return redirect(url_for("rota_login"))
        
    id_usuario_logado = session['id_usuario']
    
    sucesso = carteira.deletar_posicao_web(id_posicao, id_usuario_logado)
    
    if sucesso:
        flash("Posição vendida com sucesso!", "success")
    else:
        flash("Erro ao vender posição.", "error")
        
    return redirect(url_for("rota_carteira"))

@app.route("/adicionar_investimento")
def rota_adicionar_investimento():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para ver esta página.", "error")
        return redirect(url_for("rota_login"))
    return render_template("adicionar_investimento.html")

@app.route("/adicionar_renda_fixa", methods=["GET", "POST"])
def rota_adicionar_renda_fixa():
    if 'id_usuario' not in session:
        flash("Você precisa estar logado para ver esta página.", "error")
        return redirect(url_for("rota_login"))
        
    id_usuario_logado = session['id_usuario']
    
    if request.method == "POST":
        try:
            nome = request.form['nome']
            tipo = request.form['tipo']
            perfil_alvo = request.form['perfil_alvo']
            tipo_rendimento = request.form['tipo_rendimento']
            taxa_str = request.form['taxa']
            valor_investido_str = request.form['valor_investido']
            data_compra_str = request.form['data_compra']
            
            hoje = datetime.now().date()
            data_compra_obj = datetime.strptime(data_compra_str, '%Y-%m-%d').date()
            
            if data_compra_obj > hoje:
                flash("Erro: A data da compra não pode ser uma data futura.", "error")
                return redirect(url_for("rota_adicionar_renda_fixa"))
                
            if float(valor_investido_str) <= 0 or float(taxa_str) <= 0:
                 flash("Erro: O valor investido e a taxa devem ser maiores que zero.", "error")
                 return redirect(url_for("rota_adicionar_renda_fixa"))

            if tipo_rendimento == 'POS':
                api_online = calculadora.verificar_api_bcb()
                if not api_online:
                    flash("Problemas ao se conectar com a API do Banco Central. Tente novamente mais tarde.", "error")
                    return redirect(url_for("rota_adicionar_renda_fixa"))

            id_ativo_db = ativos.get_or_create_ativo_manual(nome, tipo, perfil_alvo)
            
            if not id_ativo_db:
                flash("Erro ao salvar o 'template' do ativo.", "error")
                return redirect(url_for("rota_adicionar_renda_fixa"))

            sucesso = carteira.adicionar_posicao(id_usuario_logado, id_ativo_db, valor_investido_str, data_compra_str, tipo_rendimento, taxa_str)
            
            if sucesso:
                flash(f"{tipo} '{nome}' adicionado à carteira!", "success")
                return redirect(url_for("rota_carteira"))
            else:
                flash("Erro ao adicionar posição na carteira.", "error")
                return redirect(url_for("rota_adicionar_renda_fixa"))

        except Exception as e:
            flash(f"Erro ao processar: {e}", "error")
            return redirect(url_for("rota_adicionar_renda_fixa"))
            
    return render_template("adicionar_renda_fixa.html")

@app.route("/deletar_conta")
def rota_deletar_conta():
    if 'id_usuario' not in session:
        return redirect(url_for("rota_login"))
    
    id_usuario = session['id_usuario']
    
    sucesso = usuarios.deletar_usuario_completo(id_usuario)
    
    if sucesso:
        session.clear()
        flash("Sua conta e seus dados foram excluídos permanentemente.", "success")
        return redirect(url_for("homepage"))
    else:
        flash("Ocorreu um erro ao tentar excluir sua conta.", "error")
        return redirect(url_for("dashboard"))

@app.route("/metas", methods=["GET", "POST"])
def rota_metas():
    if 'id_usuario' not in session:
        return redirect(url_for("rota_login"))
    
    id_usuario = session['id_usuario']

    if request.method == "POST":
        titulo = request.form['titulo']
        valor = request.form['valor_alvo']
        data = request.form['data_limite']
        
        if metas.criar_meta(id_usuario, titulo, valor, data):
            flash("Meta criada com sucesso!", "success")
        else:
            flash("Erro ao criar meta.", "error")
        return redirect(url_for("rota_metas"))

    lista_metas = metas.listar_metas(id_usuario)
    return render_template("metas.html", metas=lista_metas)

@app.route("/editar_meta/<int:id_meta>", methods=["GET", "POST"])
def rota_editar_meta(id_meta):
    if 'id_usuario' not in session:
        return redirect(url_for("rota_login"))
    
    id_usuario = session['id_usuario']

    if request.method == "POST":
        titulo = request.form['titulo']
        valor = request.form['valor_alvo']
        data = request.form['data_limite']
        
        if metas.editar_meta(id_meta, id_usuario, titulo, valor, data):
            flash("Meta atualizada!", "success")
            return redirect(url_for("rota_metas"))
        else:
            flash("Erro ao atualizar.", "error")

    meta_atual = metas.get_meta_por_id(id_meta, id_usuario)
    return render_template("editar_meta.html", meta=meta_atual)

@app.route("/deletar_meta/<int:id_meta>")
def rota_deletar_meta(id_meta):
    if 'id_usuario' not in session:
        return redirect(url_for("rota_login"))
    
    if metas.deletar_meta(id_meta, session['id_usuario']):
        flash("Meta excluída.", "success")
    else:
        flash("Erro ao excluir.", "error")
        
    return redirect(url_for("rota_metas"))

if __name__ == "__main__":
    app.run(debug=True)