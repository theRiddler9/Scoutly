import asyncio
from app.services.discovery import run_discovery

async def main():
    result = await run_discovery()
    print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())
