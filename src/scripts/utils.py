"""
Utilitários simples para processamento de faturas.
Foco em funcionalidade essencial sem complexidade desnecessária.
"""

import json
from pathlib import Path
from typing import Dict, Any

import scripts.suppress_warnings  # Configurações para suprimir avisos
import pdfplumber

from scripts.models import ProcessedInvoice


def load_pdf_text(pdf_path: str) -> str:
    """
    Extrai texto de arquivo PDF.

    Args:
        pdf_path: Caminho para o arquivo PDF

    Returns:
        Texto extraído do PDF

    Raises:
        Exception: Se não for possível extrair o texto
    """

    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"

        if not text.strip():
            raise Exception("Nenhum texto encontrado no PDF")

        return text.strip()

    except Exception as e:
        raise Exception(f"Erro ao extrair texto do PDF: {str(e)}")


def save_invoice_json(invoice: ProcessedInvoice, output_path: str) -> None:
    """
    Salva fatura processada em arquivo JSON.

    Args:
        invoice: Fatura processada
        output_path: Caminho do arquivo de saída
    """
    try:
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Converte para dicionário serializável
        invoice_dict = invoice.model_dump(mode="json")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(invoice_dict, f, ensure_ascii=False, indent=2, default=str)

        print(f"✅ Fatura salva em: {output_path}")

    except Exception as e:
        raise Exception(f"Erro ao salvar fatura: {str(e)}")


def load_invoice_json(input_path: str) -> ProcessedInvoice:
    """
    Carrega fatura processada de arquivo JSON.

    Args:
        input_path: Caminho do arquivo JSON

    Returns:
        Fatura processada
    """
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ProcessedInvoice.model_validate(data)

    except Exception as e:
        raise Exception(f"Erro ao carregar fatura: {str(e)}")


def get_invoice_summary(invoice: ProcessedInvoice) -> Dict[str, Any]:
    """
    Cria resumo da fatura processada.

    Args:
        invoice: Fatura processada

    Returns:
        Dicionário com resumo da fatura
    """
    data = invoice.data

    return {
        "order_id": data.order_id,
        "restaurant": data.restaurant.name,
        "date": data.date_time,
        "total": float(data.payment.total),
        "items_count": len(data.items),
        "items": [{"name": item.name, "price": float(item.price)} for item in data.items],
    }
