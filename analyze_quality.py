import json

with open('quality_posts.json', encoding='utf-8') as f:
    posts = json.load(f)

print(f'Quality posts: {len(posts)}')

# Stats
upvotes = sum(p.get('upvotes', 0) for p in posts)
downvotes = sum(p.get('downvotes', 0) for p in posts)
comments = sum(p.get('comment_count', 0) for p in posts)

print(f'Total upvotes: {upvotes}')
print(f'Total downvotes: {downvotes}')
print(f'Total comments: {comments}')

# Top posts
print('\nTOP-5 POSTS:')
sorted_posts = sorted(posts, key=lambda x: x.get('upvotes', 0), reverse=True)
for i, p in enumerate(sorted_posts[:5]):
    title = p['title'][:60]
    up = p.get('upvotes', 0)
    down = p.get('downvotes', 0)
    comm = p.get('comment_count', 0)
    print(f"{i+1}. {title}... | up:{up} down:{down} comm:{comm}")
