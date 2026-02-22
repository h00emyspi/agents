import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from llm.generator import LLMGenerator

async def test():
    gen = LLMGenerator()
    print('Generator ready - testing Ollama...')
    
    title, content = await gen.generate_post('AI agents')
    
    with open('ollama_test_output.txt', 'w', encoding='utf-8') as f:
        f.write(f'Title: {title}\n')
        f.write(f'Content: {content}\n')
    
    print('Done - see ollama_test_output.txt')

asyncio.run(test())
