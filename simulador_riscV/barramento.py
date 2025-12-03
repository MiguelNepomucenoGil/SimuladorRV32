from cache import Cache

class Barramento:
    def __init__(self, memoria):
        self.cache = Cache(memoria)

    def carregar(self, endereco, tamanho):
        val = 0
        for i in range(tamanho):
            val |= (self.cache.ler(endereco + i) << (8 * i))
        return val

    def armazenar(self, endereco, tamanho, valor):
        for i in range(tamanho):
            self.cache.escrever(endereco + i, (valor >> (8 * i)) & 0xFF)