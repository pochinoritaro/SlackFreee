"""
OAuth2認証用のコマンドです。
/oauthコマンドと紐づいたメソッドを実装してください。
"""
from slack_bolt import Ack
from slack_sdk import WebClient

from app import bolt_app, human_resourse
from .blocks import oauth_form
from slack_blocks.error import error_dialog


@bolt_app.command("/oauth")
def oauth_form(ack: Ack, body: dict, client: WebClient):
    """OAuth2認証コマンド

    Description:
        Freeeの認証を行うコマンドです。
        管理者権限を持つユーザのみが実行できます。
    """
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