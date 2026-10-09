#!/usr/bin/env python3
"""
Refresh the projects section of profile/README.md from real GitHub data.

Fetches the org's public repositories, assigns each one to a category
(curated overrides first, keyword rules as a fallback for new repos),
renders a markdown list and rewrites the file between the PROJECTS markers.
Also stores a pruned snapshot in data/repos.json (used by the whoami card).

Stdlib only -- no third-party dependencies.

    python3 scripts/update_projects.py
"""
import json
import os
import urllib.request

ORG = "ACADEMIC-AND-PERSONAL-PROJECTS"
HERE = os.path.dirname(os.path.abspath(__file__))
README = os.path.join(HERE, "..", "profile", "README.md")
DATA = os.path.join(HERE, "..", "data", "repos.json")
START = "<!-- PROJECTS:START -->"
END = "<!-- PROJECTS:END -->"

# display order
CATEGORIES = [
    "Data Engineering",
    "AI Engineering & Agents",
    "Machine Learning & AI",
    "Full-Stack & Apps",
    "Learning & Foundations",
]
DEFAULT_CAT = "Learning & Foundations"

# curated placement for known repos
OVERRIDES = {
    "APACHE_AIRFLOW_WORKS": "Data Engineering",
    "NeuralPulse": "AI Engineering & Agents",
    "Customer-Support-Agent": "AI Engineering & Agents",
    "langchain4j-quickstart": "AI Engineering & Agents",
    "AI-DEV-TOOLS-ZOOMCAMP-HOMEWORK_1": "AI Engineering & Agents",
    "MIT_WEEK4_Margin_Maximization": "Machine Learning & AI",
    "MIT_WEEK5_Regression": "Machine Learning & AI",
    "MIT_WEEK6_Neural_Network_I": "Machine Learning & AI",
    "MIT_WEEK7_Neural_Network_II": "Machine Learning & AI",
    "Homework-1-Introduction-to-Machine-Learning": "Machine Learning & AI",
    "Homework-2-Machine-Learning-for-Regression": "Machine Learning & AI",
    "Homework-3-Machine-Learning-for-Classification": "Machine Learning & AI",
    "EDA-WITH-PYTHON": "Machine Learning & AI",
    "California-Housing-Prices": "Machine Learning & AI",
    "Google-DeepMind-AI-Research-Foundations-solutions": "Machine Learning & AI",
    "IPDL_v2": "Full-Stack & Apps",
    "TECHBLOCKS": "Full-Stack & Apps",
    "LeagueScore": "Full-Stack & Apps",
    "tontine-pilot": "Full-Stack & Apps",
    "TRACE": "Full-Stack & Apps",
    "SCALA-BANK": "Learning & Foundations",
}

# fallback keyword rules for repos that appear later
RULES = [
    ("Data Engineering", ["airflow", "spark", "warehouse", "pipeline", "etl", "dbt"]),
    ("AI Engineering & Agents", ["agent", "llm", "langchain", "rag", "chatbot", "pydantic"]),
    ("Machine Learning & AI", ["machine learning", "neural", "regression", "classification",
                               "deep learning", "pytorch", "tensorflow", "deepmind"]),
    ("Full-Stack & Apps", ["react", "spring", "full-stack", "fullstack", "web", "api", "app", "store"]),
]


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/orgs/{ORG}/repos?per_page=100&type=public",
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "org-readme-bot/1.0"})
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        repos = json.load(resp)
    return [r for r in repos if not r["fork"] and r["name"] != ".github"]


def category_of(repo):
    name = repo["name"]
    if name in OVERRIDES:
        return OVERRIDES[name]
    hay = " ".join([name, repo.get("description") or "",
                    " ".join(repo.get("topics") or [])]).lower()
    for label, words in RULES:
        if any(w in hay for w in words):
            return label
    return DEFAULT_CAT


def clip(text, n=215):
    text = " ".join((text or "").split())
    if len(text) <= n:
        return text
    return text[:n].rsplit(" ", 1)[0] + " …"


def render(repos):
    by_cat = {}
    for r in repos:
        by_cat.setdefault(category_of(r), []).append(r)
    out = []
    for label in CATEGORIES:
        items = by_cat.get(label) or []
        if not items:
            continue
        out.append(f"#### {label}")
        out.append("")
        for r in sorted(items, key=lambda r: r.get("pushed_at") or "", reverse=True):
            desc = clip(r.get("description"))
            line = f"- **[{r['name']}]({r['html_url']})**"
            if desc:
                line += f" — {desc}"
            elif r.get("language"):
                line += f" — `{r['language']}`"
            out.append(line)
        out.append("")
    return "\n".join(out).strip()


def main():
    repos = fetch_repos()
    block = render(repos)

    with open(README) as f:
        text = f.read()
    if START not in text or END not in text:
        raise SystemExit("PROJECTS markers not found in README")
    pre = text.split(START)[0]
    post = text.split(END)[1]
    with open(README, "w") as f:
        f.write(f"{pre}{START}\n\n{block}\n\n{END}{post}")

    os.makedirs(os.path.dirname(DATA), exist_ok=True)
    keep = ["name", "html_url", "description", "language", "pushed_at", "fork", "topics"]
    snapshot = [{k: r.get(k) for k in keep} for r in repos]
    with open(DATA, "w") as f:
        json.dump(snapshot, f, indent=1, ensure_ascii=False)

    cats = sum(1 for label in CATEGORIES
               if any(category_of(r) == label for r in repos))
    print(f"wrote {README}: {len(repos)} repos in {cats} categories | snapshot -> {DATA}")


if __name__ == "__main__":
    main()
