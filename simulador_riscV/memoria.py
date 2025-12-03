from variaveis import TAM_MEMORIA, END_VRAM_INI

class Memoria:
    def __init__(self):
        self.dados = bytearray(TAM_MEMORIA)

    def ler(self, endereco):
        if 0 <= endereco < len(self.dados):
            return self.dados[endereco]
        return 0

    def escrever(self, endereco, valor):
        if 0 <= endereco < len(self.dados):
            self.dados[endereco] = valor & 0xFF

    def carregar_prog(self, binario, inicio=0):
        for i, byte in enumerate(binario):
            self.escrever(inicio + i, byte)

    def obter_vram(self):
        return self.dados[END_VRAM_INI : 0x8FFFF + 1]