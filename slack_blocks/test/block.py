from json import dumps

def test(url: str):
    d = dumps(
        {
            "type": "modal",
            "callback_id": "test",
            "title": {
                "type": "plain_text",
                "text": "有給申請フォーム",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "申請",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "キャンセル",
                "emoji": True
            },
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Click the link below:"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Open Link",
                            "emoji": True
                        },
                        "url": url
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "dispatch_action": True,
                    "type": "input",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "plain_text_input-action"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "認可コードを入力",
                        "emoji": True
                    }
                }
            ]
        }
    )
    return d