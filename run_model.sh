#!bin/bash

# Currently using the 7B model
# can also try 1.5B if it's not good
# or try 32 B (seems very promising)

vllm serve deepseek-ai/DeepSeek-R1-Distill-Qwen-7B --tensor-parallel-size 2 --max-model-len 32768 --enforce-eager
