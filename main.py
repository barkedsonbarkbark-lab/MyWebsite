import json
import os
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
CONTENT_FILE = BASE_DIR / "content.json"

DEFAULT_CONTENT = {
    "hero_title": "Maks Terminal",
    "hero_tagline": "A personal page for the games I play, the sites I build, and the stuff I'm into.",
    "status_badge": "ONLINE // BUILDING COOL STUFF",
    "about": (
        "Hey, I'm Maks. This page is my corner of the internet where I can show what I play, "
        "what I make, and whatever else feels worth sharing."
    ),
    "games": [
        "Animal Company",
        "Minecraft",
        "Roblox",
        "Fortnite",
    ],
    "websites": [
        {"name": "Main Website", "url": "https://example.com"},
        {"name": "Projects Page", "url": "https://example.com/projects"},
        {"name": "Profile Link", "url": "https://example.com/profile"},
    ],
    "more": [
        "I like building cool web stuff.",
        "I enjoy retro game menus and glowing UI.",
        "This site runs with Python and can be edited from the admin panel.",
    ],
    "announcements": [
        "New update: admin panel now controls the whole homepage.",
        "Site is live and ready for more custom sections.",
    ],
    "posts": [
        {
            "title": "First Post",
            "meta": "April 2026",
            "body": "This site is my own little command center on the internet.",
        },
        {
            "title": "What I'm Building",
            "meta": "Projects",
            "body": "I like making pages that feel like game menus and old terminals.",
        },
    ],
    "timeline": [
        "Started making websites",
        "Built a retro-styled personal page",
        "Added a real admin control panel",
    ],
    "projects": [
        "Personal homepage",
        "Mini game ideas",
        "Custom web UI experiments",
    ],
    "skills": [
        "HTML",
        "CSS",
        "Python",
        "Design ideas",
    ],
    "featured_video": "",
    "contact_email": "maks@example.com",
    "contact_discord": "maks_dev",
    "contact_location": "Poland",
    "footer_note": "Powered by Python on port 8000.",
    "primary_button_label": "OPEN MY LINKS",
    "primary_button_url": "#links",
    "custom_html": (
        "<div class=\"custom-block\">"
        "<h3>Custom HTML Area</h3>"
        "<p>You can write your own HTML here from the admin panel.</p>"
        "</div>"
    ),
    "custom_css": (
        ".custom-block {"
        " border: 1px solid rgba(84, 255, 157, 0.28);"
        " padding: 18px;"
        " background: rgba(84, 255, 157, 0.05);"
        "}"
    ),
}


def ensure_content_file():
    if not CONTENT_FILE.exists():
        CONTENT_FILE.write_text(json.dumps(DEFAULT_CONTENT, indent=2), encoding="utf-8")


def load_content():
    ensure_content_file()
    try:
        return json.loads(CONTENT_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        CONTENT_FILE.write_text(json.dumps(DEFAULT_CONTENT, indent=2), encoding="utf-8")
        return DEFAULT_CONTENT


def save_content(content):
    CONTENT_FILE.write_text(json.dumps(content, indent=2), encoding="utf-8")


def parse_lines(raw_text):
    return [line.strip() for line in raw_text.splitlines() if line.strip()]


def parse_websites(raw_text):
    websites = []
    for line in raw_text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if "|" in clean:
            name, url = clean.split("|", 1)
            websites.append({"name": name.strip(), "url": url.strip()})
        else:
            websites.append({"name": clean, "url": "#"})
    return websites


def parse_posts(raw_text):
    posts = []
    for block in raw_text.strip().split("\n\n"):
        clean = [line.strip() for line in block.splitlines() if line.strip()]
        if not clean:
            continue
        title = clean[0]
        meta = clean[1] if len(clean) > 1 else ""
        body = " ".join(clean[2:]) if len(clean) > 2 else ""
        posts.append({"title": title, "meta": meta, "body": body})
    return posts


def posts_to_text(posts):
    chunks = []
    for post in posts:
        chunks.append(
            "\n".join(
                [
                    post.get("title", "").strip(),
                    post.get("meta", "").strip(),
                    post.get("body", "").strip(),
                ]
            ).strip()
        )
    return "\n\n".join(chunk for chunk in chunks if chunk)


def build_content_from_request(form):
    return {
        "hero_title": form.get("hero_title", "").strip(),
        "hero_tagline": form.get("hero_tagline", "").strip(),
        "status_badge": form.get("status_badge", "").strip(),
        "about": form.get("about", "").strip(),
        "games": parse_lines(form.get("games", "")),
        "websites": parse_websites(form.get("websites", "")),
        "more": parse_lines(form.get("more", "")),
        "announcements": parse_lines(form.get("announcements", "")),
        "posts": parse_posts(form.get("posts", "")),
        "timeline": parse_lines(form.get("timeline", "")),
        "projects": parse_lines(form.get("projects", "")),
        "skills": parse_lines(form.get("skills", "")),
        "featured_video": form.get("featured_video", "").strip(),
        "contact_email": form.get("contact_email", "").strip(),
        "contact_discord": form.get("contact_discord", "").strip(),
        "contact_location": form.get("contact_location", "").strip(),
        "footer_note": form.get("footer_note", "").strip(),
        "primary_button_label": form.get("primary_button_label", "").strip(),
        "primary_button_url": form.get("primary_button_url", "").strip(),
        "custom_html": form.get("custom_html", "").strip(),
        "custom_css": form.get("custom_css", "").strip(),
    }


def build_admin_context(content):
    websites_text = "\n".join(
        f"{site.get('name', '').strip()} | {site.get('url', '').strip()}"
        for site in content.get("websites", [])
    )
    return {
        "content": content,
        "games_text": "\n".join(content.get("games", [])),
        "websites_text": websites_text,
        "more_text": "\n".join(content.get("more", [])),
        "announcements_text": "\n".join(content.get("announcements", [])),
        "timeline_text": "\n".join(content.get("timeline", [])),
        "projects_text": "\n".join(content.get("projects", [])),
        "skills_text": "\n".join(content.get("skills", [])),
        "posts_text": posts_to_text(content.get("posts", [])),
    }


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "maks-terminal-secret")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Maksiu04112013")


@app.route("/")
def home():
    return render_template("home.html", content=load_content())


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        password = request.form.get("password", "")
        if password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_panel"))
        flash("Wrong password. Try again.", "error")
    return render_template("admin_login.html")


@app.route("/admin", methods=["GET", "POST"])
def admin_panel():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    content = load_content()

    if request.method == "POST":
        content = build_content_from_request(request.form)
        save_content(content)
        flash("Saved. Your site content has been updated.", "success")
        return redirect(url_for("admin_panel"))

    return render_template("admin_panel.html", **build_admin_context(content))


@app.post("/admin/save")
def admin_save():
    if not session.get("admin_logged_in"):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    content = build_content_from_request(request.form)
    save_content(content)
    return jsonify({"ok": True, "message": "Live update saved."})


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
