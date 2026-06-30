import os
import re
import pandas as pd
from bs4 import BeautifulSoup

# =====================================================
# CONFIG
# =====================================================

HTML_FOLDER = "canada_express_visa"
OUTPUT_FILE = "data/canada_express.csv"

os.makedirs("data", exist_ok=True)

posts = []

stats = {
    "pages": 0,
    "posts": 0,
    "missing_username": 0,
    "missing_timestamp": 0,
    "missing_postid": 0,
    "missing_text": 0,
    "quoted_posts": 0,
}

# =====================================================
# HELPERS
# =====================================================

def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_thread_info(soup):
    """
    Extract thread ID and title from the page.
    """
    thread_id = ""
    thread_title = ""

    canonical = soup.find(
        "link",
        rel="canonical"
    )

    if canonical:
        href = canonical.get("href", "")
        m = re.search(r"/(\d+)/", href)
        if m:
            thread_id = m.group(1)

    if soup.title:
        title = soup.title.get_text(strip=True)
        title = title.replace(" - Nairaland", "").strip()
        thread_title = title

    return thread_id, thread_title


def extract_post_id(header):
    """
    Finds <a name="msg124631281"></a> as the primary target.
    Falls back to trailing href fragments if missing.
    """
    msg_anchor = header.find("a", attrs={"name": re.compile(r"^msg\d+$")})
    if msg_anchor:
        return msg_anchor["name"].replace("msg", "")

    # Fallback to the href pattern just in case Nairaland changes markup
    anchor = header.find("a", href=re.compile(r"#\d+$"))
    if anchor:
        return anchor["href"].split("#")[-1]

    return ""


def extract_username(header):
    """
    Finds <a class="user" href="/username">
    """
    user = header.find("a", class_="user")

    if user:
        return (
            user.get_text(strip=True),
            user.get("href", "")
        )

    return "", ""


def extract_timestamp(header):
    meta = header.find(
        "meta",
        itemprop="datePublished"
    )

    if meta:
        return meta.get("content", "")

    span = header.find("span", class_="s")

    if span:
        return span.get_text(" ", strip=True)

    return ""


def extract_body(body):
    td = body.find("td")

    if td is None:
        return None

    div = td.find("div", class_="narrow")

    return div


# =====================================================
# PARSER
# =====================================================

files = sorted(
    f for f in os.listdir(HTML_FOLDER)
    if f.endswith(".html")
)

print(f"Found {len(files)} html files.\n")

for filename in files:

    stats["pages"] += 1

    print(f"Parsing {filename}...")

    filepath = os.path.join(
        HTML_FOLDER,
        filename
    )

    with open(
        filepath,
        encoding="utf-8",
        errors="ignore"
    ) as f:
        html = f.read()

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    # Extract thread-level metadata once per page
    thread_id, thread_title = extract_thread_info(soup)

    table = soup.find(
        "table",
        summary="posts"
    )

    if table is None:
        print("No posts table.\n")
        continue

    rows = table.find_all("tr")

    current_header = None

    for row in rows:

        header_td = row.find(
            "td",
            class_=lambda x: x and "bold" in x
        )

        if header_td:
            current_header = row
            continue

        if current_header is None:
            continue

        body_div = extract_body(row)

        if body_div is None:
            continue

        # =======================================
        # HEADER
        # =======================================

        username, profile = extract_username(
            current_header
        )

        timestamp = extract_timestamp(
            current_header
        )

        post_id = extract_post_id(
            current_header
        )

        # =======================================
        # BODY
        # =======================================

        raw_html = str(body_div)

        has_quote = False
        quoted_usernames = []

        # Find ALL blockquotes to cleanly strip out multi-quotes
        blockquotes = body_div.find_all("blockquote")

        if blockquotes:
            has_quote = True
            stats["quoted_posts"] += 1

            for quote in blockquotes:
                author = quote.find(["a", "b"])

                if author:
                    q_user = author.get_text(strip=True).replace(" said:", "").strip()
                    # Prevent duplicate usernames if they quote the same person twice
                    if q_user and q_user not in quoted_usernames:
                        quoted_usernames.append(q_user)

                # Decompose every quote to isolate pure response text
                quote.decompose()

        quoted_username_str = ", ".join(quoted_usernames)

        raw_text = body_div.get_text(
            " ",
            strip=True
        )

        clean = clean_text(raw_text)

        # =======================================
        # VALIDATION
        # =======================================

        # It is expected and correct that posts consisting entirely of quoted 
        # text will be dropped here, preserving the integrity of voice samples.
        if clean == "":
            stats["missing_text"] += 1
            continue

        if username == "":
            stats["missing_username"] += 1

        if timestamp == "":
            stats["missing_timestamp"] += 1

        if post_id == "":
            stats["missing_postid"] += 1

        # =======================================
        # EXTRA FEATURES & APPEND
        # =======================================

        links = body_div.find_all("a")
        images = body_div.find_all("img")

        word_count = len(clean.split())
        char_count = len(clean)

        stats["posts"] += 1

        posts.append({
            "thread_id": thread_id,
            "thread_title": thread_title,
            "post_id": post_id,
            "username": username,
            "profile_link": profile,
            "timestamp": timestamp,
            "raw_html": raw_html,
            "raw_text": raw_text,
            "clean_text": clean,
            "has_quote": has_quote,
            "quoted_username": quoted_username_str,
            "num_links": len(links),
            "num_images": len(images),
            "word_count": word_count,
            "char_count": char_count,
        })

# =====================================================
# SAVE
# =====================================================

df = pd.DataFrame(posts)

df.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print("\n==============================")
print("PARSER SUMMARY")
print("==============================")
print(f"Pages processed : {stats['pages']}")
print(f"Posts parsed    : {stats['posts']}")
print(f"Missing user    : {stats['missing_username']}")
print(f"Missing time    : {stats['missing_timestamp']}")
print(f"Missing post id : {stats['missing_postid']}")
print(f"Missing text    : {stats['missing_text']}")
print(f"Quoted posts    : {stats['quoted_posts']}")
print("==============================")
print(f"\nSaved to {OUTPUT_FILE}")