import json
import os
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
CONTENT_FILE = BASE_DIR / "content.json"

DEFAULT_CONTENT = {
    "hero_title": "bloodedvr",
    "hero_tagline": "My VR-heavy corner of the internet with the games I play, my sites, updates, and more.",
    "status_badge": "ONLINE // VR PLAYER // BLOODEDVR",
    "intro_note": "Usually playing something chaotic, testing new ideas, or making the site cooler.",
    "about": (
        "Hey, I'm bloodedvr. I like Animal Company, Roblox, Minecraft, VR games, and a lot more. "
        "This site is where I share what I play, what I make, and whatever cool stuff I'm into."
    ),
    "games": [
        "Animal Company",
        "Minecraft",
        "Roblox",
        "VR Games",
        "More multiplayer games",
    ],
    "websites": [
        {"name": "Main Website", "url": "https://example.com"},
        {"name": "My Roblox Stuff", "url": "https://example.com/roblox"},
        {"name": "My Projects", "url": "https://example.com/projects"},
    ],
    "more": [
        "I like retro glowing UI and game-style menus.",
        "I enjoy making websites and trying creative ideas.",
        "This site runs with Python and can be edited from the admin panel.",
    ],
    "announcements": [
        "bloodedvr site is now live.",
        "Admin panel can update the homepage in real time.",
    ],
    "posts": [
        {
            "title": "Welcome To My Site",
            "meta": "April 2026",
            "body": "This is my personal website where I post my games, links, announcements, and more stuff.",
        },
        {
            "title": "What I Play",
            "meta": "Games",
            "body": "Right now I like playing Animal Company, Roblox, Minecraft, VR games, and other fun stuff.",
        },
    ],
    "timeline": [
        "Started building my own websites",
        "Made a retro VR-style homepage",
        "Added a live admin dashboard",
    ],
    "projects": [
        "bloodedvr homepage",
        "Game-related web ideas",
        "Custom retro UI experiments",
    ],
    "skills": [
        "HTML",
        "CSS",
        "Python",
        "VR gaming",
        "Creative design ideas",
    ],
    "featured_video": "https://www.youtube.com/",
    "video_gallery": [
        {"name": "Latest Video Drop", "url": "https://www.youtube.com/"},
        {"name": "Gameplay Clip", "url": "https://www.tiktok.com/"},
    ],
    "image_gallery": [
        {"name": "VR Setup", "url": "https://images.unsplash.com/photo-1593508512255-86ab42a8e620?auto=format&fit=crop&w=900&q=80"},
        {"name": "Gaming Desk", "url": "https://images.unsplash.com/photo-1542751371-adc38448a05e?auto=format&fit=crop&w=900&q=80"},
        {"name": "Late Night Build", "url": "https://images.unsplash.com/photo-1511512578047-dfb367046420?auto=format&fit=crop&w=900&q=80"},
    ],
    "contact_email": "bloodedvr@example.com",
    "contact_discord": "bloodedvr",
    "contact_location": "Online",
    "footer_note": "bloodedvr terminal powered by Python and ready for Render.",
    "primary_button_label": "OPEN MY STUFF",
    "primary_button_url": "#links",
    "custom_html": (
        "<div class=\"custom-block\">"
        "<h3>bloodedvr // Extra Feed</h3>"
        "<p>Animal Company, Roblox, Minecraft, VR games, websites, updates, and more.</p>"
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
        raw_content = json.loads(CONTENT_FILE.read_text(encoding="utf-8"))
        merged = DEFAULT_CONTENT.copy()
        merged.update(raw_content)
        return merged
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


def parse_named_links(raw_text):
    items = []
    for line in raw_text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if "|" in clean:
            name, url = clean.split("|", 1)
            items.append({"name": name.strip(), "url": url.strip()})
        else:
            items.append({"name": clean, "url": clean})
    return items


def named_links_to_text(items):
    return "\n".join(
        f"{item.get('name', '').strip()} | {item.get('url', '').strip()}"
        for item in items
        if item.get("name") or item.get("url")
    )


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
        "intro_note": form.get("intro_note", "").strip(),
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
        "video_gallery": parse_named_links(form.get("video_gallery", "")),
        "image_gallery": parse_named_links(form.get("image_gallery", "")),
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
        "video_gallery_text": named_links_to_text(content.get("video_gallery", [])),
        "image_gallery_text": named_links_to_text(content.get("image_gallery", [])),
    }


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "maks-terminal-secret")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Maksiu04112013")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


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
