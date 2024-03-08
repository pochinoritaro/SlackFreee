from datetime import datetime
from json import dumps

def paid_holiday_request_form():
    return dumps(
        {
            "type": "modal",
            "callback_id": "paid_holiday_request",
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
                    "type": "input",
                    "block_id": "application_datepick_form",
                    "element": {
                        "type": "datepicker",
                        "initial_date": datetime.now().strftime("%Y-%m-%d"),
                        "placeholder": {
                            "type": "plain_text",
                            "text": "申請日を選択",
                            "emoji": True
                        },
                        "action_id": "picked_date"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "申請日",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "block_id": "application_reason_form",
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "reason"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "申請理由",
                        "emoji": True
                    }
                }
            ]
        }
    )


def paid_holiday_approval_form(date: str, reason: str, user_id: str, user_email: str):
    return dumps(
        [
            {
                "fallback": dict(date=date, reason=reason, user_id=user_id, user_email=user_email),
                "blocks": [
                    {
                        "type": "section",
                        "text": {
                            "type": "plain_text",
                            "text": f"・日時: {date}\n・理由: {reason}"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "承認",
                                    "emoji": True
                                },
                                "value": "approval",
                                "action_id": "paid_holiday_request_approval"
                            },
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "差し戻し",
                                    "emoji": True
                                },
                                "value": "rejection",
                                "action_id": "paid_holiday_request_rejection"
                            }
                        ]
                    }
                ]
            }
        ]
    )


def paid_holiday_rejection_form(private_metadata: dict):
    return dumps(
        {
            "callback_id": "paid_holiday_rejection",
            "type": "modal",
            "title": {
                "type": "plain_text",
                "text": "My App",
                "emoji": True
            },
            "submit": {
                "type": "plain_text",
                "text": "Submit",
                "emoji": True
            },
            "close": {
                "type": "plain_text",
                "text": "Cancel",
                "emoji": True
            },
            "private_metadata": dumps(private_metadata),
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "plain_text",
                        "text": "差し戻し理由を入力してください。",
                        "emoji": True
                    }
                },
                {
                    "type": "input",
                    "block_id": "rejection_form",
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "request_reason"
                    },
                    "label": {
                        "type": "plain_text",
                        "text": "理由",
                        "emoji": True
                    }
                }
            ]
        }
    )


def paid_holiday_approval_resule(date: str, reason: str):
    return dumps(
                    [
                        {
                            "blocks": [
                                {
                                    "type": "section",
                                    "text": {
                                        "type": "plain_text",
                                        "text": f"・日時: {date}\n・理由: {reason}"
                                    }
                                }
                            ]
                        }
                    ]
                )
            