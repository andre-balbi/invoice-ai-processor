"""
Script principal para processamento de faturas.
"""

import shutil
from pathlib import Path
import nest_asyncio
from dotenv import load_dotenv

# Módulos locais
from scripts.processor import create_processor
from scripts.utils import get_invoice_summary, load_pdf_text, save_invoice_json

# Configurações
nest_asyncio.apply()  # Configurações para evitar problemas com loops de eventos aninhados


def process_invoice_file(pdf_path: Path, output_dir: Path) -> bool:
    """
    Processa um único arquivo de fatura.

    Args:
        pdf_path: Caminho para o arquivo PDF
        output_dir: Diretório de saída

    Returns:
        True se processamento foi bem-sucedido
    """
    try:
        print(f"\n📄 Processando: {pdf_path.name}")

        # 1. Extrair texto do PDF
        print("📖 Extraindo texto...")
        invoice_text = load_pdf_text(str(pdf_path))
        print(f"✅ Texto extraído ({len(invoice_text)} caracteres)")

        # 2. Processar com AI
        print("🤖 Processando com AI...")
        processor = create_processor()
        processed_invoice = processor.process(invoice_text)

        # 3. Salvar resultado
        output_file = output_dir / f"{pdf_path.stem}.json"
        save_invoice_json(processed_invoice, str(output_file))

        # 4. Mover PDF processado
        moved_pdf = output_dir / pdf_path.name
        shutil.move(str(pdf_path), str(moved_pdf))
        print(f"📁 PDF movido para: {moved_pdf}")

        # 5. Mostrar resumo
        summary = get_invoice_summary(processed_invoice)
        print("\n Resumo:")
        print(f"   Pedido: {summary['order_id']}")
        print(f"   Restaurante: {summary['restaurant']}")
        print(f"   Total: ${summary['total']:.2f}")
        print(f"   Itens: {summary['items_count']}")

        return True

    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        return False


def main():
    """Função principal"""

    print()
    print("=" * 60)
    print("            PROCESSADOR DE FATURAS UBER EATS")
    print("=" * 60)

    # Carregar variáveis de ambiente
    load_dotenv()

    # Definir diretórios
    src_dir = Path(__file__).parent
    raw_dir = src_dir / "data" / "raw"
    processed_dir = src_dir / "data" / "processed"

    # Verificar diretório de entrada
    if not raw_dir.exists():
        print(f"❌ Diretório não encontrado: {raw_dir}")
        return

    # Criar diretório de saída
    processed_dir.mkdir(parents=True, exist_ok=True)

    # Encontrar arquivos PDF
    pdf_files = list(raw_dir.glob("*.pdf"))
    if not pdf_files:
        print(f"Nenhum arquivo PDF encontrado em {raw_dir}")
        return

    print(f"📋 Encontrados {len(pdf_files)} arquivo(s) PDF")

    # Processar cada arquivo
    successful = 0
    failed = 0

    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"\n{'=' * 20} {i}/{len(pdf_files)} {'=' * 20}")

        if process_invoice_file(pdf_path, processed_dir):
            successful += 1
        else:
            failed += 1

    # Resumo final
    print(f"\n{'=' * 50}")
    print("Resultado Final:")
    print(f"   ✅ Sucesso: {successful}")
    print(f"   ❌ Falhas: {failed}")
    print(f"   📋 Total: {len(pdf_files)}")

    if failed == 0:
        print("Todos os arquivos processados com sucesso!")
    else:
        print(f"⚠️ {failed} arquivo(s) falharam")


if __name__ == "__main__":
    main()
