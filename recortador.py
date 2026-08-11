import cv2
import numpy as np
import os

# Variáveis globais para armazenar os dados do estado atual
pontos = []
imagem_carregada_do_disco = None 
imagem_corrente_rotacionada = None 
imagem_exibicao_com_desenhos = None 

def ordenar_pontos(pts):
    """
    Ordena os 4 pontos selecionados para garantir a ordem correta na transformação matemática.
    A ordem final será: [superior-esquerdo, superior-direito, inferior-direito, inferior-esquerdo]
    """
    rect = np.zeros((4, 2), dtype="float32")
    
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect

def capturar_cliques(event, x, y, flags, param):
    """
    Função de callback do mouse. Captura as coordenadas X e Y onde o usuário clica.
    """
    global pontos, imagem_exibicao_com_desenhos, imagem_corrente_rotacionada

    if event == cv2.EVENT_LBUTTONDOWN:
        if len(pontos) < 4:
            pontos.append([x, y])
            cv2.circle(imagem_exibicao_com_desenhos, (x, y), 7, (0, 255, 0), -1)
            
            if len(pontos) > 1:
                cv2.line(imagem_exibicao_com_desenhos, tuple(pontos[-2]), tuple(pontos[-1]), (0, 255, 0), 2)
            
            if len(pontos) == 4:
                cv2.line(imagem_exibicao_com_desenhos, tuple(pontos[3]), tuple(pontos[0]), (0, 255, 0), 2)
                print("   [+] 4 pontos selecionados! Pressione 'Enter' para recortar.")
            
            cv2.imshow("NIEF - Seletor de Perspectiva", imagem_exibicao_com_desenhos)

def corrigir_perspectiva(imagem, pts):
    """
    Calcula e aplica a transformação de perspectiva para "achatar" a imagem.
    Força a saída a ser sempre horizontal.
    """
    rect = ordenar_pontos(pts)
    (tl, tr, br, bl) = rect

    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(imagem, M, (maxWidth, maxHeight))

    # =================================================================
    # NOVO: Validação Automática de Orientação (Forçar Horizontal)
    # Compara a altura (warped.shape[0]) com a largura (warped.shape[1])
    # =================================================================
    if warped.shape[0] > warped.shape[1]:
        # Gira 90 graus no sentido anti-horário para deitar a imagem
        warped = cv2.rotate(warped, cv2.ROTATE_90_COUNTERCLOCKWISE)
        print("   [*] Ajuste automático: Imagem vertical deitada para horizontal.")

    return warped

def main():
    global pontos, imagem_carregada_do_disco, imagem_corrente_rotacionada, imagem_exibicao_com_desenhos

    pasta_atual = os.getcwd()
    extensoes_validas = ('.jpg', '.jpeg', '.png')
    todos_arquivos = os.listdir(pasta_atual)
    
    arquivos_imagem = [
        f for f in todos_arquivos 
        if f.lower().endswith(extensoes_validas) and not f.lower().endswith('_recortada.jpg')
    ]

    if not arquivos_imagem:
        print("[-] Nenhuma imagem válida (não processada) encontrada na pasta atual.")
        return

    print("======================================================")
    print(" NIEF - PROCESSADOR DE FOTOS EM LOTE")
    print("======================================================")
    print(" INSTRUÇÕES:")
    print(" 1. ROTAÇÃO (Antes de clicar):")
    print("    Pressione 'D' para girar 90° HORÁRIO.")
    print("    Pressione 'A' para girar 90° ANTI-HORÁRIO.")
    print(" 2. EDIÇÃO:")
    print("    Clique nos 4 cantos em volta da numeração.")
    print("    Pressione 'Enter' para salvar e ir para a PRÓXIMA foto.")
    print(" 3. CONTROLES:")
    print("    Pressione 'r' para refazer a seleção da foto atual.")
    print("    Pressione 's' para pular (skip) a foto atual.")
    print("    Pressione 'q' para sair do programa.")
    print("------------------------------------------------------")
    print(f" Total de imagens a processar: {len(arquivos_imagem)}")
    print("======================================================")

    cv2.namedWindow("NIEF - Seletor de Perspectiva", cv2.WINDOW_NORMAL)
    cv2.setMouseCallback("NIEF - Seletor de Perspectiva", capturar_cliques)

    for index, nome_arquivo in enumerate(arquivos_imagem):
        caminho_imagem = os.path.join(pasta_atual, nome_arquivo)
        
        nome_base, _ = os.path.splitext(nome_arquivo)
        nome_saida = f"{nome_base}_recortada.jpg"
        caminho_saida = os.path.join(pasta_atual, nome_saida)

        imagem_carregada_do_disco = cv2.imread(caminho_imagem)
        
        if imagem_carregada_do_disco is None:
            print(f"[-] Erro ao carregar a imagem {nome_arquivo}. Pulando...")
            continue

        imagem_corrente_rotacionada = imagem_carregada_do_disco.copy()
        imagem_exibicao_com_desenhos = imagem_corrente_rotacionada.copy()
        pontos = [] 

        print(f"\n[{index + 1}/{len(arquivos_imagem)}] Processando: {nome_arquivo}")

        proxima_imagem = False
        while not proxima_imagem:
            cv2.imshow("NIEF - Seletor de Perspectiva", imagem_exibicao_com_desenhos)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord("d") or key == ord("a"):
                if key == ord("d"):
                    imagem_corrente_rotacionada = cv2.rotate(imagem_corrente_rotacionada, cv2.ROTATE_90_CLOCKWISE)
                    print("   [*] Girado 90° Horário. Seleção de pontos zerada.")
                else:
                    imagem_corrente_rotacionada = cv2.rotate(imagem_corrente_rotacionada, cv2.ROTATE_90_COUNTERCLOCKWISE)
                    print("   [*] Girado 90° Anti-horário. Seleção de pontos zerada.")
                
                imagem_exibicao_com_desenhos = imagem_corrente_rotacionada.copy()
                pontos = []

            elif key == 13: 
                if len(pontos) == 4:
                    pts = np.array(pontos, dtype="float32")
                    recorte = corrigir_perspectiva(imagem_corrente_rotacionada, pts)
                    
                    cv2.imwrite(caminho_saida, recorte)
                    print(f"   [+] Sucesso! Salvo como: {nome_saida}")
                    proxima_imagem = True 
                else:
                    print("   [-] Atenção: Selecione exatamente 4 pontos antes de apertar Enter.")

            elif key == ord("r"):
                imagem_exibicao_com_desenhos = imagem_corrente_rotacionada.copy()
                pontos = []
                print("   [*] Seleção de pontos reiniciada.")

            elif key == ord("s"):
                print("   [*] Imagem pulada pelo usuário.")
                proxima_imagem = True

            elif key == ord("q"):
                print("\n[*] Processo encerrado pelo usuário. Saindo...")
                cv2.destroyAllWindows()
                return 

    print("\n[+] Ótimo trabalho! Todas as imagens foram processadas.")
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()