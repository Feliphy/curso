import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
import pyperclip

class AppMensagens:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Mensagens para Clientes")
        self.root.geometry("800x600")
        
        # Carregar arquivos de mensagem
        self.mensagens_dir = "mensagens"
        self.carregar_mensagens()
        
        # Criar interface
        self.criar_widgets()
        
    def carregar_mensagens(self):
        """Carrega os arquivos JSON de mensagens da pasta mensagens"""
        if not os.path.exists(self.mensagens_dir):
            os.makedirs(self.mensagens_dir)
            # Criar um exemplo se a pasta estiver vazia
            exemplo = {
                "nome": "Problema no Pedido",
                "conteudo": "Prezado $nome,\n\nIdentificamos um problema com seu pedido $pedido. Nossa equipe já está trabalhando para resolver.\n\nAtenciosamente,\nCRA. Padrão Color"
            }
            with open(os.path.join(self.mensagens_dir, "erro1.json"), 'w', encoding='utf-8') as f:
                json.dump(exemplo, f, ensure_ascii=False, indent=4)
        
        self.mensagens = []
        for arquivo in os.listdir(self.mensagens_dir):
            if arquivo.endswith('.json'):
                try:
                    with open(os.path.join(self.mensagens_dir, arquivo), 'r', encoding='utf-8') as f:
                        dados = json.load(f)
                        self.mensagens.append({
                            'arquivo': arquivo,
                            'nome': dados.get('nome', arquivo),
                            'conteudo': dados.get('conteudo', '')
                        })
                except Exception as e:
                    print(f"Erro ao carregar {arquivo}: {e}")
    
    def criar_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Seção de entrada de dados
        input_frame = ttk.LabelFrame(main_frame, text="Dados da Revenda", padding="10")
        input_frame.pack(fill=tk.X, pady=5)
        
        # Nome do cliente
        ttk.Label(input_frame, text="Nome da Revenda:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.nome_cliente = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.nome_cliente, width=50).grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Número do pedido
        ttk.Label(input_frame, text="Número do Pedido(s):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.numero_pedido = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.numero_pedido, width=50).grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        ttk.Label(input_frame, text="(Separe múltiplos pedidos por vírgula)").grid(row=2, column=1, sticky=tk.W, padx=5)
        
        # Seleção de mensagem
        ttk.Label(input_frame, text="Tipo de Mensagem:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.tipo_mensagem = tk.StringVar()
        self.combo_mensagens = ttk.Combobox(input_frame, textvariable=self.tipo_mensagem, state="readonly")
        self.combo_mensagens.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        
        # Atualizar combobox com as mensagens disponíveis
        self.atualizar_combo_mensagens()
        
        # Botão para gerar mensagem
        ttk.Button(input_frame, text="Gerar Mensagem", command=self.gerar_mensagem).grid(row=4, column=0, columnspan=2, pady=10)
        
        # Seção de visualização da mensagem
        output_frame = ttk.LabelFrame(main_frame, text="Mensagem Gerada", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.mensagem_gerada = ScrolledText(output_frame, wrap=tk.WORD, width=80, height=15)
        self.mensagem_gerada.pack(fill=tk.BOTH, expand=True)
        
        # Botão para copiar mensagem
        ttk.Button(output_frame, text="Copiar Mensagem", command=self.copiar_mensagem).pack(pady=5)
        
        # Botão para gerenciar mensagens
        ttk.Button(main_frame, text="Gerenciar Mensagens", command=self.gerenciar_mensagens).pack(pady=5)
        
        # Configurar expansão de colunas
        input_frame.columnconfigure(1, weight=1)
    
    def atualizar_combo_mensagens(self):
        """Atualiza o combobox com as mensagens disponíveis"""
        nomes = [msg['nome'] for msg in self.mensagens]
        self.combo_mensagens['values'] = nomes
        if nomes:
            self.combo_mensagens.set(nomes[0])
    
    def gerar_mensagem(self):
        """Gera a mensagem substituindo as variáveis"""
        nome_cliente = self.nome_cliente.get().strip()
        numero_pedido = self.numero_pedido.get().strip()
        
        if not nome_cliente or not numero_pedido:
            messagebox.showwarning("Atenção", "Por favor, preencha o nome do cliente e o número do pedido.")
            return
        
        if not self.mensagens:
            messagebox.showwarning("Atenção", "Nenhuma mensagem disponível. Adicione mensagens na pasta 'mensagens'.")
            return
        
        selected_msg_name = self.tipo_mensagem.get()
        mensagem = next((msg for msg in self.mensagens if msg['nome'] == selected_msg_name), None)
        
        if not mensagem:
            messagebox.showerror("Erro", "Mensagem selecionada não encontrada.")
            return
        
        # Substituir variáveis
        conteudo = mensagem['conteudo']
        pedido_texto = numero_pedido
        
        # Verificar se é plural
        pedidos = [p.strip() for p in numero_pedido.split(',')]
        if len(pedidos) > 1:
            pedido_texto = ", ".join(pedidos[:-1]) + " e " + pedidos[-1]
            conteudo = conteudo.replace("$pedido", "$pedidos")
        
        conteudo = conteudo.replace("$nome", nome_cliente)
        conteudo = conteudo.replace("$pedido", pedido_texto)
        conteudo = conteudo.replace("$pedidos", pedido_texto)
        
        # Exibir mensagem
        self.mensagem_gerada.delete(1.0, tk.END)
        self.mensagem_gerada.insert(tk.END, conteudo)
    
    def copiar_mensagem(self):
        """Copia a mensagem gerada para a área de transferência"""
        mensagem = self.mensagem_gerada.get(1.0, tk.END)
        if mensagem.strip():
            pyperclip.copy(mensagem)
            messagebox.showinfo("Sucesso", "Mensagem copiada para a área de transferência!")
        else:
            messagebox.showwarning("Atenção", "Nenhuma mensagem para copiar.")
    
    def gerenciar_mensagens(self):
        """Abre uma janela para gerenciar as mensagens"""
        janela_gerenciar = tk.Toplevel(self.root)
        janela_gerenciar.title("Gerenciar Mensagens")
        janela_gerenciar.geometry("600x400")
        
        # Lista de mensagens
        frame_lista = ttk.Frame(janela_gerenciar, padding="10")
        frame_lista.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_mensagens = tk.Listbox(frame_lista, yscrollcommand=scrollbar.set)
        self.lista_mensagens.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.lista_mensagens.yview)
        
        # Atualizar lista
        self.atualizar_lista_mensagens()
        
        # Botões
        frame_botoes = ttk.Frame(janela_gerenciar, padding="10")
        frame_botoes.pack(fill=tk.X)
        
        ttk.Button(frame_botoes, text="Adicionar", command=self.adicionar_mensagem).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Editar", command=self.editar_mensagem).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Remover", command=self.remover_mensagem).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Fechar", command=janela_gerenciar.destroy).pack(side=tk.RIGHT, padx=5)
    
    def atualizar_lista_mensagens(self):
        """Atualiza a lista de mensagens na janela de gerenciamento"""
        self.lista_mensagens.delete(0, tk.END)
        for msg in self.mensagens:
            self.lista_mensagens.insert(tk.END, f"{msg['nome']} ({msg['arquivo']})")
    
    def adicionar_mensagem(self):
        """Adiciona uma nova mensagem"""
        janela_adicionar = tk.Toplevel(self.root)
        janela_adicionar.title("Adicionar Mensagem")
        janela_adicionar.geometry("500x400")
        
        # Campos do formulário
        frame_form = ttk.Frame(janela_adicionar, padding="10")
        frame_form.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame_form, text="Nome da Mensagem:").grid(row=0, column=0, sticky=tk.W, pady=5)
        nome_msg = tk.StringVar()
        ttk.Entry(frame_form, textvariable=nome_msg).grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(frame_form, text="Nome do Arquivo (sem .json):").grid(row=1, column=0, sticky=tk.W, pady=5)
        nome_arquivo = tk.StringVar()
        ttk.Entry(frame_form, textvariable=nome_arquivo).grid(row=1, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(frame_form, text="Conteúdo da Mensagem:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        conteudo_msg = ScrolledText(frame_form, wrap=tk.WORD, width=40, height=10)
        conteudo_msg.grid(row=2, column=1, sticky=tk.NSEW, pady=5)
        
        # Dica sobre variáveis
        ttk.Label(frame_form, text="Use $nome para o nome do cliente e $pedido/$pedidos para o número do pedido").grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configurar expansão
        frame_form.columnconfigure(1, weight=1)
        frame_form.rowconfigure(2, weight=1)
        
        # Botões
        frame_botoes = ttk.Frame(janela_adicionar, padding="10")
        frame_botoes.pack(fill=tk.X)
        
        def salvar_mensagem():
            nome = nome_msg.get().strip()
            arquivo = nome_arquivo.get().strip()
            conteudo = conteudo_msg.get("1.0", tk.END).strip()
            
            if not nome or not arquivo or not conteudo:
                messagebox.showwarning("Atenção", "Todos os campos são obrigatórios.")
                return
            
            # Garantir que o arquivo termina com .json
            if not arquivo.endswith('.json'):
                arquivo += '.json'
            
            # Verificar se arquivo já existe
            caminho_arquivo = os.path.join(self.mensagens_dir, arquivo)
            if os.path.exists(caminho_arquivo):
                messagebox.showerror("Erro", f"O arquivo {arquivo} já existe.")
                return
            
            # Salvar mensagem
            try:
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump({
                        'nome': nome,
                        'conteudo': conteudo
                    }, f, ensure_ascii=False, indent=4)
                
                # Recarregar mensagens
                self.carregar_mensagens()
                self.atualizar_combo_mensagens()
                self.atualizar_lista_mensagens()
                messagebox.showinfo("Sucesso", "Mensagem adicionada com sucesso!")
                janela_adicionar.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar mensagem: {e}")
        
        ttk.Button(frame_botoes, text="Salvar", command=salvar_mensagem).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=janela_adicionar.destroy).pack(side=tk.RIGHT, padx=5)
    
    def editar_mensagem(self):
        """Edita uma mensagem existente"""
        selecionado = self.lista_mensagens.curselection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma mensagem para editar.")
            return
        
        index = selecionado[0]
        mensagem = self.mensagens[index]
        
        janela_editar = tk.Toplevel(self.root)
        janela_editar.title("Editar Mensagem")
        janela_editar.geometry("500x400")
        
        # Campos do formulário
        frame_form = ttk.Frame(janela_editar, padding="10")
        frame_form.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame_form, text="Nome da Mensagem:").grid(row=0, column=0, sticky=tk.W, pady=5)
        nome_msg = tk.StringVar(value=mensagem['nome'])
        ttk.Entry(frame_form, textvariable=nome_msg).grid(row=0, column=1, sticky=tk.EW, pady=5)
        
        ttk.Label(frame_form, text="Arquivo:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Label(frame_form, text=mensagem['arquivo']).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(frame_form, text="Conteúdo da Mensagem:").grid(row=2, column=0, sticky=tk.NW, pady=5)
        conteudo_msg = ScrolledText(frame_form, wrap=tk.WORD, width=40, height=10)
        conteudo_msg.insert(tk.END, mensagem['conteudo'])
        conteudo_msg.grid(row=2, column=1, sticky=tk.NSEW, pady=5)
        
        # Dica sobre variáveis
        ttk.Label(frame_form, text="Use $nome para o nome do cliente e $pedido/$pedidos para o número do pedido").grid(
            row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configurar expansão
        frame_form.columnconfigure(1, weight=1)
        frame_form.rowconfigure(2, weight=1)
        
        # Botões
        frame_botoes = ttk.Frame(janela_editar, padding="10")
        frame_botoes.pack(fill=tk.X)
        
        def salvar_edicao():
            nome = nome_msg.get().strip()
            conteudo = conteudo_msg.get("1.0", tk.END).strip()
            
            if not nome or not conteudo:
                messagebox.showwarning("Atenção", "Todos os campos são obrigatórios.")
                return
            
            # Salvar mensagem
            try:
                caminho_arquivo = os.path.join(self.mensagens_dir, mensagem['arquivo'])
                with open(caminho_arquivo, 'w', encoding='utf-8') as f:
                    json.dump({
                        'nome': nome,
                        'conteudo': conteudo
                    }, f, ensure_ascii=False, indent=4)
                
                # Recarregar mensagens
                self.carregar_mensagens()
                self.atualizar_combo_mensagens()
                self.atualizar_lista_mensagens()
                messagebox.showinfo("Sucesso", "Mensagem atualizada com sucesso!")
                janela_editar.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar mensagem: {e}")
        
        ttk.Button(frame_botoes, text="Salvar", command=salvar_edicao).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="Cancelar", command=janela_editar.destroy).pack(side=tk.RIGHT, padx=5)
    
    def remover_mensagem(self):
        """Remove uma mensagem existente"""
        selecionado = self.lista_mensagens.curselection()
        if not selecionado:
            messagebox.showwarning("Atenção", "Selecione uma mensagem para remover.")
            return
        
        index = selecionado[0]
        mensagem = self.mensagens[index]
        
        resposta = messagebox.askyesno(
            "Confirmar",
            f"Tem certeza que deseja remover a mensagem '{mensagem['nome']}' ({mensagem['arquivo']})?"
        )
        
        if resposta:
            try:
                caminho_arquivo = os.path.join(self.mensagens_dir, mensagem['arquivo'])
                os.remove(caminho_arquivo)
                
                # Recarregar mensagens
                self.carregar_mensagens()
                self.atualizar_combo_mensagens()
                self.atualizar_lista_mensagens()
                messagebox.showinfo("Sucesso", "Mensagem removida com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao remover mensagem: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppMensagens(root)
    root.mainloop()
