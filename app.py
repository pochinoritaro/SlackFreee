from os import environ
from urllib.parse import parse_qs
from fastapi import FastAPI, Request
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from Freee import HumanResourse
from Freee.freee_sdk.errors import UnAuthorizedError


human_resourse = HumanResourse(
    client_id=environ["CLIENT_ID"],
    client_secret=environ["CLIENT_SECRET"],
    redirect_uri=environ["REDIRECT_URI"],
    )

bolt_app = App(
    token=environ["SLACK_BOT_TOKEN"],
    signing_secret=environ["SLACK_SIGNING_SECRET"]
)

app_handler = SlackRequestHandler(bolt_app)

fast_api = FastAPI()


@fast_api.post("/slack/events")
async def slack_events_endpoint(request: Request):
    return await app_handler.handle(request)


@fast_api.get("/freee/callback")
async def slack_events_endpoint(request: Request):
    print("oauth callback")
    state = parse_qs(str(request.query_params))["code"][0]
    try:
        response = human_resourse.oauth.get_access_token(state=state)
        human_resourse.access_token = response["access_token"]
        human_resourse.refresh_token = response["refresh_token"]
        human_resourse.token_create_at = response["expires_in"]
        human_resourse.company_id = human_resourse.get_users_me()["companies"][0]["id"]
        return "アクセストークンを生成しました。"
    
    except UnAuthorizedError:
        return "アクセストークンの生成に失敗しました。"

# 各コマンド等をimport(ここに表記しないと循環参照になってしまいます。)
from slack_work_flow.oauth_work import oauth_command
from slack_work_flow.paid_holiday_work import paid_holiday_command
from slack_work_flow.test_work import test_command


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app="app:fast_api", host="0.0.0.0", port=3040, reload=True)
