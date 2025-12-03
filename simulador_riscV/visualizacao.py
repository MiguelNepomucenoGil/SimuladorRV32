import tkinter as tk
from variaveis import END_HANDLER
from memoria import Memoria
from barramento import Barramento
from cpu import CPU

class SimuladorVisual:
    def __init__(self, mestre):
        self.mestre = mestre
        self.mestre.title("Simulador RISC-V: Visualização de Arquitetura Completa")
        self.mestre.geometry("1200x750")
        
        self.COR_FUNDO = "#1e1e1e"
        self.COR_COMPONENTE = "#3e3e42"
        self.COR_ATIVO = "#ffcc00"
        self.COR_TEXTO = "white"
        self.COR_BARRAMENTO = "#007acc"
        self.COR_DADOS = "#00ff00"
        self.COR_ALERTA = "#ff4444"

        self.mem = Memoria()
        self.barramento = Barramento(self.mem)
        self.cpu = CPU(self.barramento)

        frame_topo = tk.Frame(mestre, bg=self.COR_FUNDO)
        frame_topo.pack(fill=tk.BOTH, expand=True)
        
        self.canvas = tk.Canvas(frame_topo, bg=self.COR_FUNDO, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        frame_ctrl = tk.Frame(mestre, bg="#252526", height=80)
        frame_ctrl.pack(fill=tk.X)
        
        tk.Button(frame_ctrl, text="▶ Clock (Passo)", font=("Segoe UI", 12, "bold"), 
                  bg=self.COR_ATIVO, fg="black", command=self.proximo_passo).pack(side=tk.LEFT, padx=30, pady=20)
        
        self.lbl_info = tk.Label(frame_ctrl, text="Status: Pronto. Pressione 'K' para Interrupção.", fg="white", bg="#252526", font=("Consolas", 14))
        self.lbl_info.pack(side=tk.LEFT, pady=20)
        
        self.lbl_stats = tk.Label(frame_ctrl, text="Cache: H=0 M=0", fg="cyan", bg="#252526", font=("Consolas", 12))
        self.lbl_stats.pack(side=tk.RIGHT, padx=30)

        self.mestre.bind('k', self.acionar_interrupcao)
        self.mestre.bind('K', self.acionar_interrupcao)

        self.carregar_demo()
        self.desenhar_arquitetura()

    def carregar_demo(self):
        raw = bytes([
            0x37, 0x05, 0x08, 0x00,
            0x93, 0x05, 0xf0, 0x04,
            0x23, 0x00, 0xb5, 0x00,
            0x13, 0x05, 0x15, 0x00,
            0x93, 0x05, 0xc0, 0x04,
            0x23, 0x00, 0xb5, 0x00,
            0x13, 0x05, 0x15, 0x00,
            0x93, 0x05, 0x10, 0x04,
            0x23, 0x00, 0xb5, 0x00,
            0x6f, 0xf0, 0x1f, 0xff
        ])
        self.mem.carregar_prog(raw, 0)
        
        handler = bytes([
            0x37, 0x05, 0x08, 0x00,
            0x93, 0x05, 0x10, 0x02,
            0x23, 0x00, 0xb5, 0x00,
            0x73, 0x00, 0x20, 0x30
        ])
        self.mem.carregar_prog(handler, END_HANDLER)

    def desenhar_caixa(self, x, y, w, h, texto, tag, subtexto=""):
        self.canvas.create_rectangle(x, y, x+w, y+h, fill=self.COR_COMPONENTE, outline="white", tags=tag)
        self.canvas.create_text(x+w/2, y+20, text=texto, fill="cyan", font=("Segoe UI", 10, "bold"))
        self.canvas.create_text(x+w/2, y+h/2+10, text=subtexto, fill="white", font=("Consolas", 9), tags=tag+"_val")

    def desenhar_seta(self, x1, y1, x2, y2, tag, label=""):
        self.canvas.create_line(x1, y1, x2, y2, arrow=tk.LAST, fill=self.COR_BARRAMENTO, width=3, tags=tag)
        if label:
            mx, my = (x1+x2)/2, (y1+y2)/2
            self.canvas.create_text(mx, my-15, text=label, fill="#aaaaaa", font=("Arial", 8, "italic"))
        self.canvas.create_text((x1+x2)/2, (y1+y2)/2 - 5, text="", fill=self.COR_DADOS, font=("Arial", 8, "bold"), tags=tag+"_txt")

    def desenhar_arquitetura(self):
        self.canvas.create_rectangle(40, 180, 720, 450, outline="white", dash=(4, 4))
        self.canvas.create_text(80, 195, text="CPU (RV32I)", fill="white", font=("Arial", 12, "bold"))

        self.desenhar_caixa(60, 250, 80, 60, "PC", "box_pc", "0x0")
        self.desenhar_caixa(180, 230, 120, 120, "Registradores", "box_regs")
        self.desenhar_caixa(550, 240, 100, 100, "ALU", "box_alu")

        self.desenhar_caixa(800, 240, 120, 100, "CACHE L1", "box_cache", "Hits/Miss")
        self.desenhar_caixa(1000, 200, 120, 180, "MEMÓRIA RAM", "box_ram", "0x00000 - 0x7FFFF")

        self.canvas.create_rectangle(1000, 50, 1150, 150, fill="black", outline="#00ff00", width=2)
        self.canvas.create_text(1075, 40, text="MONITOR VRAM", fill="#00ff00", font=("Arial", 10))
        self.canvas.create_text(1075, 100, text="", fill="#00ff00", font=("Courier New", 16, "bold"), tags="vram_txt")

        self.desenhar_seta(140, 280, 180, 280, "bus_pc_reg", "")
        self.desenhar_seta(300, 260, 550, 260, "bus_rs1", "rs1")
        self.desenhar_seta(300, 320, 550, 320, "bus_rs2", "rs2")
        self.desenhar_seta(650, 290, 800, 290, "bus_sys", "Barramento Sistema")
        self.desenhar_seta(920, 290, 1000, 290, "bus_mem", "Barramento Memória")

        self.canvas.create_text(600, 500, text="Legenda: Amarelo = Ativo | Verde = Dados | Tecla 'K' = Interrupção", fill="gray")

    def acionar_interrupcao(self, event=None):
        self.cpu.solicitar_interrupcao()
        self.lbl_info.config(text="Status: INTERRUPÇÃO SOLICITADA!", fg=self.COR_ALERTA)

    def atualizar_tela(self):
        self.canvas.itemconfigure("box_pc_val", text=hex(self.cpu.pc))
        
        reg_txt = f"x10: {hex(self.cpu.ler_reg(10))}\nx11: {hex(self.cpu.ler_reg(11))}"
        self.canvas.itemconfigure("box_regs_val", text=reg_txt)
        
        self.canvas.itemconfigure("box_alu_val", text=f"Res: {hex(self.cpu.ult_res_alu)}")
        
        stats_cache = f"H: {self.barramento.cache.hits}\nM: {self.barramento.cache.misses}"
        self.canvas.itemconfigure("box_cache_val", text=stats_cache)
        self.lbl_stats.config(text=f"Cache Total: Hits={self.barramento.cache.hits} Misses={self.barramento.cache.misses}")

        op = self.cpu.op_atual
        self.lbl_info.config(text=f"Instrução Atual: {op}", fg="white")

        for tag in ["box_alu", "box_cache", "box_ram"]:
            self.canvas.itemconfigure(tag, fill=self.COR_COMPONENTE, outline="white")
        
        self.canvas.itemconfigure("bus_sys_txt", text="")

        if "STORE" in op:
            self.canvas.itemconfigure("box_alu", fill=self.COR_ATIVO)
            self.canvas.itemconfigure("box_cache", fill=self.COR_ATIVO)
            self.canvas.itemconfigure("box_ram", fill=self.COR_ATIVO)
            self.canvas.itemconfigure("bus_sys_txt", text=hex(self.cpu.ult_val_mem))
            
        elif "ALU" in op or "LUI" in op:
            self.canvas.itemconfigure("box_alu", fill=self.COR_ATIVO)
            
        elif "LOAD" in op:
            self.canvas.itemconfigure("box_cache", fill=self.COR_ATIVO)
            self.canvas.itemconfigure("bus_sys_txt", text=hex(self.cpu.ult_val_mem))

        vram = self.mem.obter_vram()
        txt = "".join([chr(b) for b in vram if 32 <= b <= 126])
        self.canvas.itemconfigure("vram_txt", text=txt)

    def proximo_passo(self):
        instr = self.cpu.busca()
        self.cpu.decodificar_executar(instr)
        self.atualizar_tela()

if __name__ == "__main__":
    raiz = tk.Tk()
    app = SimuladorVisual(raiz)
    raiz.mainloop()