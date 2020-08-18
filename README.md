# SCIST-BOT

## Installation

```bash
pip3 install -r requirements.txt
```

## Settings

Write following in your `.bashrc` file, suggest use `127.0.0.1` for host and `27017` for port.

```bash
export SCIST_DB_NAME=<NAME>
export SCIST_DB_HOST=<HOST>
export SCIST_DB_PORT=<PORT>
export SCIST_DB_USER=<USER>
export SCIST_DB_PASSWORD=<PASSWORD>
```

## Run

Run mongoDB by docker-compose

```bash
docker-compose up -d
```

Insert seed to mongodb, or it will auto insert when startup.

```bash
python3 seed.py
```
