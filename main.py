import json
import os
from pathlib import Path

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for


BASE_DIR = Path(__file__).resolve().parent
PROFILES_FILE = BASE_DIR / "profiles.json"

DEFAULT_PROFILE = {
    "username": "BloodedVR",
    "hero_title": "BloodedVR",
    "hero_tagline": "A green-glow profile site for my games, projects, websites, and whatever I'm into.",
    "status_badge": "ONLINE // BLOODEDVR // VR PLAYER",
    "intro_note": "Usually playing Animal Company, testing a new idea, or making this site cooler.",
    "about": (
        "Hey, I'm BloodedVR. I like Animal Company, Roblox, Minecraft, VR games, and more. "
        "This is my own profile page where I can post updates, share my links, and show what I'm about."
    ),
    "games": [
        "Animal Company",
        "Roblox",
        "Minecraft",
        "VR Games",
        "Multiplayer Games",
    ],
    "websites": [
        {"name": "Main Website", "url": "https://example.com"},
        {"name": "Projects", "url": "https://example.com/projects"},
        {"name": "Profile Link", "url": "https://example.com/@BloodedVR"},
    ],
    "more": [
        "I like retro game menus and glowing terminal UI.",
        "I enjoy making websites feel personal instead of generic.",
        "This whole profile can be edited from the admin panel.",
    ],
    "announcements": [
        "The BloodedVR profile is live.",
        "Username profile pages are now enabled.",
    ],
    "posts": [
        {
            "title": "Welcome To My Page",
            "meta": "Profile Update",
            "body": "This is my own little corner of the internet with my games, websites, and updates.",
        },
        {
            "title": "What I Like",
            "meta": "Gaming",
            "body": "Animal Company, Roblox, Minecraft, VR games, and more fun stuff.",
        },
    ],
    "timeline": [
        "Started making my own websites",
        "Built a retro green profile page",
        "Turned it into a username-based profile system",
    ],
    "projects": [
        "BloodedVR profile page",
        "Custom terminal-style UI",
        "Multi-profile about-me site system",
    ],
    "skills": [
        "HTML",
        "CSS",
        "Python",
        "Creative UI ideas",
        "VR gaming",
    ],
    "contact_email": "bloodedvr@example.com",
    "contact_discord": "BloodedVR",
    "contact_location": "Online",
    "footer_note": "BloodedVR profile powered by Python and ready for Render.",
    "primary_button_label": "OPEN MY LINKS",
    "primary_button_url": "#links",
    "custom_html": (
        "<div class=\"custom-block\">"
        "<h3>BloodedVR // Extra Feed</h3>"
        "<p>Animal Company, Roblox, Minecraft, VR games, updates, and more.</p>"
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

DEFAULT_DATA = {
    "active_username": "BloodedVR",
    "profiles": {
        "bloodedvr": DEFAULT_PROFILE,
    },
}


def ensure_profiles_file():
    if not PROFILES_FILE.exists():
        PROFILES_FILE.write_text(json.dumps(DEFAULT_DATA, indent=2), encoding="utf-8")


def normalize_username(username):
    return username.strip().lstrip("@").lower()


def load_data():
    ensure_profiles_file()
    try:
        raw_data = json.loads(PROFILES_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        PROFILES_FILE.write_text(json.dumps(DEFAULT_DATA, indent=2), encoding="utf-8")
        return DEFAULT_DATA

    profiles = {}
    for key, profile in raw_data.get("profiles", {}).items():
        merged = DEFAULT_PROFILE.copy()
        merged.update(profile)
        profiles[normalize_username(profile.get("username", key) or key)] = merged

    if not profiles:
        profiles = DEFAULT_DATA["profiles"].copy()

    active_username = raw_data.get("active_username") or next(iter(profiles.values()))["username"]
    return {"active_username": active_username, "profiles": profiles}


def save_data(data):
    PROFILES_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_profile(username):
    data = load_data()
    profile = data["profiles"].get(normalize_username(username))
    return data, profile


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


def build_profile_from_request(form, existing_profile=None):
    existing_profile = existing_profile or DEFAULT_PROFILE
    username = form.get("username", existing_profile.get("username", "BloodedVR")).strip().lstrip("@") or "BloodedVR"
    return {
        "username": username,
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
        "contact_email": form.get("contact_email", "").strip(),
        "contact_discord": form.get("contact_discord", "").strip(),
        "contact_location": form.get("contact_location", "").strip(),
        "footer_note": form.get("footer_note", "").strip(),
        "primary_button_label": form.get("primary_button_label", "").strip(),
        "primary_button_url": form.get("primary_button_url", "").strip(),
        "custom_html": form.get("custom_html", "").strip(),
        "custom_css": form.get("custom_css", "").strip(),
    }


def build_admin_context(profile):
    websites_text = "\n".join(
        f"{site.get('name', '').strip()} | {site.get('url', '').strip()}"
        for site in profile.get("websites", [])
    )
    return {
        "content": profile,
        "games_text": "\n".join(profile.get("games", [])),
        "websites_text": websites_text,
        "more_text": "\n".join(profile.get("more", [])),
        "announcements_text": "\n".join(profile.get("announcements", [])),
        "timeline_text": "\n".join(profile.get("timeline", [])),
        "projects_text": "\n".join(profile.get("projects", [])),
        "skills_text": "\n".join(profile.get("skills", [])),
        "posts_text": posts_to_text(profile.get("posts", [])),
        "profile_url": f"/@{profile.get('username', 'BloodedVR')}",
    }


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "maks-terminal-secret")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Maksiu04112013")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


@app.route("/")
def home():
    data = load_data()
    return redirect(url_for("profile_page", username=data["active_username"]))


@app.route("/@<username>")
def profile_page(username):
    _, profile = get_profile(username)
    if not profile:
        abort(404)
    return render_template("home.html", content=profile)


@app.route("/<username>")
def profile_page_plain(username):
    if username in {"admin", "static"}:
        abort(404)
    _, profile = get_profile(username)
    if not profile:
        abort(404)
    return redirect(url_for("profile_page", username=profile["username"]))


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

    data = load_data()
    active_key = normalize_username(data["active_username"])
    profile = data["profiles"].get(active_key, DEFAULT_PROFILE.copy())

    if request.method == "POST":
        updated_profile = build_profile_from_request(request.form, profile)
        new_key = normalize_username(updated_profile["username"])
        old_key = normalize_username(profile["username"])
        if old_key in data["profiles"] and old_key != new_key:
            del data["profiles"][old_key]
        data["profiles"][new_key] = updated_profile
        data["active_username"] = updated_profile["username"]
        save_data(data)
        flash("Saved. Your profile site has been updated.", "success")
        return redirect(url_for("admin_panel"))

    return render_template("admin_panel.html", **build_admin_context(profile))


@app.post("/admin/save")
def admin_save():
    if not session.get("admin_logged_in"):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    data = load_data()
    active_key = normalize_username(data["active_username"])
    profile = data["profiles"].get(active_key, DEFAULT_PROFILE.copy())
    updated_profile = build_profile_from_request(request.form, profile)
    new_key = normalize_username(updated_profile["username"])
    old_key = normalize_username(profile["username"])
    if old_key in data["profiles"] and old_key != new_key:
        del data["profiles"][old_key]
    data["profiles"][new_key] = updated_profile
    data["active_username"] = updated_profile["username"]
    save_data(data)
    return jsonify({"ok": True, "message": "Live update saved.", "profile_url": f"/@{updated_profile['username']}"})


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
