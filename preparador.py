import os
import sys
import traceback

# =========================================================
# BLINDAGEM DE INICIALIZAÇÃO
# Captura erros de bibliotecas não instaladas e trava a tela
# =========================================================
try:
    import re
    import cv2
    import numpy as np
    import tkinter as tk
    from tkinter import filedialog, messagebox
    from PIL import Image, ImageTk
except ImportError as e:
    print("\n" + "="*70)
    print("🚨 ERRO FATAL: BIBLIOTECA NÃO ENCONTRADA 🚨")
    print("="*70)
    print(f"Detalhe do erro: {e}")
    print("\nO seu computador está sem algumas ferramentas necessárias para")
    print("rodar a manipulação de imagens (OpenCV / Numpy).")
    print("\nPara corrigir, abra o 'Prompt de Comando' (CMD) e digite:")
    print("👉 pip install opencv-python numpy pillow")
    print("\n" + "="*70)
    input("Pressione ENTER para fechar esta tela...")
    sys.exit()
except Exception as e:
    print("\n" + "="*70)
    print("🚨 ERRO INESPERADO AO CARREGAR O PROGRAMA 🚨")
    print("="*70)
    traceback.print_exc()
    input("\nPressione ENTER para fechar esta tela...")
    sys.exit()

class UnificadorIDV:
    def __init__(self, root):
        self.root = root
        self.root.title("NIEF - Estação Unificada de Processamento (Recorte + IDV + Tags)")
        self.root.geometry("1100x900")
        
        # Cores padronizadas do sistema
        self.cor_fundo = "#1a1a1a"
        self.cor_painel = "#252525"
        self.cor_texto = "#ffffff"
        self.cor_destaque = "#7CFC00"
        self.cor_borda = "#444444"
        self.cor_alerta = "#ff4444"
        self.cor_canvas = "#111111"
        
        self.root.configure(bg=self.cor_fundo)
        
        # Variáveis de Estado de Arquivo
        self.pasta_origem = ""
        self.pasta_destino = os.getcwd() # Salva na pasta onde o script está rodando
        self.lista_fotos = []
        self.indice_atual = 0
        
        # Variáveis de Estado de Imagem (OpenCV / PIL)
        self.imagem_cv_original = None
        self.imagem_cv_exibicao = None
        self.imagem_cv_recortada = None
        self.escala_canvas = 1.0
        self.offset_x = 0
        self.offset_y = 0
        
        # Variáveis do Recortador
        self.pontos_canvas = []
        self.ponto_arrastado = None
        self.estado_app = "RECORTANDO" # "RECORTANDO" ou "PREENCHENDO"
        
        # Dicionários de Dados
        self.mapa_anos = {
            '1': '2001', '2': '2002', '3': '2003', '4': '2004', '5': '2005',
            '6': '2006', '7': '2007', '8': '2008', '9': '2009', 'A': '2010',
            'B': '2011', 'C': '2012', 'D': '2013', 'E': '2014', 'F': '2015',
            'G': '2016', 'H': '2017', 'J': '2018', 'K': '2019', 'L': '2020',
            'M': '2021', 'N': '2022', 'P': '2023', 'R': '2024', 'S': '2025',
            'T': '2026', 'V': '1997', 'W': '1998', 'X': '1999', 'Y': '2000'
        }
        
        self.opcoes_tags = ["NIV", "MOTOR", "ETIQUETA", "PLAQUETA", "CÂMBIO", "VIS"]
        self.selecoes_tags = {}
        
        self.construir_interface()
        self.configurar_eventos()
        
    def construir_interface(self):
        # ---------------------------------------------------------
        # TOPO (Seleção de Pasta e Status)
        # ---------------------------------------------------------
        frame_topo = tk.Frame(self.root, bg=self.cor_painel, pady=10, padx=20, highlightbackground=self.cor_borda, highlightthickness=1)
        frame_topo.pack(fill=tk.X, padx=20, pady=10)
        
        self.btn_selecionar = tk.Button(
            frame_topo, text="📁 Selecionar Pasta de Imagens", font=("Segoe UI", 11, "bold"),
            bg="#111111", fg=self.cor_destaque, activebackground=self.cor_destaque, activeforeground="#111111",
            relief=tk.FLAT, borderwidth=1, highlightbackground=self.cor_destaque, highlightthickness=1,
            cursor="hand2", command=self.selecionar_pasta, padx=15, pady=5
        )
        self.btn_selecionar.pack(side=tk.LEFT)
        
        self.lbl_status_app = tk.Label(frame_topo, text="PASSO 1: Selecione a pasta de trabalho", font=("Segoe UI", 12, "bold"), bg=self.cor_painel, fg=self.cor_destaque)
        self.lbl_status_app.pack(side=tk.LEFT, expand=True)

        self.lbl_progresso = tk.Label(frame_topo, text="Fila: 0/0", font=("Segoe UI", 11, "bold"), bg=self.cor_painel, fg=self.cor_texto)
        self.lbl_progresso.pack(side=tk.RIGHT)
        
        # ---------------------------------------------------------
        # CENTRO (Prancheta de Imagem - Canvas Interativo)
        # ---------------------------------------------------------
        self.frame_imagem = tk.Frame(self.root, bg=self.cor_fundo)
        self.frame_imagem.pack(expand=True, fill=tk.BOTH, padx=20, pady=5)
        
        self.lbl_nome_arquivo = tk.Label(self.frame_imagem, text="", font=("Segoe UI", 10, "italic"), bg=self.cor_fundo, fg="#aaaaaa")
        self.lbl_nome_arquivo.pack()

        # Canvas para desenho interativo
        self.canvas_w = 900
        self.canvas_h = 450
        self.canvas = tk.Canvas(self.frame_imagem, width=self.canvas_w, height=self.canvas_h, bg=self.cor_canvas, highlightthickness=0, cursor="crosshair")
        self.canvas.pack(pady=5)
        
        # Botões de controle da imagem (Substituem os atalhos do teclado)
        frame_controles_img = tk.Frame(self.frame_imagem, bg=self.cor_fundo)
        frame_controles_img.pack(pady=5)
        
        self.btn_girar_esq = tk.Button(
            frame_controles_img, text="⟲ Girar Esq.", font=("Segoe UI", 9, "bold"),
            bg="#333333", fg=self.cor_texto, relief=tk.FLAT, cursor="hand2",
            command=lambda: self.rotacionar_imagem(cv2.ROTATE_90_COUNTERCLOCKWISE)
        )
        self.btn_girar_esq.pack(side=tk.LEFT, padx=5)
        
        self.btn_girar_dir = tk.Button(
            frame_controles_img, text="⟳ Girar Dir.", font=("Segoe UI", 9, "bold"),
            bg="#333333", fg=self.cor_texto, relief=tk.FLAT, cursor="hand2",
            command=lambda: self.rotacionar_imagem(cv2.ROTATE_90_CLOCKWISE)
        )
        self.btn_girar_dir.pack(side=tk.LEFT, padx=5)
        
        self.btn_desfazer = tk.Button(
            frame_controles_img, text="↩️ Desfazer Recorte", font=("Segoe UI", 9, "bold"),
            bg="#333333", fg=self.cor_alerta, relief=tk.FLAT, cursor="hand2",
            command=self.desfazer_recorte
        )
        self.btn_desfazer.pack(side=tk.LEFT, padx=5)
        
        # ---------------------------------------------------------
        # BASE 1 (Tags e Classificação)
        # ---------------------------------------------------------
        frame_base = tk.Frame(self.root, bg=self.cor_painel, pady=10, padx=20, highlightbackground=self.cor_borda, highlightthickness=1)
        frame_base.pack(fill=tk.X, padx=20, pady=5)
        
        lbl_pergunta = tk.Label(frame_base, text="Natureza(s) do Sinal (Múltipla Seleção):", font=("Segoe UI", 10, "bold"), bg=self.cor_painel, fg=self.cor_texto)
        lbl_pergunta.pack(pady=(0, 5))

        frame_checks = tk.Frame(frame_base, bg=self.cor_painel)
        frame_checks.pack()

        # Distribui os checkboxes em duas linhas para ficar simétrico (3 e 3)
        linha_atual = tk.Frame(frame_checks, bg=self.cor_painel)
        linha_atual.pack()
        
        for i, op in enumerate(self.opcoes_tags):
            if i == 3: # Quebra de linha após 3 itens
                linha_atual = tk.Frame(frame_checks, bg=self.cor_painel)
                linha_atual.pack()
                
            var = tk.BooleanVar(value=False)
            self.selecoes_tags[op] = var
            cb = tk.Checkbutton(
                linha_atual, text=op, variable=var,
                font=("Segoe UI", 10, "bold"), bg=self.cor_painel, fg=self.cor_texto,
                selectcolor="#333333", activebackground=self.cor_painel, activeforeground=self.cor_destaque,
                cursor="hand2"
            )
            cb.pack(side=tk.LEFT, padx=15, pady=2)
            
        # ---------------------------------------------------------
        # BASE 2 (Formulário de Entrada e Botões)
        # ---------------------------------------------------------
        frame_form = tk.Frame(self.root, bg=self.cor_fundo)
        frame_form.pack(fill=tk.X, padx=20, pady=10)
        
        # Entradas
        frame_campos = tk.Frame(frame_form, bg=self.cor_fundo)
        frame_campos.pack(side=tk.LEFT)
        
        self.entradas = {}
        campos = ["Numeração", "Marca", "Modelo", "Ano"]
        for i, campo in enumerate(campos):
            lbl = tk.Label(frame_campos, text=campo + ":", font=("Segoe UI", 10, "bold"), bg=self.cor_fundo, fg=self.cor_texto)
            lbl.grid(row=0, column=i, padx=5, sticky="w")
            
            ent = tk.Entry(frame_campos, font=("Segoe UI", 12), width=15, bg="#333333", fg=self.cor_texto, insertbackground=self.cor_destaque)
            ent.grid(row=1, column=i, padx=5)
            self.entradas[campo] = ent
            
        self.entradas["Numeração"].config(width=22)
        self.entradas["Modelo"].config(width=22)
        
        # Botões de Ação Dinâmicos
        frame_botoes = tk.Frame(frame_form, bg=self.cor_fundo)
        frame_botoes.pack(side=tk.RIGHT)
        
        self.btn_pular = tk.Button(
            frame_botoes, text="⏭ Pular Foto (M)", font=("Segoe UI", 10, "bold"),
            bg="#333333", fg=self.cor_texto, relief=tk.FLAT, cursor="hand2", command=self.pular_imagem
        )
        self.btn_pular.pack(side=tk.LEFT, padx=5)
        
        self.btn_acao_principal = tk.Button(
            frame_botoes, text="✂️ Recortar (Enter)", font=("Segoe UI", 11, "bold"),
            bg="#111111", fg=self.cor_destaque, relief=tk.FLAT, borderwidth=1, highlightbackground=self.cor_destaque, highlightthickness=1,
            cursor="hand2", command=self.acao_principal, width=20, pady=5
        )
        self.btn_acao_principal.pack(side=tk.LEFT, padx=5)
        
        # Desabilita tudo até a pasta ser selecionada
        self.desabilitar_form()
        self.btn_girar_esq.config(state=tk.DISABLED)
        self.btn_girar_dir.config(state=tk.DISABLED)
        self.btn_desfazer.config(state=tk.DISABLED)

    def configurar_eventos(self):
        # Eventos do Canvas (Mouse)
        self.canvas.bind("<ButtonPress-1>", self.ao_clicar_canvas)
        self.canvas.bind("<B1-Motion>", self.ao_arrastar_canvas)
        self.canvas.bind("<ButtonRelease-1>", self.ao_soltar_canvas)
        
        # Atalho Único de Teclado Preservado (Enter)
        self.root.bind("<Return>", lambda event: self.acao_principal())
        
        # Lógicas de Autopreenchimento
        self.entradas["Numeração"].bind("<KeyRelease>", self.checar_ano_chassi)
        self.entradas["Marca"].bind("<<Paste>>", self.ao_colar_marca)
        self.entradas["Marca"].bind("<Control-v>", self.ao_colar_marca)

    # =========================================================
    # FLUXO DE PASTAS E ARQUIVOS
    # =========================================================
    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com as imagens originais")
        if pasta:
            self.pasta_origem = pasta
            self.carregar_fila()

    def carregar_fila(self):
        extensoes = ('.jpg', '.jpeg', '.png', '.webp')
        arquivos = [f for f in os.listdir(self.pasta_origem) if f.lower().endswith(extensoes)]
        
        self.lista_fotos = []
        for f in arquivos:
            # Pula imagens que já parecem estar no formato processado longo
            if f.count('_') < 3:
                self.lista_fotos.append(f)
                
        if not self.lista_fotos:
            messagebox.showinfo("Fila Vazia", "Não há arquivos pendentes de processamento nesta pasta.")
            return
            
        self.indice_atual = 0
        self.exibir_imagem_atual()
        
    def exibir_imagem_atual(self):
        if self.indice_atual >= len(self.lista_fotos):
            self.finalizar_processo()
            return
            
        nome_arquivo = self.lista_fotos[self.indice_atual]
        caminho_completo = os.path.join(self.pasta_origem, nome_arquivo)
        
        self.lbl_progresso.config(text=f"Fila: {self.indice_atual + 1} de {len(self.lista_fotos)}")
        self.lbl_nome_arquivo.config(text=f"Processando: {nome_arquivo}")
        
        # Reseta Estado
        self.pontos_canvas = []
        self.ponto_arrastado = None
        self.estado_app = "RECORTANDO"
        self.desabilitar_form()
        self.limpar_form()
        
        self.btn_acao_principal.config(text="✂️ Confirmar Recorte (Enter)", fg=self.cor_destaque)
        self.lbl_status_app.config(text="CLIQUE E ARRASTE: Marque os 4 cantos da numeração")
        
        self.btn_girar_esq.config(state=tk.NORMAL)
        self.btn_girar_dir.config(state=tk.NORMAL)
        self.btn_desfazer.config(state=tk.DISABLED)
        
        # Leitura blindada contra caracteres especiais do Windows
        try:
            stream = np.fromfile(caminho_completo, dtype=np.uint8)
            img_lida = cv2.imdecode(stream, cv2.IMREAD_COLOR)
            if img_lida is None:
                raise Exception("Falha na decodificação da imagem.")
        except Exception as e:
            messagebox.showerror("Erro de Leitura", f"O OpenCV não conseguiu ler a imagem: {nome_arquivo}\n{e}")
            self.pular_imagem()
            return
            
        self.imagem_cv_original = img_lida.copy()
        self.imagem_cv_exibicao = self.imagem_cv_original.copy()
        
        self.atualizar_canvas()

    def pular_imagem(self):
        if self.lista_fotos:
            self.indice_atual += 1
            self.exibir_imagem_atual()

    def finalizar_processo(self):
        self.lbl_progresso.config(text="Fila zerada", fg=self.cor_destaque)
        self.lbl_status_app.config(text="Processamento Concluído!")
        self.lbl_nome_arquivo.config(text="")
        self.canvas.delete("all")
        self.desabilitar_form()
        self.btn_acao_principal.config(state=tk.DISABLED)
        self.btn_girar_esq.config(state=tk.DISABLED)
        self.btn_girar_dir.config(state=tk.DISABLED)
        self.btn_desfazer.config(state=tk.DISABLED)
        messagebox.showinfo("Fim", "Todas as imagens foram processadas com sucesso!")

    # =========================================================
    # LÓGICA DO CANVAS E DESENHO
    # =========================================================
    def rotacionar_imagem(self, direcao_cv):
        if self.imagem_cv_exibicao is not None and self.estado_app == "RECORTANDO":
            self.imagem_cv_exibicao = cv2.rotate(self.imagem_cv_exibicao, direcao_cv)
            self.pontos_canvas = [] # Reseta os pontos ao girar
            self.atualizar_canvas()

    def atualizar_canvas(self):
        self.canvas.delete("all")
        
        if self.imagem_cv_exibicao is None:
            return
            
        # Converte BGR (OpenCV) para RGB (Pillow)
        img_rgb = cv2.cvtColor(self.imagem_cv_exibicao, cv2.COLOR_BGR2RGB)
        h, w = img_rgb.shape[:2]
        
        # Cálculo de Escala e Centralização
        escala_w = self.canvas_w / w
        escala_h = self.canvas_h / h
        self.escala_canvas = min(escala_w, escala_h)
        
        new_w = int(w * self.escala_canvas)
        new_h = int(h * self.escala_canvas)
        
        self.offset_x = (self.canvas_w - new_w) // 2
        self.offset_y = (self.canvas_h - new_h) // 2
        
        # Renderiza a Imagem
        img_pil = Image.fromarray(img_rgb)
        img_pil = img_pil.resize((new_w, new_h), Image.Resampling.LANCZOS)
        self.img_tk = ImageTk.PhotoImage(img_pil)
        
        self.canvas.create_image(self.offset_x, self.offset_y, anchor=tk.NW, image=self.img_tk)
        
        # Desenha os Pontos e Polígono se estiver no modo de recorte
        if self.estado_app == "RECORTANDO":
            raio = 6
            for i, p in enumerate(self.pontos_canvas):
                x, y = p
                # Círculo verde
                self.canvas.create_oval(x - raio, y - raio, x + raio, y + raio, fill=self.cor_destaque, outline="white", tags="ponto")
                
            # Desenha as linhas conectando os pontos
            if len(self.pontos_canvas) > 1:
                for i in range(len(self.pontos_canvas) - 1):
                    p1 = self.pontos_canvas[i]
                    p2 = self.pontos_canvas[i+1]
                    self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=self.cor_destaque, width=2)
                    
            if len(self.pontos_canvas) == 4:
                # Fecha o polígono
                p1 = self.pontos_canvas[3]
                p2 = self.pontos_canvas[0]
                self.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=self.cor_destaque, width=2)
                self.lbl_status_app.config(text="OK! Arraste os pontos para ajustar ou Enter para Recortar.")

    def ao_clicar_canvas(self, event):
        if self.estado_app != "RECORTANDO": return
        
        x, y = event.x, event.y
        
        # Checa se clicou perto de um ponto existente para arrastar (raio de tolerância maior)
        for i, p in enumerate(self.pontos_canvas):
            px, py = p
            distancia = ((x - px)**2 + (y - py)**2) ** 0.5
            if distancia < 15: # 15 pixels de tolerância
                self.ponto_arrastado = i
                return
                
        # Se não clicou em nenhum existente e tem menos de 4, adiciona um novo
        if len(self.pontos_canvas) < 4:
            self.pontos_canvas.append((x, y))
            self.atualizar_canvas()

    def ao_arrastar_canvas(self, event):
        if self.estado_app != "RECORTANDO" or self.ponto_arrastado is None: return
        
        # Atualiza a posição do ponto arrastado
        self.pontos_canvas[self.ponto_arrastado] = (event.x, event.y)
        self.atualizar_canvas()

    def ao_soltar_canvas(self, event):
        self.ponto_arrastado = None

    # =========================================================
    # LÓGICA DO OPENCV (PERSPECTIVA)
    # =========================================================
    def ordenar_pontos(self, pts):
        rect = np.zeros((4, 2), dtype="float32")
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def corrigir_perspectiva(self, imagem, pts):
        rect = self.ordenar_pontos(pts)
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        dst = np.array([[0, 0], [maxWidth - 1, 0], [maxWidth - 1, maxHeight - 1], [0, maxHeight - 1]], dtype="float32")
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(imagem, M, (maxWidth, maxHeight))
        
        # Força orientação horizontal
        if warped.shape[0] > warped.shape[1]:
            warped = cv2.rotate(warped, cv2.ROTATE_90_COUNTERCLOCKWISE)
            
        return warped

    # =========================================================
    # MÁQUINA DE ESTADO E COMANDOS PRINCIPAIS
    # =========================================================
    def acao_principal(self):
        if not self.lista_fotos: return
        
        if self.estado_app == "RECORTANDO":
            if len(self.pontos_canvas) != 4:
                messagebox.showwarning("Atenção", "Selecione os 4 cantos da numeração antes de recortar.")
                return
                
            # Mapeia os pontos do Canvas de volta para a resolução original da imagem OpenCV
            pts_img = []
            for px, py in self.pontos_canvas:
                img_x = (px - self.offset_x) / self.escala_canvas
                img_y = (py - self.offset_y) / self.escala_canvas
                pts_img.append([img_x, img_y])
                
            pts_array = np.array(pts_img, dtype="float32")
            
            # Aplica o recorte na imagem exibida (já rotacionada)
            self.imagem_cv_recortada = self.corrigir_perspectiva(self.imagem_cv_exibicao, pts_array)
            
            # Atualiza o Canvas com a imagem já recortada
            self.imagem_cv_exibicao = self.imagem_cv_recortada.copy()
            self.estado_app = "PREENCHENDO"
            self.atualizar_canvas()
            
            # Libera o formulário para preenchimento e ajusta botões
            self.habilitar_form()
            self.btn_girar_esq.config(state=tk.DISABLED)
            self.btn_girar_dir.config(state=tk.DISABLED)
            self.btn_desfazer.config(state=tk.NORMAL)
            
            self.btn_acao_principal.config(text="✅ Salvar e Avançar (Enter)", fg="#00ff00")
            self.lbl_status_app.config(text="PREENCHA OS DADOS | Use o botão 'Desfazer Recorte' se precisar")
            
            # Autopreenchimento Inteligente: Tenta extrair o chassi do nome original caso já possua
            nome_arq = self.lista_fotos[self.indice_atual]
            nome_sem_ext = os.path.splitext(nome_arq)[0].upper()
            chassi_limpo = re.sub(r'_[A-Z0-9]+$', '', nome_sem_ext)
            if " " not in chassi_limpo and "_" not in chassi_limpo: # Prevenção básica
                self.entradas["Numeração"].insert(0, chassi_limpo)
            
            self.entradas["Numeração"].focus()
            
        elif self.estado_app == "PREENCHENDO":
            self.salvar_dados()

    def desfazer_recorte(self):
        if self.estado_app == "PREENCHENDO":
            self.estado_app = "RECORTANDO"
            self.desabilitar_form()
            self.btn_acao_principal.config(text="✂️ Confirmar Recorte (Enter)", fg=self.cor_destaque)
            self.lbl_status_app.config(text="CLIQUE E ARRASTE: Marque os 4 cantos da numeração")
            
            self.btn_girar_esq.config(state=tk.NORMAL)
            self.btn_girar_dir.config(state=tk.NORMAL)
            self.btn_desfazer.config(state=tk.DISABLED)
            
            # Restaura a imagem para como estava antes do recorte (mas mantém a rotação aplicada)
            # Para manter simples, restauramos da original lida
            self.imagem_cv_exibicao = self.imagem_cv_original.copy()
            self.pontos_canvas = []
            self.atualizar_canvas()

    def salvar_dados(self):
        numeracao = self.entradas["Numeração"].get().strip().upper()
        marca = self.entradas["Marca"].get().strip().upper()
        modelo = self.entradas["Modelo"].get().strip().upper()
        ano = self.entradas["Ano"].get().strip().upper()
        
        selecionadas = [op.upper() for op, var in self.selecoes_tags.items() if var.get()]
        
        if not numeracao or not marca or not modelo or not ano:
            messagebox.showwarning("Atenção", "Os campos Numeração, Marca, Modelo e Ano são obrigatórios.")
            return
            
        if not selecionadas:
            messagebox.showwarning("Atenção", "Selecione ao menos uma Natureza (Ex: MOTOR, NIV).")
            return

        # ==============================================================
        # PADRÃO DE NOMENCLATURA EXACTO A PEDIDO DO USUÁRIO
        # Ex: NUMERAÇÃO_MARCA_MODELO COM ESPAÇO_ANO NATUREZA 1 NATUREZA 2.jpg
        # ==============================================================
        natureza_str = " ".join(selecionadas)
        extensao = os.path.splitext(self.lista_fotos[self.indice_atual])[1]
        
        novo_nome = f"{numeracao}_{marca}_{modelo}_{ano} {natureza_str}{extensao}"
        
        caminho_salvamento = os.path.join(self.pasta_destino, novo_nome)
        
        try:
            # Escrita blindada contra bugs de caminho com acento no Windows
            is_success, im_buf_arr = cv2.imencode(extensao, self.imagem_cv_recortada)
            if is_success:
                im_buf_arr.tofile(caminho_salvamento)
            else:
                raise Exception("Falha ao codificar a imagem para salvamento.")
            
            self.indice_atual += 1
            self.exibir_imagem_atual()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar a imagem:\n{e}")

    # =========================================================
    # FUNÇÕES AUXILIARES DO FORMULÁRIO
    # =========================================================
    def limpar_form(self):
        for ent in self.entradas.values():
            ent.delete(0, tk.END)
        for var in self.selecoes_tags.values():
            var.set(False)

    def desabilitar_form(self):
        for ent in self.entradas.values():
            ent.config(state=tk.DISABLED)

    def habilitar_form(self):
        for ent in self.entradas.values():
            ent.config(state=tk.NORMAL)

    def checar_ano_chassi(self, event):
        chassi = self.entradas["Numeração"].get().strip().upper()
        char_ano = None
        if len(chassi) >= 10: char_ano = chassi[9]
        elif len(chassi) == 8: char_ano = chassi[0]
            
        if char_ano and char_ano in self.mapa_anos:
            self.entradas["Ano"].delete(0, tk.END)
            self.entradas["Ano"].insert(0, self.mapa_anos[char_ano])

    def ao_colar_marca(self, event):
        try:
            texto_colado = self.root.clipboard_get().upper()
            if "/" in texto_colado: marca, modelo = texto_colado.split("/", 1)
            elif "-" in texto_colado: marca, modelo = texto_colado.split("-", 1)
            else: return 
            
            self.entradas["Marca"].delete(0, tk.END)
            self.entradas["Marca"].insert(0, marca.strip())
            
            self.entradas["Modelo"].delete(0, tk.END)
            self.entradas["Modelo"].insert(0, modelo.strip())
            
            self.entradas["Ano"].focus()
            return "break" 
        except Exception:
            pass

# =========================================================
# LOOP PRINCIPAL DA APLICAÇÃO (COM BLINDAGEM DE ERROS)
# =========================================================
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = UnificadorIDV(root)
        root.mainloop()
    except Exception as e:
        print("\n" + "="*70)
        print("🚨 ERRO DURANTE A EXECUÇÃO DO PROGRAMA 🚨")
        print("="*70)
        traceback.print_exc()
        print("="*70)
        input("\nPressione ENTER para fechar esta tela...")