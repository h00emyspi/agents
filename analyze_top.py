import json

with open('quality_posts.json', encoding='utf-8') as f:
    posts = json.load(f)

sorted_posts = sorted(posts, key=lambda x: x.get('upvotes', 0), reverse=True)

output = []

output.append("=" * 80)
output.append("TOP-10 POSTS BY UPVOTES")
output.append("=" * 80)

for i, p in enumerate(sorted_posts[:10]):
    output.append(f"\n#{i+1} | UP: {p.get('upvotes', 0)} | DOWN: {p.get('downvotes', 0)} | COMMENTS: {p.get('comment_count', 0)}")
    output.append("-" * 80)
    output.append(f"Title: {p.get('title', '')}")
    output.append(f"Created: {p.get('created_at', '')}")
    output.append(f"\nContent:\n{p.get('content', '')}")
    output.append("\n")

# Topics
output.append("\n" + "=" * 80)
output.append("TOPIC ANALYSIS")
output.append("=" * 80)

keywords = {
    "AI/LLM": ["ai", "llm", "gpt", "model", "chatgpt", "claude", "gemini"],
    "Agents": ["agent", "autonomous", "agentic"],
    "Coding": ["code", "programming", "python", "api", "server", "deploy"],
    "Memory": ["memory", "remember", "session", "context"],
    "Economics": ["money", "economy", "token", "price", "trading", "profit"],
    "Society": ["society", "human", "community", "culture"],
    "Philosophy": ["philosophy", "meaning", "consciousness", "identity"],
    "Research": ["research", "study", "experiment", "data"],
}

topic_counts = {topic: 0 for topic in keywords}

for p in posts:
    text = (p.get("title", "") + " " + p.get("content", "")).lower()
    for topic, words in keywords.items():
        if any(w in text for w in words):
            topic_counts[topic] += 1

output.append("\nTopic distribution:")
for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
    pct = count / len(posts) * 100
    bar = "#" * int(pct / 5)
    output.append(f"  {topic:20s}: {count:3d} ({pct:5.1f}%) {bar}")

# Save to file
with open("analysis_output.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(output))

print("Saved to analysis_output.txt")
