import asyncio
import subprocess

class Env():
	async def __aenter__(self):
		subprocess.call(["minikube", "delete"])
		subprocess.call(["minikube", "start"])
		subprocess.call(["./setup_cluster.sh"], cwd="..")
		self.tunnel = await asyncio.create_subprocess_exec("minikube", "tunnel")
		await asyncio.sleep(5)

	async def __aexit__(self, exc_type, exc, tb):
		self.tunnel.terminate()
		await self.tunnel.wait()
