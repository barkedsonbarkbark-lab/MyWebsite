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

RESERVED_USERNAMES = {"admin", "static", "create"}


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


def profile_excerpt(profile):
    about = (profile.get("about") or "").strip()
    if not about:
        return ""
    return about[:117] + "..." if len(about) > 120 else about


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


def build_profile_list(profiles, active_username):
    active_key = normalize_username(active_username)
    items = []
    for key, profile in sorted(profiles.items(), key=lambda item: item[1].get("username", "").lower()):
        items.append(
            {
                "key": key,
                "username": profile.get("username", ""),
                "hero_title": profile.get("hero_title", profile.get("username", "")),
                "hero_tagline": profile.get("hero_tagline", ""),
                "profile_url": f"/@{profile.get('username', '')}",
                "is_active": key == active_key,
            }
        )
    return items


def build_public_profile_from_request(form):
    username = form.get("username", "").strip().lstrip("@") or "NewUser"
    display_name = form.get("display_name", "").strip() or username
    tagline = form.get("hero_tagline", "").strip() or "Just launched my own page on this site."
    about = form.get("about", "").strip() or "This is my new page."
    favorite_things = parse_lines(form.get("favorite_things", ""))
    links = parse_websites(form.get("websites", ""))

    profile = DEFAULT_PROFILE.copy()
    profile.update(
        {
            "username": username,
            "hero_title": display_name,
            "hero_tagline": tagline,
            "status_badge": f"ONLINE // @{username.upper()}",
            "intro_note": form.get("intro_note", "").strip() or "Building my own homepage.",
            "about": about,
            "games": favorite_things or ["Web design", "Games", "Projects"],
            "websites": links or [{"name": "My first link", "url": "#links"}],
            "more": parse_lines(form.get("more", "")) or [
                "Made this page with the built-in creator.",
                "Adding more stuff soon.",
            ],
            "announcements": [f"{display_name} just created a page."],
            "posts": [
                {
                    "title": "My Page Is Live",
                    "meta": "First Post",
                    "body": form.get("first_post", "").strip()
                    or "I just launched my page here and I'm going to keep customizing it.",
                }
            ],
            "timeline": ["Created my page", "Shared my favorite things", "Ready for updates"],
            "projects": parse_lines(form.get("projects", "")) or ["My personal homepage"],
            "skills": parse_lines(form.get("skills", "")) or ["Creativity", "Internet", "Ideas"],
            "contact_email": form.get("contact_email", "").strip(),
            "contact_discord": form.get("contact_discord", "").strip(),
            "contact_location": form.get("contact_location", "").strip() or "Online",
            "footer_note": f"{display_name}'s page is live on the creator hub.",
            "primary_button_label": "OPEN MY LINKS",
            "primary_button_url": "#links",
            "custom_html": "",
            "custom_css": "",
        }
    )
    return profile


def build_admin_context(profile, data, selected_key):
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
        "selected_key": selected_key,
        "active_username": data["active_username"],
        "profile_count": len(data["profiles"]),
        "profile_cards": build_profile_list(data["profiles"], data["active_username"]),
    }


def build_homepage_context():
    data = load_data()
    active_key = normalize_username(data["active_username"])
    active_profile = data["profiles"].get(active_key)

    cards = []
    for profile in data["profiles"].values():
        cards.append(
            {
                "username": profile.get("username", ""),
                "hero_title": profile.get("hero_title", profile.get("username", "")),
                "hero_tagline": profile.get("hero_tagline", ""),
                "intro_note": profile.get("intro_note", ""),
                "about_excerpt": profile_excerpt(profile),
                "projects_count": len(profile.get("projects", [])),
                "links_count": len(profile.get("websites", [])),
            }
        )

    cards.sort(key=lambda item: item["username"].lower())
    return {"active_profile": active_profile, "profile_cards": cards, "profile_count": len(cards)}


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "maks-terminal-secret")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Maksiu04112013")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


@app.route("/")
def home():
    return render_template("landing.html", **build_homepage_context())


@app.route("/create", methods=["GET", "POST"])
def create_profile():
    form_data = {
        "username": "",
        "display_name": "",
        "hero_tagline": "",
        "intro_note": "",
        "about": "",
        "favorite_things": "",
        "websites": "",
        "projects": "",
        "skills": "",
        "more": "",
        "first_post": "",
        "contact_email": "",
        "contact_discord": "",
        "contact_location": "",
    }

    if request.method == "POST":
        form_data.update({key: request.form.get(key, "") for key in form_data})
        username = request.form.get("username", "")
        normalized = normalize_username(username)

        if not normalized:
            flash("Choose a username first.", "error")
        elif normalized in RESERVED_USERNAMES:
            flash("That username is reserved. Pick a different one.", "error")
        else:
            data = load_data()
            if normalized in data["profiles"]:
                flash("That username already exists. Try another one.", "error")
            else:
                profile = build_public_profile_from_request(request.form)
                data["profiles"][normalized] = profile
                save_data(data)
                flash("Your page is live now.", "success")
                return redirect(url_for("profile_page", username=profile["username"]))

    return render_template("create_profile.html", form_data=form_data)


@app.route("/@<username>")
def profile_page(username):
    _, profile = get_profile(username)
    if not profile:
        abort(404)
    return render_template("home.html", content=profile)


@app.route("/<username>")
def profile_page_plain(username):
    if normalize_username(username) in RESERVED_USERNAMES:
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
    selected_key = normalize_username(request.args.get("profile") or data["active_username"])
    profile = data["profiles"].get(selected_key)
    if not profile:
        selected_key = normalize_username(data["active_username"])
        profile = data["profiles"].get(selected_key, DEFAULT_PROFILE.copy())

    if request.method == "POST":
        action = request.form.get("action", "save")
        original_key = normalize_username(request.form.get("original_username", profile.get("username", "")))

        if action == "new":
            new_profile = DEFAULT_PROFILE.copy()
            new_profile["username"] = "NewUser"
            new_profile["hero_title"] = "New User"
            new_profile["hero_tagline"] = "A fresh page waiting to be customized."
            base_key = normalize_username(new_profile["username"])
            new_key = base_key
            index = 1
            while new_key in data["profiles"] or new_key in RESERVED_USERNAMES:
                index += 1
                new_profile["username"] = f"NewUser{index}"
                new_profile["hero_title"] = f"New User {index}"
                new_key = normalize_username(new_profile["username"])
            data["profiles"][new_key] = new_profile
            save_data(data)
            flash("New profile created. You can edit it now.", "success")
            return redirect(url_for("admin_panel", profile=new_profile["username"]))

        if action == "delete":
            if len(data["profiles"]) <= 1:
                flash("You need at least one profile on the site.", "error")
                return redirect(url_for("admin_panel", profile=profile["username"]))
            if original_key not in data["profiles"]:
                flash("That profile no longer exists.", "error")
                return redirect(url_for("admin_panel"))

            deleted_profile = data["profiles"].pop(original_key)
            if normalize_username(data["active_username"]) == original_key:
                replacement = next(iter(data["profiles"].values()))
                data["active_username"] = replacement["username"]
            save_data(data)
            flash(f"Deleted @{deleted_profile['username']}.", "success")
            return redirect(url_for("admin_panel", profile=data["active_username"]))

        if action == "feature":
            if original_key not in data["profiles"]:
                flash("That profile no longer exists.", "error")
                return redirect(url_for("admin_panel"))
            data["active_username"] = data["profiles"][original_key]["username"]
            save_data(data)
            flash(f"Homepage featured profile set to @{data['active_username']}.", "success")
            return redirect(url_for("admin_panel", profile=data["active_username"]))

        updated_profile = build_profile_from_request(request.form, profile)
        new_key = normalize_username(updated_profile["username"])
        if not new_key:
            flash("Username cannot be empty.", "error")
            return redirect(url_for("admin_panel", profile=profile["username"]))
        if new_key in RESERVED_USERNAMES:
            flash("That username is reserved.", "error")
            return redirect(url_for("admin_panel", profile=profile["username"]))
        if new_key != original_key and new_key in data["profiles"]:
            flash("That username already exists.", "error")
            return redirect(url_for("admin_panel", profile=profile["username"]))
        if original_key in data["profiles"] and original_key != new_key:
            del data["profiles"][original_key]
        data["profiles"][new_key] = updated_profile
        if normalize_username(data["active_username"]) == original_key:
            data["active_username"] = updated_profile["username"]
        save_data(data)
        flash("Saved. This profile has been updated.", "success")
        return redirect(url_for("admin_panel", profile=updated_profile["username"]))

    return render_template("admin_panel.html", **build_admin_context(profile, data, selected_key))


@app.post("/admin/save")
def admin_save():
    if not session.get("admin_logged_in"):
        return jsonify({"ok": False, "error": "Unauthorized"}), 401

    data = load_data()
    original_key = normalize_username(request.form.get("original_username", data["active_username"]))
    profile = data["profiles"].get(original_key)
    if not profile:
        return jsonify({"ok": False, "error": "Profile not found"}), 404

    updated_profile = build_profile_from_request(request.form, profile)
    new_key = normalize_username(updated_profile["username"])
    if not new_key:
        return jsonify({"ok": False, "error": "Username cannot be empty"}), 400
    if new_key in RESERVED_USERNAMES:
        return jsonify({"ok": False, "error": "That username is reserved"}), 400
    if new_key != original_key and new_key in data["profiles"]:
        return jsonify({"ok": False, "error": "That username already exists"}), 400

    if original_key in data["profiles"] and original_key != new_key:
        del data["profiles"][original_key]
    data["profiles"][new_key] = updated_profile
    if normalize_username(data["active_username"]) == original_key:
        data["active_username"] = updated_profile["username"]
    save_data(data)
    return jsonify(
        {
            "ok": True,
            "message": "Live update saved.",
            "profile_url": f"/@{updated_profile['username']}",
            "selected_key": new_key,
            "active_username": data["active_username"],
        }
    )


@app.post("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port)
