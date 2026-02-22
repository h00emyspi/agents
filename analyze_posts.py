import json

data = json.load(open('moltbook_posts_raw.json', encoding='utf-8'))

# Фильтруем не-crypto посты
non_crypto = [p for p in data if not p.get('is_crypto')]
print(f'Не-крипто постов: {len(non_crypto)}')

# Покажем их
for p in non_crypto[:10]:
    print(f"\n=== {p['title'][:60]} ===")
    print(f"Content: {p['content'][:150]}...")
