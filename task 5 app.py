import os
import sqlite3
from datetime import datetime
from flask import Flask, g, redirect, render_template_string, request, session, url_for

app = Flask(__name__)
app.secret_key = "ngo_media_secret_key_change_me"
DATABASE = "ngo_media.db"

# --- DATABASE SETUP ---


def get_db():
  db = getattr(g, "_database", None)
  if db is None:
    db = g._database = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
  return db


@app.teardown_appcontext
def close_connection(exception):
  db = getattr(g, "_database", None)
  if db is not None:
    db.close()


def init_db():
  with app.app_context():
    db = get_db()
    # 1. press_releases table[cite: 2]
    db.execute("""
            CREATE TABLE IF NOT EXISTS press_releases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                description TEXT NOT NULL,
                release_date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    # 2. media_coverage table[cite: 2]
    db.execute("""
            CREATE TABLE IF NOT EXISTS media_coverage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                url VARCHAR(2083) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    # 3. image_gallery table[cite: 2]
    db.execute("""
            CREATE TABLE IF NOT EXISTS image_gallery (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_path VARCHAR(2083) NOT NULL,
                description VARCHAR(255),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    # 4. videos table[cite: 1, 2]
    db.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_url VARCHAR(2083) NOT NULL,
                description VARCHAR(255),
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    db.commit()


# --- HTML TEMPLATES (Embedded for Single-File Execution) ---

BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}NGO Media Page{% endblock %}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f6f9; color: #333; }
        header { background: #004080; color: #fff; padding: 1.5rem; text-align: center; }
        nav { background: #002b5c; padding: 0.75rem; text-align: center; }
        nav a { color: #fff; text-decoration: none; margin: 0 15px; font-weight: bold; }
        nav a:hover { text-decoration: underline; }
        .container { max-width: 1000px; margin: 2rem auto; background: #fff; padding: 2rem; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        h1, h2, h3 { color: #004080; }
        table { width: 100%; border-collapse: collapse; margin-top: 1rem; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
        th { background-color: #004080; color: white; }
        .btn { background: #004080; color: white; padding: 8px 14px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; font-size: 14px;}
        .btn:hover { background: #002b5c; }
        .btn-danger { background: #d9534f; }
        .btn-danger:hover { background: #c9302c; }
        .btn-warning { background: #f0ad4e; }
        .btn-warning:hover { background: #ec971f; }
        form label { display: block; margin-top: 10px; font-weight: bold; }
        form input[type="text"], form input[type="date"], form input[type="password"], form textarea { width: 100%; padding: 8px; margin-top: 5px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
        form textarea { height: 100px; }
        .gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 15px; margin-top: 1rem; }
        .gallery-item { border: 1px solid #ddd; border-radius: 4px; padding: 10px; background: #fafafa; text-align: center; }
        .gallery-item img { max-width: 100%; height: 140px; object-fit: cover; border-radius: 4px; }
        footer { text-align: center; padding: 1rem; background: #004080; color: white; margin-top: 2rem; }
    </style>
</head>
<body>
    <header>
        <h1>NGO Hope Foundation - Media Center</h1>
    </header>
    <nav>
        <a href="{{ url_for('index') }}">Public Media Page</a>
        {% if session.get('logged_in') %}
            <a href="{{ url_for('admin_dashboard') }}">Admin Dashboard</a>
            <a href="{{ url_for('logout') }}">Logout</a>
        {% else %}
            <a href="{{ url_for('admin_login') }}">Admin Login</a>
        {% endif %}
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
    <footer>
        <p>&copy; 2026 NGO Hope Foundation. All rights reserved.</p>
    </footer>
</body>
</html>
"""

PUBLIC_TEMPLATE = (
    BASE_LAYOUT.replace(
        "{% block content %}{% endblock %}",
        """
    <h2>Introduction</h2>
    <p>Welcome to the official NGO Media Page. This section highlights our recent press releases, media coverage, photo gallery, and impactful campaign videos reflecting our core mission and community outreach[cite: 1, 5].</p>
    <hr>

    <h2>Press Releases</h2>
    {% if press_releases %}
        <ul>
        {% for pr in press_releases %}
            <li><strong>{{ pr.title }}</strong> (<em>{{ pr.release_date }}</em>)<br>{{ pr.description }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No press releases available at the moment.</p>
    {% endif %}
    <hr>

    <h2>Media Coverage</h2>
    {% if media_coverages %}
        <ul>
        {% for mc in media_coverages %}
            <li><strong>{{ mc.title }}</strong> - <a href="{{ mc.url }}" target="_blank">View Article/Source</a></li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No media coverage records found.</p>
    {% endif %}
    <hr>

    <h2>Image Gallery</h2>
    {% if images %}
        <div class="gallery-grid">
        {% for img in images %}
            <div class="gallery-item">
                <img src="{{ img.image_path }}" alt="Gallery Image">
                <p>{{ img.description or 'NGO Event Image' }}</p>
            </div>
        {% endfor %}
        </div>
    {% else %}
        <p>No images uploaded yet.</p>
    {% endif %}
    <hr>

    <h2>Video Highlights</h2>
    {% if videos %}
        <ul>
        {% for vid in videos %}
            <li><a href="{{ vid.video_url }}" target="_blank">Watch Video</a> - {{ vid.description or 'Campaign Video' }}</li>
        {% endfor %}
        </ul>
    {% else %}
        <p>No videos available.</p>
    {% endif %}
    <hr>

    <h2>Contact for Media</h2>
    <p>For journalists, press inquiries, or collaboration opportunities[cite: 6], please reach out to our communications team:</p>
    <ul>
        <li><strong>Email:</strong> media@ngohope.org</li>
        <li><strong>Phone:</strong> +1 (555) 123-4567</li>
    </ul>
""",
    )
)

LOGIN_TEMPLATE = (
    BASE_LAYOUT.replace(
        "{% block content %}{% endblock %}",
        """
    <h2>Admin Login</h2>
    {% if error %}<p style="color:red;">{{ error }}</p>{% endif %}
    <form method="POST">
        <label>Username:</label>
        <input type="text" name="username" required>
        <label>Password:</label>
        <input type="password" name="password" required><br><br>
        <button type="submit" class="btn">Login</button>
    </form>
    <p><small>Default credentials: <b>admin</b> / <b>admin123</b></small></p>
""",
    )
)

DASHBOARD_TEMPLATE = (
    BASE_LAYOUT.replace(
        "{% block content %}{% endblock %}",
        """
    <h2>Admin Dashboard - Manage Media Content</h2>
    
    <h3>1. Press Releases</h3>
    <a href="{{ url_for('add_press') }}" class="btn">+ Add Press Release</a>
    <table>
        <tr><th>Title</th><th>Date</th><th>Actions</th></tr>
        {% for pr in press_releases %}
        <tr>
            <td>{{ pr.title }}</td>
            <td>{{ pr.release_date }}</td>
            <td>
                <a href="{{ url_for('edit_press', id=pr.id) }}" class="btn btn-warning">Edit</a>
                <a href="{{ url_for('delete_press', id=pr.id) }}" class="btn btn-danger" onclick="return confirm('Are you sure?');">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>

    <h3 style="margin-top:30px;">2. Media Coverage</h3>
    <a href="{{ url_for('add_media') }}" class="btn">+ Add Media Coverage</a>
    <table>
        <tr><th>Title</th><th>URL</th><th>Actions</th></tr>
        {% for mc in media_coverages %}
        <tr>
            <td>{{ mc.title }}</td>
            <td><a href="{{ mc.url }}" target="_blank">Link</a></td>
            <td>
                <a href="{{ url_for('edit_media', id=mc.id) }}" class="btn btn-warning">Edit</a>
                <a href="{{ url_for('delete_media', id=mc.id) }}" class="btn btn-danger" onclick="return confirm('Are you sure?');">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>

    <h3 style="margin-top:30px;">3. Image Gallery</h3>
    <a href="{{ url_for('add_image') }}" class="btn">+ Add Image</a>
    <table>
        <tr><th>Image Path / URL</th><th>Description</th><th>Actions</th></tr>
        {% for img in images %}
        <tr>
            <td>{{ img.image_path }}</td>
            <td>{{ img.description }}</td>
            <td>
                <a href="{{ url_for('edit_image', id=img.id) }}" class="btn btn-warning">Edit</a>
                <a href="{{ url_for('delete_image', id=img.id) }}" class="btn btn-danger" onclick="return confirm('Are you sure?');">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>

    <h3 style="margin-top:30px;">4. Videos</h3>
    <a href="{{ url_for('add_video') }}" class="btn">+ Add Video</a>
    <table>
        <tr><th>Video URL</th><th>Description</th><th>Actions</th></tr>
        {% for vid in videos %}
        <tr>
            <td><a href="{{ vid.video_url }}" target="_blank">View Video</a></td>
            <td>{{ vid.description }}</td>
            <td>
                <a href="{{ url_for('edit_video', id=vid.id) }}" class="btn btn-warning">Edit</a>
                <a href="{{ url_for('delete_video', id=vid.id) }}" class="btn btn-danger" onclick="return confirm('Are you sure?');">Delete</a>
            </td>
        </tr>
        {% endfor %}
    </table>
""",
    )
)

FORM_TEMPLATE = (
    BASE_LAYOUT.replace(
        "{% block content %}{% endblock %}",
        """
    <h2>{{ action_title }}</h2>
    <form method="POST">
        {% for field in fields %}
            <label>{{ field.label }}</label>
            {% if field.type == 'textarea' %}
                <textarea name="{{ field.name }}" required>{{ field.value or '' }}</textarea>
            {% elif field.type == 'date' %}
                <input type="date" name="{{ field.name }}" value="{{ field.value or '' }}" required>
            {% else %}
                <input type="text" name="{{ field.name }}" value="{{ field.value or '' }}" required>
            {% endif %}
        {% endfor %}
        <br><br>
        <button type="submit" class="btn">Save Record</button>
        <a href="{{ url_for('admin_dashboard') }}" class="btn" style="background:#6c757d;">Cancel</a>
    </form>
""",
    )
)


# --- ROUTES ---


@app.route("/")
def index():
  db = get_db()
  press_releases = db.execute(
      "SELECT * FROM press_releases ORDER BY release_date DESC"
  ).fetchall()
  media_coverages = db.execute(
      "SELECT * FROM media_coverage ORDER BY created_at DESC"
  ).fetchall()
  images = db.execute(
      "SELECT * FROM image_gallery ORDER BY uploaded_at DESC"
  ).fetchall()
  videos = db.execute(
      "SELECT * FROM videos ORDER BY uploaded_at DESC"
  ).fetchall()
  return render_template_string(
      PUBLIC_TEMPLATE,
      press_releases=press_releases,
      media_coverages=media_coverages,
      images=images,
      videos=videos,
  )


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
  error = None
  if request.method == "POST":
    if (
        request.form["username"] == "admin"
        and request.form["password"] == "admin123"
    ):
      session["logged_in"] = True
      return redirect(url_for("admin_dashboard"))
    else:
      error = "Invalid Credentials. Please try again."
  return render_template_string(LOGIN_TEMPLATE, error=error)


@app.route("/admin/logout")
def logout():
  session.pop("logged_in", None)
  return redirect(url_for("index"))


@app.route("/admin")
def admin_dashboard():
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  db = get_db()
  press_releases = db.execute("SELECT * FROM press_releases").fetchall()
  media_coverages = db.execute("SELECT * FROM media_coverage").fetchall()
  images = db.execute("SELECT * FROM image_gallery").fetchall()
  videos = db.execute("SELECT * FROM videos").fetchall()
  return render_template_string(
      DASHBOARD_TEMPLATE,
      press_releases=press_releases,
      media_coverages=media_coverages,
      images=images,
      videos=videos,
  )


# --- CRUD: PRESS RELEASES ---
@app.route("/admin/press/add", methods=["GET", "POST"])
def add_press():
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  if request.method == "POST":
    db = get_db()
    db.execute(
        "INSERT INTO press_releases (title, description, release_date) VALUES"
        " (?, ?, ?)",
        (
            request.form["title"],
            request.form["description"],
            request.form["release_date"],
        ),
    )
    db.commit()
    return redirect(url_for("admin_dashboard"))
  fields = [
      {"name": "title", "label": "Title", "type": "text"},
      {"name": "description", "label": "Description", "type": "textarea"},
      {"name": "release_date", "label": "Release Date", "type": "date"},
  ]
  return render_template_string(
      FORM_TEMPLATE, action_title="Add Press Release", fields=fields
  )


@app.route("/admin/press/edit/<int:id>", methods=["GET", "POST"])
def edit_press(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  db = get_db()
  item = db.execute(
      "SELECT * FROM press_releases WHERE id = ?", (id,)
  ).fetchone()
  if request.method == "POST":
    db.execute(
        "UPDATE press_releases SET title = ?, description = ?, release_date ="
        " ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (
            request.form["title"],
            request.form["description"],
            request.form["release_date"],
            id,
        ),
    )
    db.commit()
    return redirect(url_for("admin_dashboard"))
  fields = [
      {"name": "title", "label": "Title", "type": "text", "value": item["title"]},
      {
          "name": "description",
          "label": "Description",
          "type": "textarea",
          "value": item["description"],
      },
      {
          "name": "release_date",
          "label": "Release Date",
          "type": "date",
          "value": item["release_date"],
      },
  ]
  return render_template_string(
      FORM_TEMPLATE, action_title="Edit Press Release", fields=fields
  )


@app.route("/admin/press/delete/<int:id>")
def delete_press(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  db = get_db()
  db.execute("DELETE FROM press_releases WHERE id = ?", (id,))
  db.commit()
  return redirect(url_for("admin_dashboard"))


# --- CRUD: MEDIA COVERAGE ---
@app.route("/admin/media/add", methods=["GET", "POST"])
def add_media():
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  if request.method == "POST":
    db = get_db()
    db.execute(
        "INSERT INTO media_coverage (title, url) VALUES (?, ?)",
        (request.form["title"], request.form["url"]),
    )
    db.commit()
    return redirect(url_for("admin_dashboard"))
  fields = [
      {"name": "title", "label": "Title", "type": "text"},
      {
          "name": "url",
          "label": "Media URL (e.g., article link)",
          "type": "text",
      },
  ]
  return render_template_string(
      FORM_TEMPLATE, action_title="Add Media Coverage", fields=fields
  )


@app.route("/admin/media/edit/<int:id>", methods=["GET", "POST"])
def edit_media(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  db = get_db()
  item = db.execute(
      "SELECT * FROM media_coverage WHERE id = ?", (id,)
  ).fetchone()
  if request.method == "POST":
    db.execute(
        "UPDATE media_coverage SET title = ?, url = ?, updated_at ="
        " CURRENT_TIMESTAMP WHERE id = ?",
        (request.form["title"], request.form["url"], id),
    )
    db.commit()
    return redirect(url_for("admin_dashboard"))
  fields = [
      {"name": "title", "label": "Title", "type": "text", "value": item["title"]},
      {"name": "url", "label": "Media URL", "type": "text", "value": item["url"]},
  ]
  return render_template_string(
      FORM_TEMPLATE, action_title="Edit Media Coverage", fields=fields
  )


@app.route("/admin/media/delete/<int:id>")
def delete_media(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  db = get_db()
  db.execute("DELETE FROM media_coverage WHERE id = ?", (id,))
  db.commit()
  return redirect(url_for("admin_dashboard"))


# --- CRUD: IMAGE GALLERY ---
@app.route("/admin/image/add", methods=["GET", "POST"])
def add_image():
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  if request.method == "POST":
    db = get_db()
    db.execute(
        "INSERT INTO image_gallery (image_path, description) VALUES (?, ?)",
        (request.form["image_path"], request.form["description"]),
    )
    db.commit()
    return redirect(url_for("admin_dashboard"))
  fields = [
      {
          "name": "image_path",
          "label": "Image URL or File Path",
          "type": "text",
      },
      {"name": "description", "label": "Description (Optional)", "type": "text"},
  ]
  return render_template_string(
      FORM_TEMPLATE, action_title="Add Image Gallery Item", fields=fields
  )


@app.route("/admin/image/edit/<int:id>", methods=["GET", "POST"])
def edit_image(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  db = get_db()
  item = db.execute("SELECT * FROM image_gallery WHERE id = ?", (id,)).fetchone()
  if request.method == "POST":
    db.execute(
        "UPDATE image_gallery SET image_path = ?, description = ? WHERE id = ?",
        (request.form["image_path"], request.form["description"], id),
    )
    db.commit()
    return redirect(url_for("admin_dashboard"))
  fields = [
      {
          "name": "image_path",
          "label": "Image URL or File Path",
          "type": "text",
          "value": item["image_path"],
      },
      {
          "name": "description",
          "label": "Description",
          "type": "text",
          "value": item["description"],
      },
  ]
  return render_template_string(
      FORM_TEMPLATE, action_title="Edit Image Gallery Item", fields=fields
  )


@app.route("/admin/image/delete/<int:id>")
def delete_image(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  db = get_db()
  db.execute("DELETE FROM image_gallery WHERE id = ?", (id,))
  db.commit()
  return redirect(url_for("admin_dashboard"))


# --- CRUD: VIDEOS ---
@app.route("/admin/video/add", methods=["GET", "POST"])
def add_video():
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  if request.method == "POST":
    db = get_db()
    db.execute(
        "INSERT INTO videos (video_url, description) VALUES (?, ?)",
        (request.form["video_url"], request.form["description"]),
    )
    db.commit()
    return redirect(url_for("admin_dashboard"))
  fields = [
      {"name": "video_url", "label": "Video URL (YouTube link)", "type": "text"},
      {"name": "description", "label": "Description (Optional)", "type": "text"},
  ]
  return render_template_string(
      FORM_TEMPLATE, action_title="Add Video Item", fields=fields
  )


@app.route("/admin/video/edit/<int:id>", methods=["GET", "POST"])
def edit_video(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  db = get_db()
  item = db.execute("SELECT * FROM videos WHERE id = ?", (id,)).fetchone()
  if request.method == "POST":
    db.execute(
        "UPDATE videos SET video_url = ?, description = ? WHERE id = ?",
        (request.form["video_url"], request.form["description"], id),
    )
    db.commit()
    return redirect(url_for("admin_dashboard"))
  fields = [
      {
          "name": "video_url",
          "label": "Video URL",
          "type": "text",
          "value": item["video_url"],
      },
      {
          "name": "description",
          "label": "Description",
          "type": "text",
          "value": item["description"],
      },
  ]
  return render_template_string(
      FORM_TEMPLATE, action_title="Edit Video Item", fields=fields
  )


@app.route("/admin/video/delete/<int:id>")
def delete_video(id):
  if not session.get("logged_in"):
    return redirect(url_for("admin_login"))
  db = get_db()
  db.execute("DELETE FROM videos WHERE id = ?", (id,))
  db.commit()
  return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
  init_db()
  app.run(debug=True, port=5000)