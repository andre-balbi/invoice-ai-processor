"""
Processador de faturas usando Pydantic AI.
"""

import asyncio
from typing import List
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

# Módulos locais
from scripts.models import Invoice, ProcessedInvoice


class InvoiceProcessor:
    """Processador principal de faturas"""

    def __init__(self, model_name: str):
        """Inicializa o processador com modelo OpenAI"""
        self.model = OpenAIModel(model_name)

        # Agent para identificar campos
        self.schema_agent = Agent(
            model=self.model,
            output_type=List[str],
            system_prompt="""
            Você é um especialista em análise de faturas do Uber Eats.
            Analise o texto da fatura e retorne uma lista simples dos campos de dados encontrados, incluindo eventuais comentarios escritos por humanos.
            Foque nos campos essenciais: status do pedido, ID do pedido, data/hora, restaurante (nome, endereço, avaliações), itens (nome, preço unitário, quantidade), entregador (nome, tempo, distância, velocidade, altitude), valores monetários (subtotal, taxas, descontos, gorjeta, total).
            **NUNCA** inclua dados fictícios e/ou campos irrelevantes. Retorne apenas os campos identificados, sem explicações adicionais.
            """,
        )

        # Agent para extrair dados
        self.extraction_agent = Agent(
            model=self.model,
            output_type=Invoice,
            system_prompt="""
            Você é um especialista em extração de dados de faturas do Uber Eats.
            Extraia os dados da fatura de forma precisa e estruturada seguindo exatamente a estrutura dos modelos Pydantic.

            Diretrizes de Extração:

            PEDIDO:
            - order_id: ID único do pedido
            - date_time: Data e hora exatos da fatura

            ITENS DO PEDIDO:
            - name: Nome completo do item
            - price: Preço individual do item
            - quantity: Quantidade pedida

            RESTAURANTE:
            - name: Nome do restaurante
            - address: Endereço completo (se disponível)
            - total_reviews: Número total de avaliações
            - average_rating: Nota média das avaliações

            ENTREGADOR:
            - driver_name: Nome do entregador
            - delivery_time: Tempo de entrega em minutos
            - distance: Distância percorrida em quilômetros
            - average_speed: Velocidade média em km/h
            - altitude: Altitude em metros (se disponível)

            PAGAMENTO:
            - subtotal: Valor dos itens (obrigatório)
            - delivery_fee: Taxa de entrega
            - service_fee: Taxa de serviço
            - discount: Desconto aplicado
            - driver_tip: Gorjeta do entregador
            - total: Valor total final (obrigatório)

            IMPORTANTE: Se alguma informação não estiver disponível na fatura, use null/None para campos opcionais.
            """,
        )

    async def process_async(self, invoice_text: str) -> ProcessedInvoice:
        """Processa fatura de forma assíncrona"""

        # Etapa 1: Identificar campos
        print("🔍 Identificando campos da fatura...")
        schema_result = await self.schema_agent.run(f"Identifique os campos de dados nesta fatura:\n\n{invoice_text}")
        schema_fields = schema_result.output
        print(f"✅ Encontrados {len(schema_fields)} campos")

        # Etapa 2: Extrair dados
        print("📊 Extraindo dados da fatura...")
        extraction_result = await self.extraction_agent.run(
            f"Extraia os dados estruturados desta fatura:\n\n{schema_fields}"
        )
        invoice_data = extraction_result.output
        print("✅ Dados extraídos com sucesso")

        # Criar resultado processado
        return ProcessedInvoice(schema_fields=schema_fields, data=invoice_data)

    def process(self, invoice_text: str) -> ProcessedInvoice:
        """Processa fatura de forma síncrona"""
        return asyncio.run(self.process_async(invoice_text))


def create_processor(model_name: str = "gpt-4o-mini") -> InvoiceProcessor:
    """Factory function para criar processador"""
    return InvoiceProcessor(model_name)
