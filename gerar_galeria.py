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
        
        naturezas = []
        
        # Se tiver as 4 partes (Chassi, Marca, Modelo, Ano)
        if len(partes) >= 4:
            chassi = partes[0]
            marca = partes[1]
            modelo = partes[2]
            
            # O último bloco pode ter espaços, ex: "2024 NIV VIS"
            ano_bruto = partes[3]
            pedacos_ano = ano_bruto.split(' ')
            ano = pedacos_ano[0] # O primeiro item é sempre o ano
            
            # O que vier depois do ano são as naturezas (se o classificador foi usado)
            if len(pedacos_ano) > 1:
                naturezas = pedacos_ano[1:] # Pega do segundo item em diante
                
        else:
            # Arquivo antigo (sem underline)
            chassi = partes[0]
            marca = ""
            modelo = ""
            ano = ""
            
        # Adiciona os metadados no nosso dicionário (AGORA COM NATUREZA)
        dados_imagens.append({
            "arquivo": f,
            "chassi": chassi,
            "marca": marca,
            "modelo": modelo,
            "ano": ano,
            "natureza": naturezas,
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

    # 4. Localizar e substituir a lista de imagens
    marcador_inicio = "const imagens ="
    marcador_fim = "];"

    try:
        pos_inicio = conteudo.find(marcador_inicio)
        # Encontra o próximo ]; que fecha a lista logo após o marcador
        pos_temp = conteudo.find(marcador_fim, pos_inicio)
        
        if pos_inicio == -1 or pos_temp == -1:
            print("Erro: Marcadores da variável 'const imagens = [...]' não encontrados no HTML.")
            return
            
        pos_fim = pos_temp + len(marcador_fim) # Pega a posição exata após o ];

        # Converte a lista de objetos do Python para array JSON legível no JavaScript
        lista_formatada = json.dumps(dados_imagens, indent=8, ensure_ascii=False)
        
        # Monta a nova declaração da variável completa
        novo_trecho = f"const imagens = {lista_formatada};"

        # Monta o arquivo final injetando os novos dados na posição exata
        novo_conteudo = conteudo[:pos_inicio] + novo_trecho + conteudo[pos_fim:]

        with open(nome_html, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)

        print(f"✓ Sucesso! {len(dados_imagens)} imagens foram indexadas e inseridas no novo sistema restrito.")
        
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    atualizar_base_nief()