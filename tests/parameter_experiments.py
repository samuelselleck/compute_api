import asyncio
import pickle
import subprocess
import os

import matplotlib.pyplot as plt

import load_patterns
import kubernetes_utils
import minikube_context



async def main():
    test_durations = 60*30
    loads = {
        "Ramping": lambda t: 0.1 + 0.9 * t,
        "Spike": lambda t: 1.1 - t**(1/8),
        "Ramp Steady": lambda t: min(1.8*t + 0.1, 1)
    }
    configurations = {
        "Defaultlike": "simple_defaultlike_config",
        "Fast Up Slow Down": "fast_up_slow_down",
        "Slow Up Slow Down": "slow_up_slow_down",
    }

    for (l_name, l) in loads.items():
        for (c_name, c) in configurations.items():
            l_name_snake = l_name.replace(" ", "_").lower()
            c_name_snake = c_name.replace(" ", "_").lower()
            cache = f"experiment_outputs/{l_name_snake}-{c_name_snake}-{test_durations}.pkl"
            if not os.path.exists(cache):
                async with minikube_context.Env():
                    scale_variant = f"autoscale_variants/{c}.yaml"
                    subprocess.call(["kubectl", "apply", "-f", scale_variant, "-n", "model"])
                    await asyncio.sleep(1)
                    [load_results, scaling] = await asyncio.gather(
                        load_patterns.simulate_variable_load(l, test_durations),
                        kubernetes_utils.replicas_over_duration(
                            "model",
                            "celery-worker",
                            test_durations,
                            30
                        )
                    )
                    with open(cache, "wb") as f:
                        pickle.dump({
                            "load name": l_name,
                            "config name": c_name,
                            "load results": load_results,
                            "scaling": scaling,
                        }, f)
                


    fig1, axs1 = plt.subplots(len(configurations), len(loads))
    fig2, axs2 = plt.subplots(len(configurations), len(loads), sharex=True, sharey=True)
    for (i,(l_name, l)) in enumerate(loads.items()):
        for (j,(c_name, c)) in enumerate(configurations.items()):
            l_name_snake = l_name.replace(" ", "_").lower()
            c_name_snake = c_name.replace(" ", "_").lower()
            cache = f"experiment_outputs/{l_name_snake}-{c_name_snake}-{test_durations}.pkl"

            with open(cache, "rb") as f:
                res = pickle.load(f)
                latencies, errors = res["load results"]
                print(f"users experiencing errors in load \"{l_name}\" config \"{c_name}\": {len(errors)}")
                latency_hist(axs1[i, j], latencies)
                replica_changes(axs2[i, j], *res["scaling"])
                if i == 0:
                    axs1[i, j].set_title(c_name)
                    axs2[i, j].set_title(c_name)
                if j == 0:
                    axs1[i, j].set_ylabel(l_name)
                    axs2[i, j].set_ylabel(l_name)
    plt.show()
            


def latency_hist(axs, latencies):
	axs.hist(latencies, bins=20, color='skyblue', edgecolor='black')

def replica_changes(axs, timestamps, replica_counts):
    axs.plot(timestamps, replica_counts)
          
    
if __name__ == "__main__":
    asyncio.run(main())


