"""
有給申請用のコマンドです。
/testコマンドと紐づいたメソッドを実装してください。
"""
import json
from slack_bolt import Ack
from slack_sdk import WebClient

from Freee.freee_sdk.errors import (
    AccessDeniedError,
    BadRequestError
)
from app import bolt_app, human_resourse
from .blocks import (
    paid_holiday_approval_form,
    paid_holiday_rejection_modal,
    paid_holiday_request_modal
)
from .works import approval_paid_holiday
from slack_blocks.error import error_dialog


@bolt_app.command("/form")
def paid_holiday_request(ack: Ack, command, body: dict, client: WebClient):
    """
    有給申請フォームを表示します。
    """
    ack()
    try:
        # command リクエストを確認
        client.views_open(
            trigger_id=body["trigger_id"],
            view=paid_holiday_request_modal(),
            )

    #TODO もっと具体的なエラーハンドリングを    
    except Exception as e:
        print(f"エラーが発生しました: {e}")



@bolt_app.view("paid_holiday_request")
def paid_holiday_request_callback(ack: Ack, body, view: dict, client: WebClient):
    """
    送信された有給申請情報を「有給登録」チャンネルに通知します。
    """
    user_id = body["user"]["id"]
    user_email = client.users_info(user=user_id)["user"]["profile"]["email"]
    user_name = client.users_info(user=user_id)["user"]["profile"]["real_name"]
    request_date = view["state"]["values"]["application_datepick_form"]["picked_date"]["selected_date"]
    request_reason = view["state"]["values"]["application_reason_form"]["reason"]["value"]
    ack()
    client.chat_postMessage(
        channel="有給登録",
        text=f"{user_name}さんから有給の申請が届きました。",
        blocks=paid_holiday_approval_form(
            user_name=user_name,
            request_date=request_date,
            request_reason=request_reason,
            user_id=user_id,
            user_email=user_email
        )
    )


@bolt_app.block_action("paid_holiday_request_approval")
def paid_holiday_approval_callback(ack: Ack, body, client: WebClient):
    """
    通知された有給を承認した際の処理
    """
    channel_id = body["container"]["channel_id"]
    user_id = body["user"]["id"]
    user_name = client.users_info(user=user_id)["user"]["profile"]["real_name"]
    blocks = body["message"]["blocks"]
    ack()
    
    #TODO ブロックの説明欄にEメールのアドレスをぶち込んでる。(後日調べなおす)
    paid_holiday_info = json.json.loads(body["actions"][0]["value"])
    try:
        approval_paid_holiday(
            request_date=paid_holiday_info["date"],
            request_reason=paid_holiday_info["reason"],
            user_email=paid_holiday_info["user_email"],
            hr=human_resourse
        )

    except AccessDeniedError as e:
        client.chat_postMessage(
            channel=channel_id,
            text="⚠️アクセストークンを発行してください。"
        )

    except BadRequestError as e:
        #TODO 見直し必須
        client.views_open(
            trigger_id=body["trigger_id"],
            view=error_dialog(message="使用可能な有給がありません。"),
            )

    else:
        ts = body["container"]["message_ts"]
        blocks[3] = dict(
            type="section",
            text=dict(
                type="plain_text",
                text=f"{user_name}さんが承認しました。"
            )
        )

        
        client.chat_update(
            channel=channel_id,
            text="text",
            blocks=blocks,
            ts=ts
        )
        
        blocks[1] = dict(
            type="section",
            text=dict(
                type="plain_text",
                text=f"有給が承認されました。"
            )
        )
        del blocks[3]
        conversation =  client.conversations_open(users=paid_holiday_info["user_id"])
        dm_channel_id = conversation["channel"]["id"]
        client.chat_postMessage(
            channel=dm_channel_id,
            text="有給が承認されました。",
            blocks=blocks
        )


# 有給申請差し戻し時
@bolt_app.block_action("paid_holiday_request_rejection")
def paid_holiday_approval_callback(ack: Ack, body, view: dict, client: WebClient):
    """
    通知された有給を差し戻した際の処理
    """
    approval_user_text = body["message"]["text"]
    channel_id = body["container"]["channel_id"]
    ts = body["container"]["message_ts"]
    paid_holiday_info = json.loads(body["actions"][0]["value"])
    blocks = body["message"]["blocks"]
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view=paid_holiday_rejection_modal(
            dict(
                approval_user_text=approval_user_text,
                blocks=blocks,
                ts=ts,
                channel_id=channel_id,
                paid_holiday_info=paid_holiday_info
                )
            ),
        )


# 有給申請差し戻し時の処理
@bolt_app.view("paid_holiday_rejection")
def paid_holiday_rejection_callback(ack: Ack, body, view: dict, client: WebClient):
    """
    有給が差し戻された際に通知を「差し戻し済」に変更し、
    申請者にダイレクトメッセージを送信します。
    """
    reason = view["state"]["values"]["rejection_form"]["request_reason"]["value"]
    #TODO jsonモジュールをblockライブラリに移行
    paid_holiday_info = json.loads(body["view"]["private_metadata"])
    channel_id = paid_holiday_info["channel_id"]
    blocks = paid_holiday_info["blocks"]
    blocks[3] = dict(
        type="section",
        text=dict(
            type="plain_text",
            text=f"・却下理由: {reason}"
        )
    )
    request_user_dict = blocks.pop(1)
    blocks.insert(
        1,
        dict(
            type="section",
            text=dict(
                type="plain_text",
                text="申請が却下されました。"
            )
        )
    )
    ack()
    # ユーザに却下のDMを送信
    conversation =  client.conversations_open(users=paid_holiday_info["paid_holiday_info"]["user_id"])
    dm_channel_id = conversation["channel"]["id"]
    client.chat_postMessage(
        channel=dm_channel_id,
        text="test",
        blocks=blocks
    )
    # 有給登録のメッセージを編集する
    user_name = client.users_info(user=body["user"]["id"])["user"]["profile"]["real_name"]
    blocks[1] = request_user_dict
    blocks.insert(
        3,
        dict(
            type="section",
            text=dict(
                type="plain_text",
                text=f"{user_name}さんが却下しました。"
            )
        )
    )
    client.chat_update(
        #TODO bodyからチャンネルIDを取得したい
        channel=channel_id,
        text="test",
        blocks=blocks,
        ts=paid_holiday_info["ts"]
    )
