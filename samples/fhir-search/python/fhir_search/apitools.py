from typing import Mapping
from requests import (PreparedRequest, Response)
from requests.exceptions import (JSONDecodeError)
from json import (loads, dumps)
from jwt.utils import base64url_decode


def request_to_curl(
        request: PreparedRequest,
        hide_body_secrets: Mapping[str, str] = dict()
      ) -> str:
    lines = []
    lines.append(f'curl -X {request.method} "{request.url}"')

    relevant_headers = {k: v for k, v in request.headers.items() if k in ["Authorization", "Content-Type"] or k.startswith("X-")}
    for key, value in relevant_headers.items():
        lines.append(f'-H "{key}: {request.headers[key]}"')

    if request.body is not None and request.headers.get("Content-Type", "").startswith("application/json"):
        body = loads(request.body.decode("utf-8"))
        body = body | hide_body_secrets
        lines.append(f"-d @- << EOF\n{dumps(body, indent=2)}\nEOF")
    elif request.body is not None:
        lines.append(f"-d @- << EOF\n{request.body}\nEOF")
    return " \\\n    ".join(lines)


def response_to_text(
        response: Response,
        hide_body_secrets: Mapping[str, str] = dict()
      ) -> str:
    """Converts the response to human readable text"""
    str = f"{response.status_code}"
    try:
        str = str + "\n" + dumps(response.json(), indent=2)
    except JSONDecodeError:
        str = str + "\n" + response.raw.read().decode("utf-8")

    return str


def jwt_to_text(token: str) -> str:
    (header, payload, signature) = map(lambda data: base64url_decode(data), token.split("."))

    header = loads(header.decode("utf-8"))
    payload = loads(payload.decode("utf-8"))

    return dumps(header, indent=4) + "\n" + dumps(payload, indent=4)
