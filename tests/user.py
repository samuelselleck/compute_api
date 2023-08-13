
import aiohttp
import asyncio

STATUS_REQUEST_RATE = 3.0 
MAX_STATUS_REQ = 60

async def _make_request(session, url, type="get"):
    method = getattr(session, type)
    async with method(url) as response:
        return await response.json()

async def typical_call_chain(identifier, payload):
    push_url = f"http://localhost:8002/push?input={payload}"

    async with aiohttp.ClientSession() as session:
        push_response = await _make_request(session, push_url, "post")
        print(f"{identifier}: Pushed payload {payload} response: {push_response}")

        status_response = {"status": "never_run"}
        count = 0
        while status_response["status"] != "finished":
            count += 1
            if count > MAX_STATUS_REQ:
                raise TimeoutError("user got impatient")

            await asyncio.sleep(STATUS_REQUEST_RATE)

            status_url = f"http://localhost:8002/status/{push_response['id']}"
            status_response = await _make_request(session, status_url)
            print(f"{identifier}: Status response {count}: {status_response}")

        data_url = f"http://localhost:8002/data/{push_response['id']}"
        data_response = await _make_request(session, data_url)
        print(f"{identifier}: Data returned: {data_response}")
        print(f"{identifier}: client satisfied, exiting")

    return data_response["latency"]

