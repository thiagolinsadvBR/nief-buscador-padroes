import os
import json
import datetime

def atualizar_base_nief():
    try:
        print("Iniciando gerador de galeria...")
        
        # GARANTIA 1: Força o script a rodar na exata pasta onde ele está salvo
        pasta_script = os.path.dirname(os.path.abspath(__file__))
        os.chdir(pasta_script)
        print(f"Pasta de trabalho: {pasta_script}")
        
        extensoes_alvo = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP')
        arquivos_na_pasta = os.listdir('.')
        
        fotos_encontradas = [f for f in arquivos_na_pasta if f.endswith(extensoes_alvo)]
        print(f"Fotos encontradas na pasta: {len(fotos_encontradas)}")
        
        if len(fotos_encontradas) == 0:
            print("ERRO: Nenhuma foto foi encontrada nesta pasta.")
            input("\nPressione ENTER para fechar...")
            return

        dados_imagens = []
        tags_conhecidas = ["NIV", "MOTOR", "ETIQUETA", "PLAQUETA", "CÂMBIO", "VIS", "CHAPA", "PAINEL", "PORTA", "VIDRO"]

        for f in fotos_encontradas:
            mtime = os.path.getmtime(f)
            data_formatada = datetime.datetime.fromtimestamp(mtime).strftime('%d/%m/%Y')
            
            nome_sem_ext = os.path.splitext(f)[0]
            nome_norm = nome_sem_ext.replace('-', ' ')
            partes = nome_norm.split('_')
            
            naturezas = []
            chassi = ""
            marca = ""
            modelo = ""
            ano = ""

            if len(partes) >= 4:
                chassi = partes[0].strip()
                marca = partes[1].strip()
                modelo = partes[2].strip()
                
                bloco_final = partes[3].strip()
                pedacos_ano = bloco_final.split(' ')
                ano = pedacos_ano[0] 
                
                if len(pedacos_ano) > 1:
                    for p in pedacos_ano[1:]:
                        if p.upper() in tags_conhecidas:
                            naturezas.append(p.upper())
                            
                if len(partes) > 4:
                    for p in partes[4:]:
                        for s in p.split(' '):
                            if s.upper() in tags_conhecidas:
                                naturezas.append(s.upper())
            else:
                pedacos = nome_norm.split(' ')
                chassi_parts = []
                for p in pedacos:
                    if p.upper() in tags_conhecidas:
                        naturezas.append(p.upper())
                    else:
                        chassi_parts.append(p)
                chassi = " ".join(chassi_parts).replace('_', '').strip()

            if not chassi:
                chassi = "NÚMERO NÃO CADASTRADO"

            naturezas_unicas = list(dict.fromkeys(naturezas))

            dados_imagens.append({
                "arquivo": f,
                "chassi": chassi,
                "marca": marca,
                "modelo": modelo,
                "ano": ano,
                "natureza": naturezas_unicas,
                "data": data_formatada,
                "timestamp": mtime
            })
            
        dados_imagens.sort(key=lambda x: x["chassi"])

        nome_html = 'index.html'
        if not os.path.exists(nome_html):
            print(f"ERRO: O arquivo {nome_html} não foi encontrado na pasta {pasta_script}.")
            input("\nPressione ENTER para fechar...")
            return

        with open(nome_html, 'r', encoding='utf-8') as f_html:
            conteudo = f_html.read()

        marcador_inicio = "const imagens ="
        marcador_fim = "];"

        pos_inicio = conteudo.find(marcador_inicio)
        pos_temp = conteudo.find(marcador_fim, pos_inicio)
        
        if pos_inicio == -1 or pos_temp == -1:
            print("ERRO: O robô não conseguiu achar a tag 'const imagens = [];' dentro do seu HTML.")
            print("Isso geralmente ocorre se o HTML foi apagado incorretamente.")
            input("\nPressione ENTER para fechar...")
            return
            
        pos_fim = pos_temp + len(marcador_fim)
        
        lista_formatada = json.dumps(dados_imagens, indent=8, ensure_ascii=False)
        novo_trecho = f"const imagens = {lista_formatada};"
        
        novo_conteudo = conteudo[:pos_inicio] + novo_trecho + conteudo[pos_fim:]

        with open(nome_html, 'w', encoding='utf-8') as f_html:
            f_html.write(novo_conteudo)

        print(f"\n✓ SUCESSO! {len(dados_imagens)} imagens foram injetadas no arquivo index.html.")
        input("\nPressione ENTER para finalizar e fechar...")

    except Exception as e:
        print(f"\nOCORREU UM ERRO GRAVE: {e}")
        input("\nPressione ENTER para fechar...")

if __name__ == "__main__":
    atualizar_base_nief()