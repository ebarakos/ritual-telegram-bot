# Creating an infernet-compatible `telegram` container

In this tutorial, we'll create a simple telegram bot container that can be used
with infernet.

> [!NOTE]
> This directory `containers/telegram` already includes the final result
> of this tutorial. Run the following tutorial in a new directory.

Let's get started! 🎉

## Step 1: create a simple flask-app and a requirements.txt file

First, we'll create a simple flask-app that returns a telegram message.
We begin by creating a `src` directory:

```
mkdir src
```

Inside `src`, we create a `app.py` file with the following content:

```python

def create_app() -> Quart:
    app = Quart(__name__)
    bot = telegram.Bot(TELEGRAM_TOKEN)

    @app.route("/")
    def index() -> str:
        """
        Utility endpoint to check if the service is running.
        """
        return "Telegram Bot Solidity"

    @app.route("/new_message", methods=["POST"])
    async def new_message() -> dict[str, Any]:
        req_data = await request.get_json()
        message = req_data.get("message")

        sub = Subscription(
            owner="0x13D69Cf7d6CE4218F646B759Dcf334D82c023d8e",
            active_at=0,
            period=0,
            frequency=1,
            redundancy=1,
            containers=["telegram"],
            lazy=False,
            verifier=ZERO_ADDRESS,
            payment_amount=0,
            payment_token=ZERO_ADDRESS,
            wallet=ZERO_ADDRESS,
        )

        client = NodeClient("http://172.17.0.1:4000")
        nonce = random.randint(0, 2**32 - 1)
        await client.request_delegated_subscription(
            subscription=sub,
            rpc=RPC("http://172.17.0.1:8545"),
            coordinator_address="0x2E983A1Ba5e8b38AAAeC4B440B9dDcFBf72E15d1",
            expiry=int(time() + 10),
            nonce=nonce,
            private_key="0x5de4111afa1a4b94908f83103eb1f1706367c2e68ca870fc3fb9a804cdab365a",
            data={ "message" : "Delegated subscription message: " + message },
        )

        return {"status": "ok"}

    @app.route("/service_output", methods=["POST"])
    async def service_output() -> dict[str, Any]:
        req_data = await request.get_json()
        """
        InfernetInput has the format:
            source: (0 on-chain, 1 off-chain)
            data: dict[str, Any]
        """
        infernet_input: InfernetInput = InfernetInput(**req_data)

        match infernet_input:
            case InfernetInput(source=JobLocation.OFFCHAIN):
                message = cast(dict[str, Any], infernet_input.data).get("message")
            case InfernetInput(source=JobLocation.ONCHAIN):
                # On-chain requests are sent as a generalized hex-string which we will
                # decode to the appropriate format.
                bytes_data = bytes.fromhex(infernet_input.data)
                message = bytes_data.decode('utf-8')
            case _:
                raise ValueError("Invalid source")
        log.info("message: %s", message)

        async with bot:
            await bot.send_message(text=message, chat_id=CHAT_ID)
        return {"output": f"Your Telegram message was: {message}"}
    return app

if __name__ == "__main__":
    """
    Utility to run the app locally. For development purposes only.
    """
    create_app().run(port=3000)

```

As you can see, the app has 3 endpoints: `/`, `/service_output` and `/new_message`. The first
one is simply used to ping the service, the second one is used for infernet and the 3rd one is using by another Telegram bot polling service.

We'll create a `requirements.txt`
file with the following content:

```
python-telegram-bot===21.3
quart==0.19.4
infernet-ml==1.0.0
web3==6.15.0
tqdm==4.66.3
infernet-client===1.0.0
```

## Step 2: create a Dockerfile

Next, we'll create a Dockerfile that builds the flask-app and runs it.
At the top-level directory, create a `Dockerfile` with the following content:

```dockerfile
FROM python:3.11-slim as builder

WORKDIR /app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PIP_NO_CACHE_DIR 1
ENV RUNTIME docker
ENV PYTHONPATH src
ARG index_url
ENV UV_EXTRA_INDEX_URL ${index_url}

RUN apt-get update
RUN apt-get install -y git curl

# install uv
ADD https://astral.sh/uv/install.sh /install.sh
RUN chmod 755 /install.sh
RUN /install.sh && rm /install.sh

COPY src/requirements.txt .

RUN /root/.cargo/bin/uv pip install --system --no-cache -r requirements.txt

COPY src src

ARG appname
ARG port
ENV APP_NAME=${appname}
ENV PORT=${port}
EXPOSE ${port}
RUN echo '#!/bin/sh\nexec hypercorn "${APP_NAME}:create_app()" -b "0.0.0.0:${PORT}"' > /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]
```

This is a simple Dockerfile that:

1. Uses the `python:3.11-slim` image as a base image
2. Installs the requirements
3. Copies the source code
4. Runs the app on port `3000` and the telegram polling service on `3001`

> [!IMPORTANT]
> App must be exposed on port `3000`. Infernet's orchestrator
> will always assume that the container apps are exposed on that port within the container.
> Users can then remap this port to any port that they want on the host machine
> using the `port` parameter in the container specs.

By now, your project directory should look like this:

```
.
├── Dockerfile
├── README.md
└── src
    ├── __init__.py
    └── app.py
    └── telegram_polling.py
    └── requirements.txt
```

## Step 3: build and run the containers

Now, we can build and run the containers. At the top-level directory, run:

```
make run
```

## Step 4: ping the container

In another terminal, run:

```
curl "localhost:3000"
```

It should return something like:

```
Telegram Bot
```

Congratulations! You've created a simple telegram bot container that can be
used with infernet. 🎉

## Step 5: request a service output

Now, let's request a service output. Note that this endpoint is called by
the infernet node, not by the user. For debugging purposes however, it's useful to
be able to call it manually.

In your terminal, run:

```
curl -X POST -H "Content-Type: application/json" -d '{"message": "Off-chain message"}' localhost:3000/service_output
```

The output should be something like:

```
{"output": "Hello your telegram message was: {'input': 'hello'}"}
```

Your users will never call this endpoint directly. Instead, they will:

1. Either [create an off-chain job request](../telegram#L36) through the node API
2. Or they will make a subscription on their contracts
