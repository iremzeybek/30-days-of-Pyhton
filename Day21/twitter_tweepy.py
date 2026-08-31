import tweepy
import pandas as pd
from datetime import datetime

# =========================================================
# TWITTER API CONFIGURATION
# =========================================================

# Replace with your own Bearer Token
BEARER_TOKEN = "YOUR_BEARER_TOKEN_HERE"

# =========================================================
# SEARCH SETTINGS
# =========================================================

SEARCH_QUERY = "python lang:en -is:retweet"
MAX_RESULTS = 20
CSV_FILE = "tweets_output.csv"

# =========================================================
# CREATE CLIENT
# =========================================================

client = tweepy.Client(bearer_token=BEARER_TOKEN)

# =========================================================
# FETCH TWEETS
# =========================================================


def fetch_tweets(query, max_results=20):
    print(f"Searching tweets for: {query}\\n")

    response = client.search_recent_tweets(
        query=query,
        max_results=max_results,
        tweet_fields=[
            "created_at",
            "public_metrics",
            "author_id",
            "lang"
        ]
    )

    tweets = response.data

    if not tweets:
        print("No tweets found.")
        return []

    tweet_data = []

    for tweet in tweets:
        metrics = tweet.public_metrics

        tweet_data.append({
            "tweet_id": tweet.id,
            "author_id": tweet.author_id,
            "text": tweet.text.replace("\\n", " "),
            "created_at": tweet.created_at,
            "likes": metrics["like_count"],
            "retweets": metrics["retweet_count"],
            "replies": metrics["reply_count"],
            "quotes": metrics["quote_count"],
            "language": tweet.lang
        })

    return tweet_data


# =========================================================
# SAVE TO CSV
# =========================================================


def save_to_csv(data, filename):
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    print(f"Saved {len(df)} tweets to {filename}\\n")
    return df


# =========================================================
# ANALYZE TWEETS
# =========================================================


def analyze_tweets(df):
    print("========== TWEET ANALYSIS ==========")

    total_tweets = len(df)
    avg_likes = df["likes"].mean()
    avg_retweets = df["retweets"].mean()

    print(f"Total tweets: {total_tweets}")
    print(f"Average likes: {avg_likes:.2f}")
    print(f"Average retweets: {avg_retweets:.2f}")

    # Most liked tweet
    top_like_row = df.loc[df["likes"].idxmax()]

    print("\\nMost liked tweet:")
    print(f"Likes: {top_like_row['likes']}")
    print(f"Created: {top_like_row['created_at']}")
    print(f"Text: {top_like_row['text'][:150]}...")

    # Most retweeted tweet
    top_retweet_row = df.loc[df["retweets"].idxmax()]

    print("\\nMost retweeted tweet:")
    print(f"Retweets: {top_retweet_row['retweets']}")
    print(f"Created: {top_retweet_row['created_at']}")
    print(f"Text: {top_retweet_row['text'][:150]}...")

    # Top 5 by likes
    print("\\nTop 5 tweets by likes:")
    top5 = df.sort_values(by="likes", ascending=False).head(5)

    for i, (_, row) in enumerate(top5.iterrows(), start=1):
        print(f"{i}. {row['likes']} likes | {row['text'][:80]}...")

    print("====================================\\n")


# =========================================================
# DISPLAY TABLE
# =========================================================


def display_table(df):
    print("Tweet Summary Table:\\n")

    display_df = df[["likes", "retweets", "replies", "created_at", "text"]].copy()

    display_df["text"] = display_df["text"].str.slice(0, 60) + "..."

    print(display_df.to_string(index=False))


# =========================================================
# MAIN PROGRAM
# =========================================================


def main():
    print("Twitter API Practice with Tweepy")
    print("Started at:", datetime.now())
    print("-" * 50)

    try:
        tweets = fetch_tweets(SEARCH_QUERY, MAX_RESULTS)

        if not tweets:
            return

        df = save_to_csv(tweets, CSV_FILE)

        analyze_tweets(df)

        display_table(df)

        print("\\nProgram completed successfully.")

    except tweepy.TooManyRequests:
        print("Rate limit exceeded. Please wait and try again later.")

    except tweepy.Unauthorized:
        print("Authentication failed. Check your Bearer Token.")

    except Exception as e:
        print("Unexpected error:", e)


if __name__ == "__main__":
    main()
