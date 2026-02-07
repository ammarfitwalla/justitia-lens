import httpx
import asyncio
import traceback

async def test_upload():
    # Create a dummy file
    with open("test_upload.txt", "w") as f:
        f.write("This is a test file for upload debugging.")

    base_url = "http://localhost:8000"
    
    # 1. First list cases to find a valid ID
    async with httpx.AsyncClient() as client:
        try:
            print(f"Listing cases from {base_url}/api/v1/cases...")
            resp = await client.get(f"{base_url}/api/v1/cases")
            if resp.status_code != 200:
                print(f"Failed to list cases: {resp.status_code} - {resp.text}")
                return
            
            cases = resp.json()
            if not cases:
                print("No cases found!")
                return
                
            case_id = cases[0]['id']
            print(f"Using Case ID: {case_id}")
            
            # Upload file
            upload_url = f"{base_url}/api/v1/upload/evidence/{case_id}"
            print(f"Uploading to {upload_url}...")
            
            # Use tuple for file upload: (filename, file_content, content_type)
            with open("test_upload.txt", "rb") as f:
                content = f.read()
                
            files = {'file': ('test_upload.txt', content, 'text/plain')}
            
            async with httpx.AsyncClient(timeout=60.0) as uploader:
                response = await uploader.post(upload_url, files=files)
                print(f"Status Code: {response.status_code}")
                print(f"Response: {response.text}")
            
        except Exception as e:
            print("Error occurred:")
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_upload())
