"""FLUX.1-schnell via the free Hugging Face Space (ZeroGPU quota of the account whose read token the
environment proxy injects into the Authorization header for the space host).
usage: python3 tools/concept_gen/flux.py <outfile.png> <seed> <prompt> [width height]
Note: gradio_client moves 'authorization' into 'x-hf-authorization' at construction; we set it after
construction so it stays 'Authorization' and the proxy can substitute the saved token."""
import shutil, sys, time
from gradio_client import Client
from PIL import Image
out, seed, prompt = sys.argv[1], int(sys.argv[2]), sys.argv[3]
w, h = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (1024, 1024)
c = Client("https://black-forest-labs-flux-1-schnell.hf.space/", verbose=False)
c.headers["authorization"] = "Bearer proxy-injected"
c.headers.pop("x-hf-authorization", None)
t = time.time()
res = c.predict(prompt=prompt, seed=seed, randomize_seed=False, width=w, height=h, num_inference_steps=4, api_name="/infer")
p = res[0] if isinstance(res, (list, tuple)) else res
p = p if isinstance(p, str) else p.get("path")
Image.open(p).convert("RGB").save(out)
print(out, round(time.time() - t), "s")
