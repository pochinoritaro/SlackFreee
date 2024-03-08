from json import dumps, loads
from os import environ

#TODO OAuthのコールバックで使用
from urllib.parse import parse_qs

from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler

from slack_bolt import App, Ack
from slack_sdk import WebClient

from Freee import HumanResourse
from Freee.freee_sdk.errors import UnAuthorizedError

# モーダルのブロック
from slack_blocks.paid_holiday import (
    paid_holiday_approval_form,
    paid_holiday_approval_resule,
    paid_holiday_request_form,
    paid_holiday_rejection_form
)
from slack_blocks.oauth import oauth_form
from slack_blocks.error import error_dialog

# Freeeのワークフロー
from freee_workflow import paid

from Freee.freee_sdk.errors import (
    AccessDeniedError,
    BadRequestError
)


bolt_app = App(
    token=environ["SLACK_BOT_TOKEN"],
    signing_secret=environ["SLACK_SIGNING_SECRET"]
)
app_handler = SlackRequestHandler(bolt_app)

human_resourse = HumanResourse(
    client_id=environ["CLIENT_ID"],
    client_secret=environ["CLIENT_SECRET"],
    redirect_uri=environ["REDIRECT_URI"],
    )

# コマンド
@bolt_app.command("/oauth")
def test_form(ack: Ack, body: dict, client: WebClient, say):
    user_id = body["user_id"]
    ack()
    # ユーザ権限を確認
    if client.users_info(user=user_id)["user"]["is_admin"] == True:
        try:
            client.views_open(
                trigger_id=body["trigger_id"],
                view=oauth_form(
                    url=human_resourse.oauth.get_auth_url()
                    )
                )

        except Exception as e:
            print(f"エラーが発生しました: {e}")

    else:
        client.views_open(
            trigger_id=body["trigger_id"],
            view=error_dialog(message="ユーザー権限がありません。"),
        )

# 有給申請
@bolt_app.command("/form")
def paid_holiday_request(ack: Ack, command, body: dict, client: WebClient):
    ack()
    try:
        # command リクエストを確認
        client.views_open(
            trigger_id=body["trigger_id"],
            view=paid_holiday_request_form(),
            )

    except Exception as e:
        print(f"エラーが発生しました: {e}")

# 有給申請送信時の処理
@bolt_app.view("paid_holiday_request")
def paid_holiday_request_callback(ack: Ack, body, view: dict, client: WebClient):
    user_id = body["user"]["id"]
    user_email = client.users_info(user=user_id)["user"]["profile"]["email"]
    user_name = client.users_info(user=user_id)["user"]["profile"]["real_name"]
    date = view["state"]["values"]["application_datepick_form"]["picked_date"]["selected_date"]
    reason = view["state"]["values"]["application_reason_form"]["reason"]["value"]
    ack()
    client.chat_postMessage(
            channel="有給登録",
            text=f"{user_name}さんから有給の申請が届きました。",
            blocks=paid_holiday_approval_form(user_name=user_name, date=date, reason=reason, user_id=user_id, user_email=user_email)
            #attachments=paid_holiday_approval_form(date=date, reason=reason, user_id=user_id, user_email=user_email),
            )


# 有給申請承認時
@bolt_app.block_action("paid_holiday_request_approval")
def paid_holiday_approval_callback(ack: Ack, body, view: dict, client: WebClient):
    ack()
    channel_id = body["container"]["channel_id"]
    user_id = body["user"]["id"]
    user_name = client.users_info(user=user_id)["user"]["profile"]["real_name"]
    attachments = body["message"]["attachments"]
    print(attachments)
    
    #TODO ブロックの説明欄にEメールのアドレスをぶち込んでる。(後日調べなおす)
    paid_holiday_info = attachments[0]["fallback"]
    print(paid_holiday_info["user_email"])
    try:
        approval = paid(
            date=paid_holiday_info["date"],
            reason=paid_holiday_info["reason"],
            email=paid_holiday_info["user_email"],
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
        attachments[0]["blocks"][1] = {"type": "section", "text": {"type": "plain_text", "text": f"{user_name}さんが承認しました。"}}
        client.chat_update(
            channel=channel_id,
            text=body["message"]["text"],
            attachments=attachments,
            ts=ts
        )
        
        conversation =  client.conversations_open(users=paid_holiday_info["user_id"])
        dm_channel_id = conversation["channel"]["id"]
        client.chat_postMessage(
            channel=dm_channel_id,
            text="有給が承認されました。",
            attachments=paid_holiday_approval_resule(
                date=paid_holiday_info["date"],
                reason=paid_holiday_info["reason"],
            )
        )


# 有給申請差し戻し時
@bolt_app.block_action("paid_holiday_request_rejection")
def paid_holiday_approval_callback(ack: Ack, body, view: dict, client: WebClient):
    approval_user_text = body["message"]["text"]
    channel_id = body["container"]["channel_id"]
    ts = body["container"]["message_ts"]
    paid_holiday_info = loads(body["actions"][0]["value"])
    blocks = body["message"]["blocks"]
    ack()
    client.views_open(
        trigger_id=body["trigger_id"],
        view=paid_holiday_rejection_form(
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
    reason = view["state"]["values"]["rejection_form"]["request_reason"]["value"]
    #TODO jsonモジュールをblockライブラリに移行
    paid_holiday_info = loads(body["view"]["private_metadata"])
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


from fastapi import FastAPI, Request

fast_api = FastAPI()

# Slackのイベントを受け取る
@fast_api.post("/slack/events")
async def slack_events_endpoint(request: Request):
    return await app_handler.handle(request)


#TODO いったん完成、要リファクタリング
#TODO OAuthをクラス切り分け済(2024/02/08)
@fast_api.get("/freee/callback")
async def slack_events_endpoint(request: Request):
    print("oauth callback")
    state = parse_qs(str(request.query_params))["code"][0]
    try:
        response = human_resourse.oauth.get_access_token(state=state)
        print(response)
        human_resourse.access_token = response["access_token"]
        human_resourse.refresh_token = response["refresh_token"]
        human_resourse.token_create_at = response["expires_in"]
        human_resourse.company_id = human_resourse.get_users_me()["companies"][0]["id"]
        print(human_resourse.access_token)
        print(human_resourse.company_id)
        return "アクセストークンを生成しました。"
    
    except UnAuthorizedError:
        return "アクセストークンの生成に失敗しました。"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="app:fast_api", host="0.0.0.0", port=3040, reload=True)