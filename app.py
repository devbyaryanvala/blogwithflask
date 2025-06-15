# app.py

import os
import json
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime

app = Flask(__name__)

POSTS_DIR = 'posts/'

# Ensure posts directory exists
if not os.path.exists(POSTS_DIR):
    os.makedirs(POSTS_DIR)

# Helper function to save a post to a file
def save_post(post):
    post_id = str(post['id'])
    filename = os.path.join(POSTS_DIR, f'post_{post_id}.json')
    with open(filename, 'w') as file:
        json.dump(post, file, indent=4) # Added indent for readability

# Helper function to load all posts from files
def load_posts():
    posts = []
    # Ensure posts are sorted by ID or timestamp if available
    filenames = sorted(os.listdir(POSTS_DIR))
    for filename in filenames:
        if filename.endswith('.json'):
            with open(os.path.join(POSTS_DIR, filename), 'r') as file:
                try:
                    post = json.load(file)
                    posts.append(post)
                except json.JSONDecodeError:
                    print(f"Error decoding JSON from {filename}")
    # Sort posts by ID to maintain consistent order
    return sorted(posts, key=lambda p: p.get('id', 0))

# Mock database (load posts on startup)
posts = load_posts()
# Ensure IDs are sequential and unique, especially after deletions
if not posts:
    next_id = 1
else:
    next_id = max(post.get('id', 0) for post in posts) + 1


@app.route('/')
def index():
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = next((p for p in posts if p.get('id') == post_id), None)
    if post:
        return render_template('post.html', post=post)
    return 'Post not found', 404

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    global next_id # Use global next_id
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_post = {"id": next_id, "title": title, "content": content, "timestamp": current_time}
        save_post(new_post)
        posts.append(new_post)
        next_id += 1 # Increment for the next post
        return redirect(url_for('index'))
    return render_template('add_post.html')

@app.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
def edit_post(post_id):
    post_to_edit = next((p for p in posts if p.get('id') == post_id), None)
    if not post_to_edit:
        return 'Post not found', 404

    if request.method == 'POST':
        post_to_edit['title'] = request.form['title']
        post_to_edit['content'] = request.form['content']
        # Optionally update timestamp for edits, or keep original
        # post_to_edit['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_post(post_to_edit) # Save the updated post to its file
        return redirect(url_for('post', post_id=post_id))
    
    return render_template('edit_post.html', post=post_to_edit)


@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    global posts
    original_len = len(posts)
    posts = [post for post in posts if post.get('id') != post_id]
    
    if len(posts) < original_len: # Check if a post was actually removed
        # Delete post file
        filename = os.path.join(POSTS_DIR, f'post_{post_id}.json')
        if os.path.exists(filename):
            os.remove(filename)
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)