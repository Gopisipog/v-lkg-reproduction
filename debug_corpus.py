"""Extract most frequent meaningful terms from the corpus."""
import json, re
from collections import Counter

with open("data/processed/corpus.json", "r", encoding="utf-8") as f:
    corpus = json.load(f)

# concatenate all transcripts
full = " ".join(s.get("transcript", "") for s in corpus)
full_lower = full.lower()

# word frequency (skip short/stop words)
stop = {"the","a","an","and","or","but","in","on","at","to","for","of","with",
        "by","from","is","it","that","this","was","are","be","has","had","have",
        "will","can","do","does","did","not","so","if","as","we","you","they",
        "he","she","my","your","our","their","what","how","when","why","which",
        "who","there","just","about","all","also","than","some","more","very",
        "no","yes","right","like","know","think","going","one","two","make",
        "people","say","said","got","get","would","could","should","really",
        "thing","things","way","time","come","back","let","much","even","well",
        "first","last","new","now","here","into","over","only","other","than",
        "them","then","these","those","its","been","being","because","through",
        "during","before","after","between","where","under","every","own","same",
        "tell","told","ask","asked","look","see","want","need","try","start",
        "good","great","big","little","long","high","old","different","important",
        "most","many","often","still","while","however","another","another",
        "point","actually","something","going","take","come","may","might",
        "around","lot","off","down","up","out","in","isn","don","doesn",
        "won","didn","wouldn","couldn","shouldn","aren","isn","wasn","weren",
        "haven","hasn","hadn","let","make","made","know","think","going"}

words = re.findall(r"[a-z]+(?:[-'][a-z]+)*", full_lower)
# filter stop words and short words
filtered = [w for w in words if w not in stop and len(w) > 3]
freq = Counter(filtered)
print("Top 80 meaningful words:")
for word, count in freq.most_common(80):
    print(f"  {word}: {count}")

# Now look for bigrams (two-word phrases)
bigram_counter = Counter()
tokens = [w for w in words if w not in stop and len(w) > 2]
for i in range(len(tokens) - 1):
    bg = tokens[i] + " " + tokens[i+1]
    bigram_counter[bg] += 1
print("\nTop 40 bigrams:")
for bg, count in bigram_counter.most_common(40):
    if count >= 3:
        print(f"  {bg}: {count}")

# trigrams
trigram_counter = Counter()
for i in range(len(tokens) - 2):
    tg = tokens[i] + " " + tokens[i+1] + " " + tokens[i+2]
    trigram_counter[tg] += 1
print("\nTop 20 trigrams (count >= 3):")
for tg, count in trigram_counter.most_common(20):
    if count >= 3:
        print(f"  {tg}: {count}")
