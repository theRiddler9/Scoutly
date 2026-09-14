import asyncio
from app.services.llm_client import llm_client

async def main():
    try:
        res = await llm_client.call("You are a helpful assistant", "Hello, who are you?", json_mode=False)
        print("Raw response:", res)
    except Exception as e:
        print("Exception:", e)

if __name__ == "__main__":
    asyncio.run(main())
