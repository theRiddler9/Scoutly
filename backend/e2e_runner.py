import httpx
import time
import json
import sys

API_URL = "http://localhost:8000/api"

def run_e2e():
    print("Starting Scoutly E2E Test Pipeline...\n")
    
    with httpx.Client(timeout=120.0) as client:
        # 1. Clear Database
        print("1. Clearing all existing opportunities...")
        r = client.delete(f"{API_URL}/opportunities/clear")
        if r.status_code != 200:
            print("Failed to clear database!")
            sys.exit(1)
        print("Database cleared.")

        # 2. Create Profile
        print("\n2. Creating robust test profile...")
        profile_data = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "github_url": "https://github.com/janedoe",
            "skills": ["React", "Python", "Machine Learning", "TypeScript", "TailwindCSS"],
            "projects": [
                {
                    "title": "AI Image Generator",
                    "description": "A web app that generates high quality images using stable diffusion.",
                    "tech_stack": "React, Python, FastAPI"
                },
                {
                    "title": "Smart Crypto Bot",
                    "description": "An automated trading bot leveraging LLMs to analyze market sentiment.",
                    "tech_stack": "Python, Pandas, Groq"
                }
            ],
            "resume_text": "I am a full stack AI engineer with a passion for participating in competitive hackathons.",
            "social_handles": {
                "twitter": "https://twitter.com/janedoe",
                "linkedin": "https://linkedin.com/in/janedoe",
                "website": ""
            }
        }
        r = client.post(f"{API_URL}/profile", json=profile_data)
        if r.status_code != 200:
            print(f"Failed to create profile! {r.text}")
            sys.exit(1)
        print("Profile created/updated successfully.")

        # 3. Run Discovery
        print("\n3. Triggering Discovery Engine (this will take 20-40 seconds)...")
        start = time.time()
        r = client.post(f"{API_URL}/discovery/run", json={})
        if r.status_code != 200:
            print(f"Discovery failed! {r.text}")
            sys.exit(1)
        
        data = r.json()
        print(f"Discovery completed in {time.time() - start:.1f}s!")
        print(f"   New Opportunities Found: {data.get('new_opportunities')}")
        
        # 4. Trigger Matching
        print("\n4. Triggering AI Matching...")
        r = client.post(f"{API_URL}/opportunities/match", json={"profile_id": 1})
        if r.status_code != 200:
            print(f"Matching failed! {r.text}")
            sys.exit(1)
        
        match_data = r.json()
        print(f"Matching completed! Matched {match_data.get('matched')} opportunities.")

        # 5. Fetch Top Opportunity
        print("\n5. Fetching top matching opportunity...")
        r = client.get(f"{API_URL}/opportunities?sort_by=score&limit=5")
        opps = r.json().get("opportunities", [])
        
        if not opps:
            print("No opportunities returned!")
            sys.exit(1)
        
        top_opp = opps[0]
        print(f"Top Match: {top_opp['name']} (Score: {top_opp['match_score']})")

        # 6. Auto-Fill Application
        print("\n6. Triggering Auto-Fill Agent for top match (this takes 10-30s)...")
        start = time.time()
        r = client.post(f"{API_URL}/applications/fill", json={
            "opportunity_id": top_opp["id"],
            "profile_id": 1
        })
        if r.status_code != 200:
            print(f"Auto-Fill failed! {r.text}")
            sys.exit(1)
            
        app_data = r.json()
        print(f"Auto-Fill completed in {time.time() - start:.1f}s!")
        print(f"   Application Status: {app_data.get('status')}")
        print(f"   Screenshot Path: {app_data.get('screenshot_path')}")

        print("\nALL E2E TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_e2e()
