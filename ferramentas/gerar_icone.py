"""Desenha o ícone do painel e grava painel/recursos/icone.ico.

Só usa a biblioteca padrão, para o kit não ganhar dependência por causa de um ícone.
Rode de novo só se quiser mudar o desenho: python ferramentas/gerar_icone.py
"""

import struct
import sys
import zlib
from pathlib import Path

DESTINO = Path(__file__).resolve().parents[1] / "painel" / "recursos" / "icone.ico"
TAMANHOS = (16, 24, 32, 48, 64, 128, 256)
TAMANHO_EM_PNG = 256  # O Windows aceita PNG dentro do .ico só na entrada grande; as demais vão em BMP.
AMOSTRAS = 4  # Cada pixel é a média de 4x4 amostras: é o que suaviza as bordas.

# Desenho em coordenadas de 0 a 1: uma batuta (o maestro) e três pontos (os agentes).
RAIO_DO_FUNDO = 0.22
COR_TOPO = (88, 80, 220)
COR_BASE = (38, 34, 128)
BRANCO = (255, 255, 255)
COR_DOS_PONTOS = (125, 227, 244)
BATUTA_INICIO = (0.27, 0.75)
BATUTA_FIM = (0.66, 0.24)
ESPESSURA_DA_BATUTA = 0.058
RAIO_DO_CABO = 0.082
RAIO_DO_PONTO = 0.052
PONTOS = ((0.52, 0.80), (0.68, 0.71), (0.79, 0.56))


def _dentro_do_fundo(x: float, y: float) -> bool:
    # Quadrado de cantos arredondados: mede a distância até o "miolo" sem os cantos.
    dx = max(abs(x - 0.5) - (0.5 - RAIO_DO_FUNDO), 0.0)
    dy = max(abs(y - 0.5) - (0.5 - RAIO_DO_FUNDO), 0.0)
    return dx * dx + dy * dy <= RAIO_DO_FUNDO * RAIO_DO_FUNDO


def _distancia_ao_segmento(x: float, y: float) -> float:
    (ax, ay), (bx, by) = BATUTA_INICIO, BATUTA_FIM
    vx, vy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((x - ax) * vx + (y - ay) * vy) / (vx * vx + vy * vy)))
    return ((x - ax - t * vx) ** 2 + (y - ay - t * vy) ** 2) ** 0.5


def _cor_da_amostra(x: float, y: float) -> tuple[int, int, int, int]:
    if not _dentro_do_fundo(x, y):
        return (0, 0, 0, 0)
    ax, ay = BATUTA_INICIO
    no_cabo = (x - ax) ** 2 + (y - ay) ** 2 <= RAIO_DO_CABO**2
    if no_cabo or _distancia_ao_segmento(x, y) <= ESPESSURA_DA_BATUTA / 2:
        return (*BRANCO, 255)
    if any((x - px) ** 2 + (y - py) ** 2 <= RAIO_DO_PONTO**2 for px, py in PONTOS):
        return (*COR_DOS_PONTOS, 255)
    return (*(round(a + (b - a) * y) for a, b in zip(COR_TOPO, COR_BASE)), 255)


def desenhar(tamanho: int) -> list[tuple[int, int, int, int]]:
    """Pixels RGBA, linha a linha de cima para baixo."""
    lado = tamanho * AMOSTRAS
    total = AMOSTRAS * AMOSTRAS
    pixels = []
    for py in range(tamanho):
        for px in range(tamanho):
            r = g = b = a = 0
            for sy in range(AMOSTRAS):
                for sx in range(AMOSTRAS):
                    cr, cg, cb, ca = _cor_da_amostra(
                        (px * AMOSTRAS + sx + 0.5) / lado, (py * AMOSTRAS + sy + 0.5) / lado
                    )
                    r, g, b, a = r + cr * ca, g + cg * ca, b + cb * ca, a + ca
            # Média ponderada pelo alfa: a borda não escurece com as amostras transparentes.
            pixels.append((r // a, g // a, b // a, a // total) if a else (0, 0, 0, 0))
    return pixels


def _bloco_png(tipo: bytes, dados: bytes) -> bytes:
    return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados))


def em_png(tamanho: int, pixels: list) -> bytes:
    linhas = b"".join(
        b"\x00" + b"".join(bytes(p) for p in pixels[y * tamanho : (y + 1) * tamanho])
        for y in range(tamanho)
    )
    cabecalho = struct.pack(">IIBBBBB", tamanho, tamanho, 8, 6, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _bloco_png(b"IHDR", cabecalho)
        + _bloco_png(b"IDAT", zlib.compress(linhas, 9))
        + _bloco_png(b"IEND", b"")
    )


def em_bmp_de_icone(tamanho: int, pixels: list) -> bytes:
    # No .ico a altura declarada é o dobro (imagem + máscara) e as linhas vão de baixo para cima.
    cabecalho = struct.pack("<IiiHHIIiiII", 40, tamanho, tamanho * 2, 1, 32, 0, 0, 0, 0, 0, 0)
    cores = b"".join(
        bytes((b, g, r, a))
        for y in range(tamanho - 1, -1, -1)
        for r, g, b, a in pixels[y * tamanho : (y + 1) * tamanho]
    )
    mascara = bytes(((tamanho + 31) // 32) * 4 * tamanho)  # zerada: quem decide é o alfa
    return cabecalho + cores + mascara


def gerar() -> None:
    imagens = []
    for tamanho in TAMANHOS:
        pixels = desenhar(tamanho)
        codificar = em_png if tamanho >= TAMANHO_EM_PNG else em_bmp_de_icone
        imagens.append((tamanho, codificar(tamanho, pixels)))
        if tamanho == TAMANHO_EM_PNG and len(sys.argv) > 1:
            Path(sys.argv[1]).write_bytes(em_png(tamanho, pixels))  # prévia opcional

    deslocamento = 6 + 16 * len(imagens)
    indice, corpo = b"", b""
    for tamanho, dados in imagens:
        lado = 0 if tamanho >= 256 else tamanho  # no .ico, 0 significa 256
        indice += struct.pack("<BBBBHHII", lado, lado, 0, 0, 1, 32, len(dados), deslocamento)
        corpo += dados
        deslocamento += len(dados)
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_bytes(struct.pack("<HHH", 0, 1, len(imagens)) + indice + corpo)
    print(f"Gravado {DESTINO} ({DESTINO.stat().st_size} bytes, {len(imagens)} tamanhos)")


if __name__ == "__main__":
    gerar()
