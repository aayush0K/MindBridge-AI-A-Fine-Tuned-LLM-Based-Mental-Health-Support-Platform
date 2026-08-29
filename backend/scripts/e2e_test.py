import asyncio
import httpx
import uuid

API_BASE = "http://localhost:8000/api/v1"

async def run_e2e_test():
    print("Starting End-to-End API Test")
    
    unique_id = str(uuid.uuid4())[:8]
    email = f"testuser_{unique_id}@example.com"
    password = "securepassword123"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Register
        print(f"1. Registering user {email}...")
        res = await client.post(f"{API_BASE}/auth/register", json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        })
        if res.status_code != 201:
            print(f"ERROR: Registration failed: {res.text}")
            return
        
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("SUCCESS: Registered successfully.")
        
        # 2. Check /users/me
        print("2. Checking /users/me...")
        res = await client.get(f"{API_BASE}/users/me", headers=headers)
        if res.status_code != 200:
            print(f"ERROR: User fetch failed: {res.text}")
            return
        print("SUCCESS: User fetch successful.")
        
        # 3. Log a mood
        print("3. Logging mood...")
        res = await client.post(f"{API_BASE}/mood/log", headers=headers, json={
            "mood_score": 7,
            "mood_label": "calm",
            "notes": "Testing mood log"
        })
        if res.status_code != 201 and res.status_code != 200:
            print(f"ERROR: Mood log failed: {res.text}")
            return
        print("SUCCESS: Mood logged successfully.")
        
        # 4. Fetch mood stats
        print("4. Fetching mood stats...")
        res = await client.get(f"{API_BASE}/mood/stats", headers=headers)
        if res.status_code != 200:
            print(f"ERROR: Mood stats failed: {res.text}")
            return
        print(f"SUCCESS: Mood stats fetched: {res.json()}")
        
        # 5. Start Chat Session & Send Message
        print("5. Testing chat pipeline...")
        res = await client.post(f"{API_BASE}/chat/message", headers=headers, json={
            "message": "I'm feeling really anxious about my upcoming exams.",
            "session_id": None
        })
        if res.status_code != 200:
            print(f"ERROR: Chat failed: {res.text}")
            return
        
        chat_data = res.json()
        session_id = chat_data["session_id"]
        print(f"SUCCESS: Chat response received. Relevance: {chat_data['relevance_score']:.2f}")
        print(f"AI: {chat_data['response'][:100]}...")
        
        # 6. Send short conversational message (should bypass relevance check!)
        print("6. Testing short conversational bypass...")
        res = await client.post(f"{API_BASE}/chat/message", headers=headers, json={
            "message": "That helps, thank you.",
            "session_id": session_id
        })
        if res.status_code != 200:
            print(f"ERROR: Chat bypass failed: {res.text}")
            return
            
        chat_data2 = res.json()
        print(f"SUCCESS: Short message response received. Relevance: {chat_data2['relevance_score']:.2f}")
        print(f"AI: {chat_data2['response'][:100]}...")

        print("\nALL TESTS PASSED! System is 100% operational.")

if __name__ == "__main__":
    asyncio.run(run_e2e_test())
