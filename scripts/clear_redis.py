import os
from pathlib import Path

import redis
from dotenv import load_dotenv

# Load env variables
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def clear_redis():
    print("🧹 connecting to Redis...")
    try:
        redis_url = os.getenv("REDIS_URL")

        if redis_url:
            r = redis.from_url(redis_url, decode_responses=True)
            # Mask URL for printing
            safe_host = redis_url.split("@")[-1] if "@" in redis_url else redis_url
            print(f"✅ Connected to {safe_host}")
        else:
            host = os.getenv("REDIS_HOST", "localhost")
            port = int(os.getenv("REDIS_PORT", 6379))
            username = os.getenv("REDIS_USERNAME", None)
            password = os.getenv("REDIS_PASSWORD", None)

            kwargs = {"host": host, "port": port, "decode_responses": True}

            if username:
                kwargs["username"] = username
            if password:
                kwargs["password"] = password

            r = redis.Redis(**kwargs)
            print(f"✅ Connected to {host}:{port}")

        r.ping()

        print("🗑️  Flushing all keys...")
        r.flushall()
        print("✨ Redis database cleared! Memory should be free now.")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    clear_redis()
