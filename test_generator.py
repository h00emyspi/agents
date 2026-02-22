import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

import asyncio
from src.llm.generator import LLMGenerator


async def test_generator():
    gen = LLMGenerator()
    
    output = []
    output.append("=" * 60)
    output.append("TEST GENERATOR")
    output.append("=" * 60)
    
    output.append("\nTopics:")
    topics = gen.training_data.get_topics()
    for i, topic in enumerate(topics):
        output.append(f"  {i+1}. {topic}")
    
    output.append("\n" + "=" * 60)
    output.append("POST GENERATION")
    output.append("=" * 60)
    
    for i in range(3):
        output.append(f"\n--- Post {i+1} ---")
        title, content = await gen.generate_post()
        output.append(f"Title: {title}")
        output.append(f"Content: {content[:200]}...")
    
    output.append("\n" + "=" * 60)
    output.append("COMMENT GENERATION")
    output.append("=" * 60)
    
    comment = await gen.generate_comment("I think AI agents should have memory")
    output.append(f"Comment: {comment}")
    
    result = "\n".join(output)
    
    with open("generator_test_output.txt", "w", encoding="utf-8") as f:
        f.write(result)
    
    print("Done. See generator_test_output.txt")


if __name__ == "__main__":
    asyncio.run(test_generator())
