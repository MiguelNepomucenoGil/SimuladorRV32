class Cache:
    def __init__(self, memoria_ref):
        self.mem_principal = memoria_ref
        self.linhas = 256
        self.tamanho_bloco = 4
        self.cache_interna = {} 
        self.hits = 0
        self.misses = 0

    def ler(self, endereco):
        indice = (endereco // self.tamanho_bloco) % self.linhas
        tag = (endereco // self.tamanho_bloco) // self.linhas
        
        linha = self.cache_interna.get(indice)
        
        if linha and linha['tag'] == tag:
            self.hits += 1
            offset = endereco % self.tamanho_bloco
            return linha['dados'][offset]
        
        self.misses += 1
        endereco_base = (endereco // self.tamanho_bloco) * self.tamanho_bloco
        bloco = []
        for i in range(self.tamanho_bloco):
            bloco.append(self.mem_principal.ler(endereco_base + i))
        
        self.cache_interna[indice] = {'tag': tag, 'dados': bloco}
        return bloco[endereco % self.tamanho_bloco]

    def escrever(self, endereco, valor):
        self.mem_principal.escrever(endereco, valor)
        
        indice = (endereco // self.tamanho_bloco) % self.linhas
        tag = (endereco // self.tamanho_bloco) // self.linhas
        
        linha = self.cache_interna.get(indice)
        if linha and linha['tag'] == tag:
            linha['dados'][endereco % self.tamanho_bloco] = valor & 0xFF