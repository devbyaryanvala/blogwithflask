# app.py

import os
import json
from flask import Flask, render_template, request, redirect, url_for

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
        json.dump(post, file)

# Helper function to load all posts from files
def load_posts():
    posts = []
    for filename in os.listdir(POSTS_DIR):
        if filename.endswith('.json'):
            with open(os.path.join(POSTS_DIR, filename), 'r') as file:
                post = json.load(file)
                posts.append(post)
    return posts

# Mock database
posts = load_posts()

@app.route('/')
def index():
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    post = next((post for post in posts if post['id'] == post_id), None)
    if post:
        return render_template('post.html', post=post)
    return 'Post not found', 404

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_post = {"id": len(posts) + 1, "title": title, "content": content}
        save_post(new_post)
        posts.append(new_post)
        return redirect(url_for('index'))
    return render_template('add_post.html')

@app.route('/delete_post/<int:post_id>', methods=['POST'])
def delete_post(post_id):
    global posts
    posts = [post for post in posts if post['id'] != post_id]
    # Delete post file
    filename = os.path.join(POSTS_DIR, f'post_{post_id}.json')
    if os.path.exists(filename):
        os.remove(filename)
    return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)

