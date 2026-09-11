import json
from pathlib import Path
import markdown

build_dir = Path(__file__).parent
issue = json.loads((build_dir / "issue.json").read_text(encoding="utf-8"))
comments = json.loads((build_dir / "comments.json").read_text(encoding="utf-8"))

parts = [
    f"# {issue['title']}",
    f"*Issue #{issue['number']} on `asluk/OpenUSD-proposals` — opened by {issue['author']['login']} on {issue['createdAt'][:10]}*",
    f"*{issue['url']}*",
    "---",
    issue["body"],
]

for c in comments:
    parts.append("---")
    parts.append(f"### Comment by {c['user']['login']} on {c['created_at'][:10]}")
    parts.append(c["body"])

combined_md = "\n\n".join(parts)

html_body = markdown.markdown(
    combined_md,
    extensions=["tables", "fenced_code", "sane_lists", "attr_list", "nl2br"],
)

css = """
body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
       max-width: 900px; margin: 2em auto; padding: 0 1em;
       line-height: 1.5; color: #1f2328; }
h1, h2 { border-bottom: 1px solid #d0d7de; padding-bottom: 0.3em; }
h1 { font-size: 1.8em; }
h2 { font-size: 1.4em; margin-top: 2em; }
h3 { font-size: 1.15em; margin-top: 1.5em; }
h4 { font-size: 1em; }
code { background: #f6f8fa; padding: 0.2em 0.4em; border-radius: 6px;
       font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
       font-size: 0.85em; }
pre { background: #f6f8fa; padding: 1em; border-radius: 6px; overflow: auto; }
pre code { background: none; padding: 0; }
blockquote { border-left: 0.25em solid #d0d7de; padding: 0.2em 1em;
             color: #59636e; margin-left: 0; }
table { border-collapse: collapse; margin: 1em 0; font-size: 0.9em; }
th, td { border: 1px solid #d0d7de; padding: 0.5em 0.8em; vertical-align: top; }
th { background: #f6f8fa; }
a { color: #0969da; text-decoration: none; }
hr { border: 0; border-top: 1px solid #d0d7de; margin: 2em 0; }
ul, ol { padding-left: 1.5em; }
li { margin: 0.2em 0; }
@page { size: letter; margin: 0.7in; }
@media print {
  h2, h3 { page-break-after: avoid; }
  pre, blockquote, table { page-break-inside: avoid; }
}
"""

html_doc = (
    "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
    f"<title>{issue['title']}</title>"
    f"<style>{css}</style></head>"
    f"<body>{html_body}</body></html>"
)

(build_dir / "issue.html").write_text(html_doc, encoding="utf-8")
print(f"Wrote {build_dir / 'issue.html'}")
print(f"Comments included: {len(comments)}")
