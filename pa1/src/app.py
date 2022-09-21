import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

posts = {
    "posts": [
        {
            "id": 0,
            "upvotes": 1,
            "title": "My cat is the cutest!",
            "link": "https://i.imgur.com/jseZqNK.jpg",
            "username": "alicia98",
            "comments": [
                {
                    "id": 0,
                    "upvotes": 8,
                    "text": "that is a hot cat",
                    "username": "dave69",
                },
                {
                    "id": 1,
                    "upvotes": 4,
                    "text": "ur fat",
                    "username": "bob420",
                },
            ],
        },
        {
            "id": 1,
            "upvotes": 3,
            "title": "Cat loaf",
            "link": "https://i.imgur.com/TJ46wX4.jpg",
            "username": "alicia98",
            "comments": [
                {
                    "id": 2,
                    "upvotes": 1,
                    "text": "I don't get it",
                    "username": "daquavis_pikachu",
                }
            ],
        },
    ],
}

post_id_counter = 2
comment_id_counter = 3


@app.route("/")
def hello_world():
    return "Hello world!"


# your routes here
@app.route("/api/posts/")
def get_posts():
    return json.dumps({
        "success": True,
        "data": posts,
    }), 200


@app.route("/api/posts/", methods=["POST"])
def create_post():
    global post_id_counter
    body = json.loads(request.data)
    if not body:
        return json.dumps({"success": False, "error": "no body"}), 400
    title, link, username = body.get("title"), body.get("link"), body.get("username")
    if not (title and link and username):
        return json.dumps({"success": False, "error": "missing field"}), 400
    post = {
        "id": post_id_counter,
        "upvotes": 0,
        "title": title,
        "link": link,
        "username": username,
        "comments": [],
    }
    posts["posts"].append(post)
    post_id_counter += 1
    return json.dumps({"success": True, "data": post}), 201


@app.route("/api/posts/<int:post_id>")
def get_specific_post(post_id):
    post = None
    try:
        post = posts["posts"][post_id]
    except:
        return json.dumps({"success": False, "error": f"No post with id {post_id}"}), 404
    return json.dumps({"success": True, "data": post}), 200


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    post = None
    for i,p in enumerate(posts["posts"]):
        if p["id"] == post_id:
            post = posts["posts"].pop(i)
    if not post:
        return json.dumps({"success": False, "error": "Post not found"}), 404
    return json.dumps({"success": True, "data": post}), 200


@app.route("/api/posts/<int:post_id>/comments")
def get_comments(post_id):
    post = json.loads(get_specific_post(post_id)[0])
    if not post["success"]:
        return json.dumps(post), 404
    print(json.dumps(post))
    return json.dumps({"success": True, "data": post["data"]["comments"]}), 200


@app.route("/api/posts/<int:post_id>/comments", methods=["POST"])
def post_comment(post_id):
    global comment_id_counter
    body = json.loads(request.data)
    if not body:
        return json.dumps({"success": False, "error": "no body"}), 400
    text, username = body.get("text"), body.get("username")
    if not (text and username):
        return json.dumps({"success": False, "error": "missing field"}), 400

    index = -1
    for i,p in enumerate(posts["posts"]):
        if p["id"] == post_id:
            index = i
            break
    if index == -1:
        return json.dumps({"success": False, "error": "Post not found"}), 404
    
    comment = {
        "id": comment_id_counter,
        "text": text,
        "upvotes": 0,
        "username": username,
    }
    comment_id_counter += 1

    posts["posts"][index]["comments"].append(comment)
    return json.dumps({"success": True, "data": comment}), 201


@app.route("/api/posts/<int:post_id>/comments/<int:comment_id>", methods=["POST"])
def edit_comment(post_id, comment_id):
    body = json.loads(request.data)
    if not body:
        return json.dumps({"success": False, "error": "no body"}), 400
    text = body.get("text")
    if not text:
        return json.dumps({"success": False, "error": "missing field"}), 400
    
    post_index = -1
    for i,p in enumerate(posts["posts"]):
        if p["id"] == post_id:
            post_index = i
            break
    if post_index == -1:
        return json.dumps({"success": False, "error": "Post not found"}), 404
    
    comment_index = -1
    for i,c in enumerate(posts["posts"][post_index]["comments"]):
        if c["id"] == comment_id:
            comment_index = i
            break
    if comment_index == -1:
        return json.dumps({"success": False, "error": "Comment not found"}), 404

    posts["posts"][post_index]["comments"][comment_index]["text"] = f"{posts['posts'][post_index]['comments'][comment_index]['text']} (edit): {text}"
    return json.dumps({"success": True, "data": posts["posts"][post_index]["comments"][comment_index]["text"]}), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
