import os
import json
import datetime

def atualizar_base_nief():
    extensoes_alvo = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP')
    arquivos_na_pasta = os.listdir('.')
    
    fotos_encontradas = [f for f in arquivos_na_pasta if f.endswith(extensoes_alvo)]
    dados_imagens = []
    
    for f in fotos_encontradas:
        mtime = os.path.getmtime(f)
        data_formatada = datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y')
        
        nome_sem_ext = os.path.splitext(f)[0]
        partes = nome_sem_ext.split('_')
        
        naturezas = []
        
        if len(partes) >= 4:
            chassi = partes[0]
            # Restaura os espaços substituindo hífens por espaços na marca e modelo
            marca = partes[1].replace('-', ' ')
            modelo = partes[2].replace('-', ' ')
            ano = partes[3]
            
            # Se houver mais partes após o ano, são as naturezas/etiquetas
            if len(partes) > 4:
                for p in partes[4:]:
                    # Trata caso venha com hífens (ex: NIV-MOTOR) ou separado
                    sub_tags = p.replace('-', ' ').split(' ')
                    for st in sub_tags:
                        if st.strip():
                            naturezas.append(st.strip().upper())
        else:
            chassi = partes[0]
            marca = ""
            modelo = ""
            ano = ""
            
        dados_imagens.append({
            "arquivo": f,
            "chassi": chassi,
            "marca": marca,
            "modelo": modelo,
            "ano": ano,
            "natureza": naturezas,
            "data": data_formatada,
            "timestamp": mtime
        })
        
    dados_imagens.sort(key=lambda x: x["chassi"])

    nome_html = 'index.html'
    if not os.path.exists(nome_html):
        print(f"Erro: O arquivo {nome_html} não foi encontrado na pasta.")
        return

    with open(nome_html, 'r', encoding='utf-8') as f:
        conteudo = f.read()

    marcador_inicio = "const imagens ="
    marcador_fim = "];"

    try:
        pos_inicio = conteudo.find(marcador_inicio)
        pos_temp = conteudo.find(marcador_fim, pos_inicio)
        
        if pos_inicio == -1 or pos_temp == -1:
            print("Erro: Marcadores da variável 'const imagens = [...]' não encontrados no HTML.")
            return
            
        pos_fim = pos_temp + len(marcador_fim)

        lista_formatada = json.dumps(dados_imagens, indent=8, ensure_ascii=False)
        novo_trecho = f"const imagens = {lista_formatada};"

        novo_conteudo = conteudo[:pos_inicio] + novo_trecho + conteudo[pos_fim:]

        with open(nome_html, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)

        print(f"✓ Sucesso! {len(dados_imagens)} imagens foram indexadas e inseridas no sistema com suporte a web otimizado.")
        
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    atualizar_base_nief()