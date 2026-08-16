import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class ReparadorChassi:
    def __init__(self, root):
        self.root = root
        self.root.title("Reparador de Arquivos - IDV")
        self.root.geometry("900x750")
        
        # Cores
        self.cor_fundo = "#1a1a1a"
        self.cor_painel = "#252525"
        self.cor_texto = "#ffffff"
        self.cor_destaque = "#ffaa00" # Amarelo alerta para o reparador
        self.cor_borda = "#444444"
        
        self.root.configure(bg=self.cor_fundo)
        
        self.pasta_atual = os.getcwd()
        self.lista_fotos = []
        self.indice_atual = 0
        
        self.construir_interface()
        
    def construir_interface(self):
        # Topo
        frame_topo = tk.Frame(self.root, bg=self.cor_painel, pady=15, padx=20, highlightbackground=self.cor_borda, highlightthickness=1)
        frame_topo.pack(fill=tk.X, padx=20, pady=20)
        
        self.btn_selecionar = tk.Button(
            frame_topo, text="📁 Selecionar Pasta com Erros", font=("Segoe UI", 12, "bold"),
            bg="#111111", fg=self.cor_destaque, activebackground=self.cor_destaque, activeforeground="#111111",
            relief=tk.FLAT, borderwidth=1, highlightbackground=self.cor_destaque, highlightthickness=1,
            cursor="hand2", command=self.selecionar_pasta, padx=15, pady=5
        )
        self.btn_selecionar.pack(side=tk.LEFT)
        
        self.lbl_progresso = tk.Label(frame_topo, text="Aguardando...", font=("Segoe UI", 12, "bold"), bg=self.cor_painel, fg=self.cor_texto)
        self.lbl_progresso.pack(side=tk.RIGHT)
        
        # Centro (Imagem e Avisos)
        self.frame_imagem = tk.Frame(self.root, bg=self.cor_fundo)
        self.frame_imagem.pack(expand=True, fill=tk.BOTH, padx=20, pady=5)
        
        self.lbl_nome_arquivo = tk.Label(self.frame_imagem, text="", font=("Segoe UI", 11, "italic"), bg=self.cor_fundo, fg="#aaaaaa")
        self.lbl_nome_arquivo.pack(pady=5)
        
        self.lbl_imagem = tk.Label(self.frame_imagem, bg=self.cor_fundo)
        self.lbl_imagem.pack(expand=True)
        
        # Base (Formulário de Reparo)
        frame_base = tk.Frame(self.root, bg=self.cor_painel, pady=15, padx=20, highlightbackground=self.cor_borda, highlightthickness=1)
        frame_base.pack(fill=tk.X, padx=20, pady=20)
        
        lbl_instrucao = tk.Label(frame_base, text="Insira o Chassi/Sinal faltante para esta foto:", font=("Segoe UI", 12, "bold"), bg=self.cor_painel, fg=self.cor_texto)
        lbl_instrucao.pack(pady=(0, 10))
        
        self.ent_chassi = tk.Entry(frame_base, font=("Segoe UI", 18, "bold"), width=25, bg="#333333", fg=self.cor_destaque, justify="center", insertbackground=self.cor_destaque)
        self.ent_chassi.pack(pady=5)
        
        self.btn_salvar = tk.Button(
            frame_base, text="🔧 Reparar Arquivo (Enter)", font=("Segoe UI", 12, "bold"),
            bg="#111111", fg=self.cor_destaque, activebackground=self.cor_destaque, activeforeground="#111111",
            relief=tk.FLAT, borderwidth=1, highlightbackground=self.cor_destaque, highlightthickness=1,
            cursor="hand2", command=self.salvar_reparo, width=30, pady=10
        )
        self.btn_salvar.pack(pady=10)
        
        # Atalho
        self.root.bind("<Return>", lambda event: self.salvar_reparo())
        
        self.desabilitar_botoes()
        
    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta com as imagens")
        if pasta:
            self.pasta_atual = pasta
            self.carregar_fila()

    def desabilitar_botoes(self):
        self.ent_chassi.config(state=tk.DISABLED)
        self.btn_salvar.config(state=tk.DISABLED)

    def habilitar_botoes(self):
        self.ent_chassi.config(state=tk.NORMAL)
        self.btn_salvar.config(state=tk.NORMAL)
        
    def carregar_fila(self):
        extensoes = ('.jpg', '.jpeg', '.png', '.webp')
        arquivos = [f for f in os.listdir(self.pasta_atual) if f.lower().endswith(extensoes)]
        
        self.lista_fotos = []
        for f in arquivos:
            # Puxa APENAS arquivos que começam com underline (erro de chassi vazio)
            if f.startswith('_'):
                self.lista_fotos.append(f)
                
        if not self.lista_fotos:
            messagebox.showinfo("Tudo Certo", "Não há nenhum arquivo corrompido começando com '_' nesta pasta.")
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
        
        self.lbl_progresso.config(text=f"Arquivos Corrompidos: {self.indice_atual + 1} de {len(self.lista_fotos)}", fg=self.cor_destaque)
        self.lbl_nome_arquivo.config(text=f"Recuperando: {nome_arquivo}")
        
        self.ent_chassi.delete(0, tk.END)
        self.ent_chassi.focus()
        
        try:
            img = Image.open(caminho_completo)
            img.thumbnail((700, 400), Image.Resampling.LANCZOS)
            self.img_tk = ImageTk.PhotoImage(img)
            self.lbl_imagem.config(image=self.img_tk)
        except Exception as e:
            self.lbl_nome_arquivo.config(text=f"Erro ao carregar imagem: {e}")
            self.lbl_imagem.config(image='')
            
    def salvar_reparo(self, event=None):
        if str(self.btn_salvar['state']) == tk.DISABLED:
            return

        chassi = self.ent_chassi.get().strip().upper()
        
        if not chassi:
            messagebox.showwarning("Atenção", "O chassi não pode ficar vazio.")
            return
            
        nome_arquivo_antigo = self.lista_fotos[self.indice_atual]
        caminho_antigo = os.path.join(self.pasta_atual, nome_arquivo_antigo)
        
        # Junta o chassi digitado com o resto do nome do arquivo (que começa com '_')
        novo_nome = f"{chassi}{nome_arquivo_antigo}"
        caminho_novo = os.path.join(self.pasta_atual, novo_nome)
        
        try:
            if caminho_antigo != caminho_novo:
                os.rename(caminho_antigo, caminho_novo)
            
            self.indice_atual += 1
            self.exibir_imagem_atual()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao renomear arquivo:\n{e}")
            
    def tela_concluida(self):
        self.lbl_progresso.config(text="Fila zerada", fg="#00ff00")
        self.lbl_nome_arquivo.config(text="Todos os arquivos foram corrigidos com sucesso!")
        self.lbl_imagem.config(image='')
        self.desabilitar_botoes()

if __name__ == "__main__":
    root = tk.Tk()
    app = ReparadorChassi(root)
    root.mainloop()