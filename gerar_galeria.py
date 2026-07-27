import os
import json
import datetime

def atualizar_base_nief():
    # 1. Definir as extensões que queremos buscar
    extensoes_alvo = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP')
    arquivos_na_pasta = os.listdir('.')
    
    # Filtra apenas os arquivos de imagem
    fotos_encontradas = [f for f in arquivos_na_pasta if f.endswith(extensoes_alvo)]
    
    dados_imagens = []
    
    for f in fotos_encontradas:
        # Pega a data de modificação/criação do arquivo no sistema operacional
        mtime = os.path.getmtime(f)
        data_formatada = datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y')
        
        # Remove a extensão para processar os dados
        nome_sem_ext = os.path.splitext(f)[0]
        
        # Divide o nome usando o underline "_"
        partes = nome_sem_ext.split('_')
        
        # Se tiver as 4 partes (Chassi, Marca, Modelo, Ano)
        if len(partes) >= 4:
            chassi = partes[0]
            marca = partes[1]
            modelo = partes[2]
            ano = partes[3]
        else:
            # Arquivo antigo (sem underline)
            chassi = partes[0]
            marca = ""
            modelo = ""
            ano = ""
            
        # Adiciona os metadados no nosso dicionário
        dados_imagens.append({
            "arquivo": f,
            "chassi": chassi,
            "marca": marca,
            "modelo": modelo,
            "ano": ano,
            "data": data_formatada,
            "timestamp": mtime # Guardamos o timestamp real para ordenar no JavaScript
        })
        
    # Ordena alfabeticamente pelo chassi para organizar a visualização padrão
    dados_imagens.sort(key=lambda x: x["chassi"])

    # 3. Ler o arquivo index.html
    nome_html = 'index.html'
    if not os.path.exists(nome_html):
        print(f"Erro: O arquivo {nome_html} não foi encontrado na pasta.")
        return

    with open(nome_html, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    # 4. Localizar e substituir a lista de imagens no JavaScript
    marcador_inicio = "// LISTA DE ARQUIVOS"
    marcador_fim = "];"

    try:
        pos_inicio = conteudo.find(marcador_inicio)
        # Encontra o próximo ]; que fecha a lista logo após o marcador
        pos_temp = conteudo.find(marcador_fim, pos_inicio)
        
        if pos_inicio == -1 or pos_temp == -1:
            print("Erro: Marcador '// LISTA DE ARQUIVOS' ou o fechamento '];' não encontrados no HTML.")
            return
            
        pos_fim = pos_temp + 2 # Pega a posição logo após o ponto e vírgula

        # Converte a lista de objetos do Python para array JSON legível no JavaScript
        lista_formatada = json.dumps(dados_imagens, indent=8, ensure_ascii=False)
        novo_trecho = f"{marcador_inicio}\n        const imagens = {lista_formatada};"

        # Monta o arquivo final
        novo_conteudo = conteudo[:pos_inicio] + novo_trecho + conteudo[pos_fim:]

        with open(nome_html, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)

        print(f"✓ Sucesso! {len(dados_imagens)} imagens foram indexadas com metadados estruturados.")
        
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    atualizar_base_nief()