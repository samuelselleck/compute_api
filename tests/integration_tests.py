import subprocess
import asyncio
import traceback

import user
import load_patterns
import kubernetes_utils
import minikube_context


async def simple_api_test():
    try:
        await user.typical_call_chain("api customer", "complicated task")
    except Exception:
        print_failed(traceback.print_exc())


async def calm_test():
    def req_freq(t): return 0.1
    (latencies, errors) = await load_patterns.simulate_variable_load(req_freq, 60)
    if len(errors) > 0:
        print_failed(errors)


async def spike_test():
    def req_freq(t): return 3
    (latencies, errors) = await load_patterns.simulate_variable_load(req_freq, 10)
    if len(errors) > 0:
        print_failed(errors)


async def longer_calm_test_with_faults():
    def req_freq(t): return 0.1
    ((latencies, errors), _) = await asyncio.gather(
        load_patterns.simulate_variable_load(req_freq, 60*5),
        kubernetes_utils.delete_random_pods(60*3, 30, "model", "celery-worker")
    )
    if len(errors) > 0:
        print_failed(errors)


def print_failed(message):
    print("FAILED TEST:", message)


async def main():
    tests = [simple_api_test, calm_test,
             spike_test, longer_calm_test_with_faults]
    for test in tests:
        async with minikube_context.Env():
            await test()

if __name__ == "__main__":
    asyncio.run(main())
