import aiohttp
import asyncio
import random
import string
import time 
import traceback
import user 

async def simulate_variable_load(requests_per_sec_func, total_time):
    start_time = time.time()
    elapsed = 0
    tasks = []
    while elapsed < total_time:
        elapsed = time.time() - start_time
        payload  = ''.join(random.choices(string.ascii_letters, k=10))

        async def async_wrapper():
            try: 
                res = await user.typical_call_chain(elapsed, payload)
                return res
            except Exception:
                return "user was dissapointed: " + traceback.format_exc()

        tasks.append(asyncio.create_task(async_wrapper()))

        # this is ok if the change in requests/sec is slowish
        f = requests_per_sec_func(elapsed/total_time)
        await asyncio.sleep(1/f)

    results = await asyncio.gather(*tasks)

    errors = [e for e in results if isinstance(e, str)]
    latencies = [e for e in results if isinstance(e, (int, float))]
    return (latencies, errors)
