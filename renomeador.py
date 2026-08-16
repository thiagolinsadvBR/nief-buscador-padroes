import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class CatalogadorRapido:
    def __init__(self, root):
        self.root = root
        self.root.title("Catalogador Rápido - Renomeador IDV")
        self.root.geometry("1000x850")
        
        # Cores padronizadas do sistema
        self.cor_fundo = "#1a1a1a"
        self.cor_painel = "#252525"
        self.cor_texto = "#ffffff"
        self.cor_destaque = "#7CFC00"
        self.cor_borda = "#444444"
        self.cor_alerta = "#ff4444"
        
        self.root.configure(bg=self.cor_fundo)
        
        self.pasta_atual = ""
        self.lista_fotos = []
        self.indice_atual = 0
        
        # Tabela global de decodificação do Ano do Chassi (VIS / NIV)
        self.mapa_anos = {
            '1': '2001', '2': '2002', '3': '2003', '4': '2004', '5': '2005',
            '6': '2006', '7': '2007', '8': '2008', '9': '2009', 'A': '2010',
            'B': '2011', 'C': '2012', 'D': '2013', 'E': '2014', 'F': '2015',
            'G': '2016', 'H': '2017', 'J': '2018', 'K': '2019', 'L': '2020',
            'M': '2021', 'N': '2022', 'P': '2023', 'R': '2024', 'S': '2025',
            'T': '2026', 'V': '1997', 'W': '1998', 'X': '1999', 'Y': '2000'
        }
        
        # Lista de naturezas que o programa deve procurar e preservar
        self.tags_conhecidas = ["NIV", "MOTOR", "ETIQUETA", "PLAQUETA", "CÂMBIO", "VIS"]
        self.tags_preservadas = ""
        
        self.construir_interface()
        
    def construir_interface(self):
        # Topo
        frame_topo = tk.Frame(self.root, bg=self.cor_painel, pady=15, padx=20, highlightbackground=self.cor_borda, highlightthickness=1)
        frame_topo.pack(fill=tk.X, padx=20, pady=20)
        
        self.btn_selecionar = tk.Button(
            frame_topo, text="📁 Selecionar Pasta de Imagens", font=("Segoe UI", 12, "bold"),
            bg="#111111", fg=self.cor_destaque, activebackground=self.cor_destaque, activeforeground="#111111",
            relief=tk.FLAT, borderwidth=1, highlightbackground=self.cor_destaque, highlightthickness=1,
            cursor="hand2", command=self.selecionar_pasta, padx=15, pady=5
        )
        self.btn_selecionar.pack(side=tk.LEFT)
        
        self.lbl_progresso = tk.Label(frame_topo, text="Nenhuma pasta selecionada", font=("Segoe UI", 12, "bold"), bg=self.cor_painel, fg=self.cor_texto)
        self.lbl_progresso.pack(side=tk.RIGHT)
        
        # Centro (Imagem e Avisos)
        self.frame_imagem = tk.Frame(self.root, bg=self.cor_fundo)
        self.frame_imagem.pack(expand=True, fill=tk.BOTH, padx=20, pady=5)
        
        # Área para copiar o nome/chassi original com botão dedicado
        frame_original = tk.Frame(self.frame_imagem, bg=self.cor_fundo)
        frame_original.pack(pady=5)
        
        lbl_orig = tk.Label(frame_original, text="Chassi/Identificador Original:", font=("Segoe UI", 10, "italic"), bg=self.cor_fundo, fg="#aaaaaa")
        lbl_orig.pack(side=tk.LEFT, padx=5)
        
        self.ent_nome_original = tk.Entry(frame_original, font=("Segoe UI", 12, "bold"), width=30, bg="#222222", fg=self.cor_destaque, relief=tk.FLAT, justify="center", insertbackground=self.cor_destaque)
        self.ent_nome_original.pack(side=tk.LEFT, padx=5)
        
        self.btn_copiar = tk.Button(
            frame_original, text="📋 Copiar", font=("Segoe UI", 9, "bold"),
            bg="#333333", fg=self.cor_texto, activebackground=self.cor_destaque, activeforeground="#111111",
            relief=tk.FLAT, cursor="hand2", command=self.copiar_texto_original, padx=8, pady=2
        )
        self.btn_copiar.pack(side=tk.LEFT, padx=5)
        
        # Alerta visual da natureza encontrada
        self.lbl_tags = tk.Label(self.frame_imagem, text="", font=("Segoe UI", 12, "bold"), bg=self.cor_fundo, fg=self.cor_destaque)
        self.lbl_tags.pack(pady=2)
        
        self.lbl_imagem = tk.Label(self.frame_imagem, bg=self.cor_fundo)
        self.lbl_imagem.pack(expand=True)
        
        # Base (Formulário de Entrada)
        frame_base = tk.Frame(self.root, bg=self.cor_painel, pady=15, padx=20, highlightbackground=self.cor_borda, highlightthickness=1)
        frame_base.pack(fill=tk.X, padx=20, pady=20)
        
        frame_campos = tk.Frame(frame_base, bg=self.cor_painel)
        frame_campos.pack(pady=10)
        
        self.entradas = {}
        campos = ["Chassi", "Marca", "Modelo", "Ano"]
        
        for i, campo in enumerate(campos):
            lbl = tk.Label(frame_campos, text=campo + ":", font=("Segoe UI", 11, "bold"), bg=self.cor_painel, fg=self.cor_texto)
            lbl.grid(row=0, column=i, padx=8, sticky="w")
            
            ent = tk.Entry(frame_campos, font=("Segoe UI", 14), width=15, bg="#333333", fg=self.cor_texto, insertbackground=self.cor_destaque)
            ent.grid(row=1, column=i, padx=8, pady=5)
            self.entradas[campo] = ent
            
        self.entradas["Chassi"].config(width=22)
        self.entradas["Modelo"].config(width=22)
        
        # Vínculos e Lógicas Automáticas
        self.entradas["Chassi"].bind("<KeyRelease>", self.checar_ano_chassi)
        self.entradas["Marca"].bind("<<Paste>>", self.ao_colar_marca)
        self.entradas["Marca"].bind("<Control-v>", self.ao_colar_marca)
        
        # Botões Pular e Salvar
        frame_botoes = tk.Frame(frame_base, bg=self.cor_painel)
        frame_botoes.pack(pady=10)
        
        self.btn_pular = tk.Button(
            frame_botoes, text="⏭ Pular Imagem (Tecla D)", font=("Segoe UI", 12, "bold"),
            bg=self.cor_painel, fg=self.cor_alerta, activebackground=self.cor_alerta, activeforeground=self.cor_texto,
            relief=tk.FLAT, borderwidth=1, highlightbackground=self.cor_alerta, highlightthickness=1,
            cursor="hand2", command=self.pular_imagem, width=25, pady=10
        )
        self.btn_pular.pack(side=tk.LEFT, padx=10)

        self.btn_salvar = tk.Button(
            frame_botoes, text="✅ Salvar e Avançar (Enter)", font=("Segoe UI", 12, "bold"),
            bg="#111111", fg=self.cor_destaque, activebackground=self.cor_destaque, activeforeground="#111111",
            relief=tk.FLAT, borderwidth=1, highlightbackground=self.cor_destaque, highlightthickness=1,
            cursor="hand2", command=self.salvar_dados, width=25, pady=10
        )
        self.btn_salvar.pack(side=tk.LEFT, padx=10)
        
        # Atalhos
        self.root.bind("<Return>", lambda event: self.salvar_dados())
        self.root.bind("<d>", self.pular_imagem)
        self.root.bind("<D>", self.pular_imagem)
        
        # Inicia desabilitado
        self.desabilitar_botoes()
        
    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com as imagens")
        if pasta:
            self.pasta_atual = pasta
            self.carregar_fila()

    def desabilitar_botoes(self):
        for ent in self.entradas.values():
            ent.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.DISABLED)
        self.btn_pular.config(state=tk.DISABLED)
        self.ent_nome_original.config(state=tk.DISABLED)
        self.btn_copiar.config(state=tk.DISABLED)

    def habilitar_botoes(self):
        for ent in self.entradas.values():
            ent.config(state=tk.NORMAL)
        self.btn_salvar.config(state=tk.NORMAL)
        self.btn_pular.config(state=tk.NORMAL)
        self.ent_nome_original.config(state=tk.NORMAL)
        self.btn_copiar.config(state=tk.NORMAL)
        
    def carregar_fila(self):
        extensoes = ('.jpg', '.jpeg', '.png', '.webp')
        arquivos = [f for f in os.listdir(self.pasta_atual) if f.lower().endswith(extensoes)]
        
        self.lista_fotos = []
        for f in arquivos:
            if f.count('_') < 3:
                self.lista_fotos.append(f)
                
        if not self.lista_fotos:
            messagebox.showinfo("Fila Vazia", "Não há arquivos pendentes de renomeação nesta pasta.")
            self.tela_concluida()
            return
            
        self.indice_atual = 0
        self.habilitar_botoes()
        self.exibir_imagem_atual()
        
    def exibir_imagem_atual(self):
        if self.indice_atual >= len(self.lista_fotos):
            self.tela_concluida()
            return
            
        nome_arquivo = self.lista_fotos[self.indice_atual]
        caminho_completo = os.path.join(self.pasta_atual, nome_arquivo)
        
        self.lbl_progresso.config(text=f"Fila: {self.indice_atual + 1} de {len(self.lista_fotos)}", fg=self.cor_texto)
        
        # Processa o nome original para isolar o chassi e remover o sufixo _X (ex: _1)
        nome_sem_ext = os.path.splitext(nome_arquivo)[0].upper()
        pedacos = nome_sem_ext.split(' ')
        
        partes_chassi = [p for p in pedacos if p not in self.tags_conhecidas and p != ""]
        chassi_bruto = "_".join(partes_chassi)
        
        # Remove qualquer sufixo do tipo _1, _2, _A do final do chassi base
        chassi_limpo = re.sub(r'_[A-Z0-9]+$', '', chassi_bruto)
        
        # Exibe o chassi sem o _X na caixa de texto selecionável
        self.ent_nome_original.config(state=tk.NORMAL)
        self.ent_nome_original.delete(0, tk.END)
        self.ent_nome_original.insert(0, chassi_limpo)
        
        # Limpar os campos do formulário para a nova foto
        for ent in self.entradas.values():
            ent.delete(0, tk.END)
            
        # Memória de Etiqueta: Extrair as naturezas para preservação futura
        tags_encontradas = [p for p in pedacos if p in self.tags_conhecidas]
        if tags_encontradas:
            self.tags_preservadas = " ".join(tags_encontradas)
            self.lbl_tags.config(text=f"🏷 Natureza(s) preservada(s): {self.tags_preservadas}")
        else:
            self.tags_preservadas = ""
            self.lbl_tags.config(text="")
        
        # Direciona o cursor automaticamente para o campo Chassi
        self.entradas["Chassi"].focus()
        
        # Carrega a imagem na tela
        try:
            img = Image.open(caminho_completo)
            img.thumbnail((800, 450), Image.Resampling.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(img)
            self.lbl_imagem.config(image=self.img_tk)
        except Exception as e:
            self.lbl_tags.config(text=f"Erro ao carregar imagem: {e}")
            self.lbl_imagem.config(image='')
            
    def copiar_texto_original(self):
        texto = self.ent_nome_original.get()
        if texto:
            self.root.clipboard_clear()
            self.root.clipboard_append(texto)
            self.root.update()

    def checar_ano_chassi(self, event):
        if str(self.entradas["Ano"]['state']) == tk.DISABLED:
            return
            
        chassi = self.entradas["Chassi"].get().strip().upper()
        char_ano = None
        
        if len(chassi) >= 10:
            char_ano = chassi[9]
        elif len(chassi) == 8:
            char_ano = chassi[0]
            
        if char_ano and char_ano in self.mapa_anos:
            self.entradas["Ano"].delete(0, tk.END)
            self.entradas["Ano"].insert(0, self.mapa_anos[char_ano])

    def ao_colar_marca(self, event):
        if str(self.entradas["Marca"]['state']) == tk.DISABLED:
            return
            
        try:
            texto_colado = self.root.clipboard_get().upper()
            
            if "/" in texto_colado:
                marca, modelo = texto_colado.split("/", 1)
            elif "-" in texto_colado:
                marca, modelo = texto_colado.split("-", 1)
            else:
                return 
            
            self.entradas["Marca"].delete(0, tk.END)
            self.entradas["Marca"].insert(0, marca.strip())
            
            self.entradas["Modelo"].delete(0, tk.END)
            self.entradas["Modelo"].insert(0, modelo.strip())
            
            self.entradas["Ano"].focus()
            
            return "break" 
        except Exception:
            pass

    def pular_imagem(self, event=None):
        if str(self.btn_pular['state']) == tk.DISABLED:
            return
        
        self.indice_atual += 1
        self.exibir_imagem_atual()

    def salvar_dados(self, event=None):
        if str(self.btn_salvar['state']) == tk.DISABLED:
            return

        chassi = self.entradas["Chassi"].get().strip().upper()
        marca = self.entradas["Marca"].get().strip().upper()
        modelo = self.entradas["Modelo"].get().strip().upper()
        ano = self.entradas["Ano"].get().strip().upper()
        
        if not marca or not modelo or not ano:
            messagebox.showwarning("Atenção", "Os campos Marca, Modelo e Ano são obrigatórios.")
            return
            
        nome_arquivo_antigo = self.lista_fotos[self.indice_atual]
        caminho_antigo = os.path.join(self.pasta_atual, nome_arquivo_antigo)
        extensao = os.path.splitext(nome_arquivo_antigo)[1]
        
        if self.tags_preservadas:
            novo_nome = f"{chassi}_{marca}_{modelo}_{ano} {self.tags_preservadas}{extensao}"
        else:
            novo_nome = f"{chassi}_{marca}_{modelo}_{ano}{extensao}"
            
        caminho_novo = os.path.join(self.pasta_atual, novo_nome)
        
        try:
            if caminho_antigo != caminho_novo:
                os.rename(caminho_antigo, caminho_novo)
            
            self.indice_atual += 1
            self.exibir_imagem_atual()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao renomear arquivo no Windows:\n{e}")
            
    def tela_concluida(self):
        self.lbl_progresso.config(text="Fila zerada", fg=self.cor_destaque)
        
        self.ent_nome_original.config(state=tk.NORMAL)
        self.ent_nome_original.delete(0, tk.END)
        self.ent_nome_original.config(state="readonly")
        
        self.lbl_tags.config(text="", font=("Segoe UI", 12), fg=self.cor_texto)
        self.lbl_imagem.config(image='')
        
        self.desabilitar_botoes()

if __name__ == "__main__":
    root = tk.Tk()
    app = CatalogadorRapido(root)
    root.mainloop()