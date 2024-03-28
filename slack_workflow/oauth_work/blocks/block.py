from json import dumps

def oauth_form(url: str) -> str:
    return dumps(
            {
                "type": "modal",
                "title": {
                    "type": "plain_text",
                    "text": "My App",
                    "emoji": True
                },
                "close": {
                    "type": "plain_text",
                    "text": "終了",
                    "emoji": True
                },
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "Freeeの認証を行ってください。"
                        },
                        "accessory": {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "認証サイトリンク",
                                "emoji": True
                            },
                            "url": url
                        }
                    }
                ]
            }
        )