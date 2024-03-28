"""
新機能開発用のコマンドです。
/testコマンドと紐づいたメソッドを実装してください。
"""
from slack_bolt import Ack
from slack_sdk import WebClient

from app import bolt_app
from .blocks.block import test_block


@bolt_app.command("/test")
def test(ack: Ack, body: dict, client: WebClient, say):
    ack()
    client.chat_postMessage(
        channel="bot",
        text="テストです。",
        blocks=test_block()
        )