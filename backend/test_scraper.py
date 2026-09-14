import httpx, time, json, os
from dotenv import load_dotenv
import asyncio

load_dotenv()
api_key = os.getenv("ANAKIN_API_KEY")

HEADERS = {"X-API-Key": api_key, "Content-Type": "application/json"}
payload = {
  "url": "https://devpost.com/hackathons?status[]=upcoming&status[]=open",
  "country": "us",
  "formats": [
    "markdown",
    "cleanedHtml"
  ]
}

async def main():
    print("Starting Anakin scrape job...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post("https://api.anakin.io/v1/url-scraper", headers=HEADERS, json=payload, timeout=10)
            print("Submit response:", resp.status_code, resp.text)
            
            if resp.status_code in (200, 202):
                job = resp.json()
                job_id = job.get("jobId")
                if job_id:
                    print("Job ID:", job_id)
                    for i in range(10):
                        poll_resp = await client.get(f"https://api.anakin.io/v1/url-scraper/{job_id}", headers=HEADERS, timeout=10)
                        result = poll_resp.json()
                        print(f"Poll {i} status:", result.get("status"))
                        if result.get("status") in ("completed", "failed"):
                            if result.get("status") == "completed":
                                print("Keys:", result.keys())
                                print("Markdown len:", len(result.get("markdown", "")))
                                print("CleanedHtml len:", len(result.get("cleanedHtml", "")))
                            break
                        await asyncio.sleep(2)
                else:
                    print("No job ID found in response")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
