import os
import json

def atualizar_base_nief():
    # 1. Definir as extensões que queremos buscar
    # O script vai procurar por todas essas variações
    extensoes_alvo = ('.jpg', '.jpeg', '.png', '.webp', '.JPG', '.JPEG', '.PNG', '.WEBP')
    
    # 2. Listar os arquivos da pasta
    # O segredo aqui é pegar o nome EXATO do arquivo sem forçar minúsculas
    arquivos_na_pasta = os.listdir('.')
    
    # Filtra apenas os arquivos que terminam com as extensões permitidas
    fotos_encontradas = [f for f in arquivos_na_pasta if f.endswith(extensoes_alvo)]
    
    # Ordenar alfabeticamente para organizar a busca
    fotos_encontradas.sort()

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
        pos_fim = conteudo.find(marcador_fim, pos_inicio) + 2
        
        if pos_inicio == -1:
            print("Erro: Não encontrei o marcador '// LISTA DE ARQUIVOS' no seu HTML.")
            return

        # Converte a lista do Python para o formato de array do JavaScript
        lista_formatada = json.dumps(fotos_encontradas, indent=8, ensure_ascii=False)
        novo_trecho = f"{marcador_inicio}\n        const imagens = {lista_formatada};"

        # Monta o arquivo final
        novo_conteudo = conteudo[:pos_inicio] + novo_trecho + conteudo[pos_fim:]

        with open(nome_html, 'w', encoding='utf-8') as f:
            f.write(novo_conteudo)

        print(f"✓ Sucesso! {len(fotos_encontradas)} imagens foram indexadas com nomes exatos.")
        
    except Exception as e:
        print(f"Ocorreu um erro ao processar o arquivo: {e}")

if __name__ == "__main__":
    atualizar_base_nief()