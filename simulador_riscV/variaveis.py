TAM_MEMORIA = 0xA0000
END_RAM_INI = 0x00000
END_VRAM_INI = 0x80000
END_IO_INI = 0x9FC00
END_HANDLER = 0x00000100

OP_R_TYPE = 0x33
OP_IMI_ALU = 0x13
OP_LOAD = 0x03
OP_STORE = 0x23
OP_BRANCH = 0x63
OP_JAL = 0x6F
OP_JALR = 0x67
OP_LUI = 0x37
OP_AUIPC = 0x17
OP_SISTEMA = 0x73

def estender_sinal(valor, bits):
    bit_sinal = 1 << (bits - 1)
    return (valor & (bit_sinal - 1)) - (valor & bit_sinal)