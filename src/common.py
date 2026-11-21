"""Shared loading / cleaning / feature helpers for all tasks."""
import glob, html, re
from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
REPORTS = ROOT / "reports"
MODELS = ROOT / "models"
for p in (REPORTS, MODELS):
    p.mkdir(exist_ok=True)

# Taxonomy: the CSV has no category column, so categories are derived from title keywords.
CATEGORY_RULES = [
    ("AI / Machine Learning", r"\b(ai|a\.i\.|artificial intelligence|machine learning|ml|llm|gpt|chatgpt|openai|nlp|deep learning|computer vision|chatbot|prompt)\b"),
    ("Data / Analytics", r"\b(data|analyst|analytics|dashboard|power ?bi|tableau|excel|sql|scraping|scraper|etl|looker)\b"),
    ("Mobile Apps", r"\b(mobile|android|ios|flutter|react native|swift|app developer|iphone)\b"),
    ("Web Development", r"\b(web ?developer|website|wordpress|shopify|wix|webflow|react|angular|vue|node|php|laravel|django|full[- ]?stack|front[- ]?end|back[- ]?end|html|css|web app|developer|squarespace|ecommerce|e-commerce|woocommerce)\b"),
    ("Software / DevOps", r"\b(software|python|java|c\+\+|\.net|api|devops|aws|cloud|blockchain|crypto|smart contract|web3|nft|automation|zapier|saas|backend|engineer|bot)\b"),
    ("Design / Creative", r"\b(design|designer|logo|graphic|ui|ux|figma|photoshop|illustrat\w*|branding|canva|3d|animation|packaging)\b"),
    ("Video / Audio", r"\b(video|editor|editing|youtube|tiktok|reels|podcast|audio|voice ?over|voiceover|music|motion|after effects|thumbnail)\b"),
    ("Writing / Content", r"\b(writer|writing|content|copywrit\w*|blog|article|ghostwrit\w*|editor|proofread\w*|ebook|e-book|book|script)\b"),
    ("Translation", r"\b(translat\w*|transcri\w*|interpreter|subtitl\w*|localization)\b"),
    ("SEO / Marketing", r"\b(seo|marketing|marketer|ads|ad|facebook|google ads|ppc|social media|smm|instagram|email|klaviyo|affiliate|growth|brand|influencer|linkedin|media buyer|campaign)\b"),
    ("Sales / Lead Gen", r"\b(lead|leads|sales|sdr|appointment|setter|cold|outreach|closer|b2b|prospecting|crm|hubspot|gohighlevel|ghl)\b"),
    ("Admin / Virtual Assistant", r"\b(virtual assistant|assistant|va|admin\w*|data entry|secretary|executive|bookkeep\w*|research|typing|scheduling|organizer|project manager|manager)\b"),
    ("Customer Support", r"\b(customer|support|service|chat|call|agent|helpdesk)\b"),
    ("Finance / Legal", r"\b(accountant|accounting|finance|financial|tax|quickbooks|legal|lawyer|contract|trading|forex|invoice|payroll)\b"),
    ("Engineering / Other Tech", r"\b(cad|autocad|solidworks|engineer\w*|architect\w*|electrical|mechanical|pcb|embedded|game|unity|unreal)\b"),
]
_CAT = [(n, re.compile(p, re.I)) for n, p in CATEGORY_RULES]

# NOTE: bare "virtual" is deliberately excluded - it mostly matches "virtual assistant" (a job title, not a work arrangement).
REMOTE_RX = re.compile(r"\b(remote(?:ly)?|work(?:ing)? from home|wfh|telecommut\w*|work(?: from)? anywhere|fully remote)\b", re.I)
ONSITE_RX = re.compile(r"\b(on[- ]?site|onsite|in[- ]?person|in[- ]?office|local only|hybrid)\b", re.I)
LONGTERM_RX = re.compile(r"\b(long[- ]?term|ongoing|full[- ]?time|part[- ]?time|permanent|retainer)\b", re.I)


def categorize(title: str) -> str:
    for name, rx in _CAT:
        if rx.search(title):
            return name
    return "Other"


def load_raw(files=None) -> pd.DataFrame:
    files = files or sorted(glob.glob(str(RAW / "*.csv")))
    if not files:
        raise FileNotFoundError(f"No CSVs in {RAW}")
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    return df


def load_clean(files=None, window=None) -> pd.DataFrame:
    """Clean data. window=(start,end) overrides auto dense-window detection."""
    df = load_raw(files)
    df["published_date"] = pd.to_datetime(df["published_date"], utc=True, errors="coerce")
    df = df.dropna(subset=["published_date", "title"]).drop_duplicates("link")
    df["title"] = df["title"].map(html.unescape)  # RSS titles carry HTML entities (&amp;, &#39;)
    df["date"] = df["published_date"].dt.tz_localize(None).dt.normalize()

    # A handful of stray rows sit months before the real scrape; keep the dense window only.
    if window is None:
        daily = df["date"].value_counts()
        dense = daily[daily > 100].index
        window = (dense.min(), dense.max())
    df = df[(df["date"] >= window[0]) & (df["date"] <= window[1])].copy()

    # Rate cleaning: hourly rates outside $3-$300 are treated as typos/placeholders.
    for c in ("hourly_low", "hourly_high"):
        df.loc[(df[c] < 3) | (df[c] > 300), c] = np.nan
    bad = df["hourly_low"] > df["hourly_high"]
    df.loc[bad, ["hourly_low", "hourly_high"]] = df.loc[bad, ["hourly_high", "hourly_low"]].values
    df["hourly_mid"] = df[["hourly_low", "hourly_high"]].mean(axis=1)
    df.loc[(df["budget"] < 5) | (df["budget"] > 100_000), "budget"] = np.nan

    df["title_clean"] = df["title"].str.lower().str.replace(r"[^a-z0-9+#.\s-]", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    df["category"] = df["title"].map(categorize)
    df["remote_mention"] = df["title"].map(lambda t: bool(REMOTE_RX.search(t)))
    df["onsite_mention"] = df["title"].map(lambda t: bool(ONSITE_RX.search(t)))
    df["longterm_mention"] = df["title"].map(lambda t: bool(LONGTERM_RX.search(t)))
    df["week"] = df["date"].dt.to_period("W-SUN").dt.start_time
    df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    df["country"] = df["country"].fillna("Unknown")
    return df.reset_index(drop=True)


def daily_counts(df, col="category", exclude_dates=()):
    t = df.groupby(["date", col]).size().unstack(fill_value=0)
    t = t.reindex(pd.date_range(t.index.min(), t.index.max()), fill_value=0)
    return t.drop(index=[pd.Timestamp(d) for d in exclude_dates if pd.Timestamp(d) in t.index])


def md_table(df: pd.DataFrame, floatfmt="{:,.2f}") -> str:
    d = df.copy()
    for c in d.columns:
        if d[c].dtype.kind == "f":
            d[c] = d[c].map(lambda v: floatfmt.format(v) if pd.notna(v) else "")
    head = "| " + " | ".join(map(str, d.columns)) + " |\n|" + "---|" * len(d.columns) + "\n"
    return head + "\n".join("| " + " | ".join(map(str, r)) + " |" for r in d.values)


def write_report(name: str, text: str):
    (REPORTS / name).write_text(text, encoding="utf-8")
