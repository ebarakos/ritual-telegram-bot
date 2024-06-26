from time import sleep
from typing import Any

import requests


def hit_server_directly() -> None:
    print("hello")
    r = requests.get("http://localhost:3000/")
    print(r.status_code)
    # server response
    print("server response", r.text)


def poll_until_complete(id: str) -> Any:
    status = "running"
    r = None
    while status == "running":
        r = requests.get(
            "http://localhost:4000/api/jobs",
            params={
                "id": id,
            },
        ).json()[0]
        status = r.get("status")
        print("status", status)
        if status != "running":
            break
        sleep(1)
    return r


def create_job_through_node() -> None:
    r = requests.post(
        "http://localhost:4000/api/jobs",
        json={
            "containers": ["telegram"],
            "data": {"some": "object"},
        },
    )

    job_id = r.json().get("id")

    result = poll_until_complete(job_id)
    print("result", result)


if __name__ == "__main__":
    create_job_through_node()
