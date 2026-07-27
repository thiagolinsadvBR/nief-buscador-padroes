import os
from flask import Flask, request, jsonify, send_file

# Configura o Flask para servir os arquivos da pasta atual
app = Flask(__name__, static_folder='.', static_url_path='/fotos')

@app.route('/')
def index():
    # Carrega a interface visual
    return send_file('renomeador.html')

@app.route('/api/pendentes')
def pendentes():
    extensoes = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP')
    # Filtra arquivos que são imagens e que NÃO possuem underline no nome
    arquivos = [f for f in os.listdir('.') if f.endswith(extensoes) and '_' not in f]
    arquivos.sort()
    return jsonify(arquivos)

@app.route('/api/salvar', methods=['POST'])
def salvar():
    dados = request.json
    antigo = dados.get('antigo')
    ignorar = dados.get('ignorar', False)
    
    if not antigo or not os.path.exists(antigo):
        return jsonify({"status": "erro", "msg": "Arquivo não encontrado no diretório."}), 404
        
    nome_sem_ext, ext = os.path.splitext(antigo)
    
    if ignorar:
        # Marca como ignorado para não voltar a aparecer na lista
        novo_nome = f"{nome_sem_ext}_IGNORADO_X_X{ext}"
    else:
        # Formata o novo nome com os dados recebidos
        marca = dados.get('marca', '').strip()
        modelo = dados.get('modelo', '').strip()
        ano = dados.get('ano', '').strip()
        novo_nome = f"{nome_sem_ext}_{marca}_{modelo}_{ano}{ext}"
        
    try:
        os.rename(antigo, novo_nome)
        return jsonify({"status": "sucesso", "novo_nome": novo_nome})
    except Exception as e:
        return jsonify({"status": "erro", "msg": str(e)}), 500

if __name__ == '__main__':
    # Roda o servidor localmente na porta 5000
    app.run(debug=True, port=5000)