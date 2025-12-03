from variaveis import *

class CPU:
    def __init__(self, barramento):
        self.barramento = barramento
        self.pc = 0
        self.regs = [0] * 32
        
        self.interrupcao_pendente = False
        self.epc = 0
        
        self.ult_res_alu = 0
        self.ult_end_mem = 0
        self.ult_val_mem = 0
        self.op_atual = ""
        self.val_rs1 = 0
        self.val_rs2 = 0

    def ler_reg(self, indice):
        return 0 if indice == 0 else self.regs[indice]

    def esc_reg(self, indice, valor): 
        if indice != 0: self.regs[indice] = valor & 0xFFFFFFFF

    def solicitar_interrupcao(self):
        self.interrupcao_pendente = True

    def verificar_interrupcoes(self):
        if self.interrupcao_pendente:
            self.interrupcao_pendente = False
            self.epc = self.pc
            self.pc = END_HANDLER
            self.op_atual = "INTERRUPÇÃO!"
            return True
        return False

    def busca(self):
        return self.barramento.carregar(self.pc, 4)
    
    def decodificar_executar(self, instr):
        if self.verificar_interrupcoes():
            return

        opcode = instr & 0x7F
        rd = (instr >> 7) & 0x1F
        funct3 = (instr >> 12) & 0x07
        rs1 = (instr >> 15) & 0x1F
        rs2 = (instr >> 20) & 0x1F
        funct7 = (instr >> 25) & 0x7F
        
        imi_i = estender_sinal((instr >> 20), 12)
        imi_s = estender_sinal(((instr >> 25) << 5) | ((instr >> 7) & 0x1F), 12)
        imi_b = estender_sinal(((instr >> 31) << 12) | ((instr & 0x80) << 4) | ((instr >> 25) & 0x3F) << 5 | ((instr >> 8) & 0xF) << 1, 13)
        imi_u = (instr & 0xFFFFF000)
        imi_j = estender_sinal(((instr >> 31) << 20) | ((instr & 0xFF) << 12) | ((instr >> 20) & 0x1) << 11 | ((instr >> 21) & 0x3FF) << 1, 21)
        
        self.val_rs1 = self.ler_reg(rs1)
        self.val_rs2 = self.ler_reg(rs2)
        self.ult_end_mem = 0
        
        prox_pc = self.pc + 4
        
        if opcode == OP_LUI:
            self.op_atual = "LUI"
            res = imi_u
            self.ult_res_alu = res
            self.esc_reg(rd, res)

        elif opcode == OP_AUIPC:
            self.op_atual = "AUIPC"
            res = self.pc + imi_u
            self.ult_res_alu = res
            self.esc_reg(rd, res)

        elif opcode == OP_JAL:
            self.op_atual = "JAL"
            self.esc_reg(rd, self.pc + 4)
            prox_pc = self.pc + imi_j

        elif opcode == OP_JALR:
            self.op_atual = "JALR"
            t = self.pc + 4
            prox_pc = (self.val_rs1 + imi_i) & ~1
            self.esc_reg(rd, t)

        elif opcode == OP_BRANCH:
            self.op_atual = "BRANCH"
            tomar = False
            v1 = self.val_rs1
            v2 = self.val_rs2
            sv1 = v1 if v1 < 0x80000000 else v1 - 0x100000000
            sv2 = v2 if v2 < 0x80000000 else v2 - 0x100000000
            
            if funct3 == 0x0: tomar = (v1 == v2)
            elif funct3 == 0x1: tomar = (v1 != v2)
            elif funct3 == 0x4: tomar = (sv1 < sv2)
            elif funct3 == 0x5: tomar = (sv1 >= sv2)
            elif funct3 == 0x6: tomar = (v1 < v2)
            elif funct3 == 0x7: tomar = (v1 >= v2)
            
            if tomar:
                prox_pc = self.pc + imi_b

        elif opcode == OP_LOAD:
            self.op_atual = "LOAD"
            end = self.val_rs1 + imi_i
            self.ult_end_mem = end
            val = 0
            if funct3 == 0x0: val = estender_sinal(self.barramento.carregar(end, 1), 8)
            elif funct3 == 0x1: val = estender_sinal(self.barramento.carregar(end, 2), 16)
            elif funct3 == 0x2: val = self.barramento.carregar(end, 4)
            elif funct3 == 0x4: val = self.barramento.carregar(end, 1)
            elif funct3 == 0x5: val = self.barramento.carregar(end, 2)
            self.ult_val_mem = val
            self.esc_reg(rd, val)

        elif opcode == OP_STORE:
            self.op_atual = "STORE"
            end = self.val_rs1 + imi_s
            val = self.val_rs2
            self.ult_end_mem = end
            self.ult_val_mem = val
            if funct3 == 0x0: self.barramento.armazenar(end, 1, val & 0xFF)
            elif funct3 == 0x1: self.barramento.armazenar(end, 2, val & 0xFFFF)
            elif funct3 == 0x2: self.barramento.armazenar(end, 4, val)

        elif opcode == OP_IMI_ALU:
            self.op_atual = "ALU (Imediato)"
            v1 = self.val_rs1
            sv1 = v1 if v1 < 0x80000000 else v1 - 0x100000000
            res = 0
            if funct3 == 0x0: res = v1 + imi_i
            elif funct3 == 0x2: res = 1 if sv1 < imi_i else 0
            elif funct3 == 0x3: res = 1 if v1 < (imi_i & 0xFFFFFFFF) else 0
            elif funct3 == 0x4: res = v1 ^ imi_i
            elif funct3 == 0x6: res = v1 | imi_i
            elif funct3 == 0x7: res = v1 & imi_i
            elif funct3 == 0x1: res = v1 << (imi_i & 0x1F)
            elif funct3 == 0x5:
                shamt = imi_i & 0x1F
                if (instr >> 30) == 0: res = v1 >> shamt
                else: res = sv1 >> shamt
            self.ult_res_alu = res
            self.esc_reg(rd, res)

        elif opcode == OP_R_TYPE:
            self.op_atual = "ALU (Reg-Reg)"
            v1 = self.val_rs1
            v2 = self.val_rs2
            sv1 = v1 if v1 < 0x80000000 else v1 - 0x100000000
            sv2 = v2 if v2 < 0x80000000 else v2 - 0x100000000
            res = 0
            if funct7 == 0x00:
                if funct3 == 0x0: res = v1 + v2
                elif funct3 == 0x1: res = v1 << (v2 & 0x1F)
                elif funct3 == 0x2: res = 1 if sv1 < sv2 else 0
                elif funct3 == 0x3: res = 1 if v1 < v2 else 0
                elif funct3 == 0x4: res = v1 ^ v2
                elif funct3 == 0x5: res = v1 >> (v2 & 0x1F)
                elif funct3 == 0x6: res = v1 | v2
                elif funct3 == 0x7: res = v1 & v2
            elif funct7 == 0x20:
                if funct3 == 0x0: res = v1 - v2
                elif funct3 == 0x5: res = sv1 >> (v2 & 0x1F)
            self.ult_res_alu = res
            self.esc_reg(rd, res)
            
        elif opcode == OP_SISTEMA:
            self.op_atual = "SYSTEM"
            if funct3 == 0 and imi_i == 0x302:
                self.op_atual = "MRET (Retorno)"
                prox_pc = self.epc

        self.pc = prox_pc