from json import dumps

def error_dialog(message: str):
    return dumps(
        {
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "エラー",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "閉じる",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": message,
                        "emoji": True
                    }
                }
            ]
        }
    )
