"""
Modelos Pydantic para processamento de faturas.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class OrderStatus(str, Enum):
    """Status possíveis do pedido"""

    CONCLUIDO = "concluido"
    PENDENTE = "pendente"


class OrderItem(BaseModel):
    """Item do pedido"""

    name: str = Field(..., description="Nome do item")
    price: Decimal = Field(..., description="Preço do item")
    quantity: int = Field(default=1, description="Quantidade")


class Restaurant(BaseModel):
    """Informações do restaurante"""

    name: str = Field(..., description="Nome do restaurante")
    address: Optional[str] = Field(None, description="Endereço")
    total_reviews: int = Field(None, description="Total de avaliações")
    average_rating: Decimal = Field(None, description="Nota média das avaliações")


class DeliveryDriver(BaseModel):
    """Informações do entregador"""

    driver_name: Optional[str] = Field(None, description="Nome do entregador")
    delivery_time: Optional[int] = Field(None, description="Tempo de entrega em minutos")
    distance: Optional[Decimal] = Field(None, description="Distância em quilômetros")
    average_speed: Optional[Decimal] = Field(None, description="Velocidade média em km/h")


class PaymentSummary(BaseModel):
    """Resumo do pagamento"""

    subtotal: Decimal = Field(..., description="Subtotal")
    delivery_fee: Optional[Decimal] = Field(None, description="Taxa de entrega")
    service_fee: Optional[Decimal] = Field(None, description="Taxa de serviço")
    discount: Optional[Decimal] = Field(None, description="Desconto aplicado")
    driver_tip: Optional[Decimal] = Field(None, description="Gorjeta do entregador")
    total: Decimal = Field(..., description="Total final")


class Invoice(BaseModel):
    """Fatura completa"""

    order_status: OrderStatus = Field(..., description="Status do pedido")
    order_id: str = Field(..., description=" #ID do pedido")
    date_time: str = Field(..., description="Data e hora")
    restaurant: Restaurant = Field(..., description="Restaurante")
    items: List[OrderItem] = Field(..., description="Itens do pedido")
    deliver_driver: DeliveryDriver = Field(..., description="Entregador")
    payment: PaymentSummary = Field(..., description="Resumo do pagamento")
    processed_at: datetime = Field(default_factory=datetime.now, description="Data de processamento")


class ProcessedInvoice(BaseModel):
    """Fatura processada com schema e dados"""

    schema_fields: List[str] = Field(..., description="Campos identificados")
    data: Invoice = Field(..., description="Dados extraídos")
