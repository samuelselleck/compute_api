import uuid
import time


class Model:
    def __init__(self):
        time.sleep(self.setup_time())
        self.uuid = str(uuid.uuid4())

    def predict(self, input: str):
        time.sleep(self.predict_time())
        output = f"""\
		model inference on instance {self.uuid}\
		with input {input} was successfull!
		"""
        return {"output": output, "input": input}

    def setup_time(self):
        return 30

    def predict_time(self):
        return 5
