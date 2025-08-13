import asyncio
import aio_pika
import json
from app.messaging.conection import get_connection
from app.database import SessionLocal
from app.crud.orders import finalize_order_logic
from fastapi import HTTPException
import os

QUEUE_NAME = os.getenv('QUEUE_NAME', 'order_queue')

async def process_order(message: aio_pika.IncomingMessage):
    async with message.process():
        try:
            order_data = json.loads(message.body)
            print("Mensagem recebida JSON:", order_data)
        except json.JSONDecodeError:
            print("Mensagem inválida: não é um JSON válido")
            return

        order_id = order_data.get('order_id')
        if not order_id:
            print("Mensagem inválida: order_id faltando")
            return

        print(f"Processando pedido: {order_id}")

        def sync_finalize():
            with SessionLocal() as db:
                try:
                    result = finalize_order_logic(order_id, db)
                    print("Resultado da finalização do pedido:", result)
                    return result
                except HTTPException as e:
                    print(f"Erro na finalização do pedido {order_id}: {e.detail}")
                    return None
                except Exception as e:
                    print(f"Erro inesperado ao finalizar pedido {order_id}: {e}")
                    return None

        result = await asyncio.to_thread(sync_finalize)

        if result:
            print(f"Pedido {order_id} processado e finalizado com sucesso")
        else:
            print(f"Falha ao processar pedido {order_id}")

async def main():
    connection = await get_connection()
    channel = await connection.channel()
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)
    await queue.consume(process_order)
    print("Worker aguardando pedidos...")
    await asyncio.Future()
