from typing import List
from fastapi import Depends, FastAPI, Response
from pydantic import BaseModel
from enum import Enum
from environs import Env
import requests
import uvicorn

env = Env()
env.read_env()


class Config:
    bind_address = env(
        "BIND_ADDRESS", "0.0.0.0")
    bind_port = env.int("BIND_PORT", "8080")
    domain_name = env("MAILGUN_DOMAIN_NAME")
    api_key = env("MAILGUN_API_KEY")
    target_emails = env.list("MAILGUN_TARGET_EMAILS")
    from_user = env("FROM_USER", "alerts")
    from_user_email = env("FROM_USER_EMAIL", "alerts")


app = FastAPI()


class Status(str, Enum):
    RESOLVED = "resolved"
    FIRING = "firing"


class Alert(BaseModel):
    status: Status
    labels: dict
    annotations: dict

    class Config:
        use_enum_values = True


class AlertmanagerData(BaseModel):
    alerts: List[Alert]


class MailgunApi:
    def __init__(self, domain_name: str, api_key: str, from_user: str, user_email_name: str = None) -> None:
        self.domain_name = domain_name
        self.api_key = api_key
        self.from_user = from_user
        self.user_email_name = user_email_name or from_user.replace(
            " ", "_").lower()

    def send_email(self, subject: str, text: str, to: List[str] | str) -> requests.Response:
        return requests.post(
            f"https://api.mailgun.net/v3/{self.domain_name}/messages",
            auth=("api", self.api_key),
            data={"from": f"{self.from_user} <{self.user_email_name}@{self.domain_name}>",
                  "to": (to if isinstance(to, list) else [to]),
                  "subject": subject,
                  "text": text})


def config():
    return Config()


def mailgun(config: Config = Depends(config)):
    return MailgunApi(config.domain_name, config.api_key, config.from_user, config.from_user_email)


@app.post("/")
def handle_alerts(data: AlertmanagerData,
                  response: Response,
                  api: MailgunApi = Depends(mailgun),
                  config: Config = Depends(config)
                  ):
    texts = [f"""STATUS: {alert.status}
    LABELS: {alert.labels}
    ANNOTATIONS: {alert.annotations}"""
             for alert in data.alerts]

    call_result = api.send_email("alert fired", "\n~~~\n".join(
        texts), config.target_emails)

    response.status_code = call_result.status_code
    return call_result.json()


if __name__ == "__main__":
    cfg = Config()
    uvicorn.run(app, host=cfg.bind_address, port=cfg.bind_port)
