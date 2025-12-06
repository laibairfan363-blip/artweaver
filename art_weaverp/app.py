from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from DSA.Stack import Stack
from DSA.Queue import Queue, CircularQueue, PriorityQueue
from DSA.Tree import BinarySearchTree
from DSA.Graph import Graph
from DSA.Heap import MaxHeap
import os
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = 'super_secret_key_art_weaver' # In prod, use env var
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Supabase Configuration ---
# TODO: USER MUST FILL THESE IN
SUPABASE_URL = "https://oocmlrpsbdjobiphlsoa.supabase.co"
SUPABASE_KEY = "sb_secret_bFei65IdfLZN3nnkXxLZ0w_JEXCFvUu"

# Initialize Client safely
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Supabase client initialized.")
except Exception as e:
    print(f"Warning: Supabase not initialized. Please set credentials. Error: {e}")
    supabase = None

# --- Global DSA Instances (Hydrated from DB) ---
# We keep these instances to satisfy DSA requirements (BST Search, Graph, etc.)
stories_bst = BinarySearchTree()
undo_stacks = {} 
visualization_queue = Queue() 
priority_queue = PriorityQueue()
artist_scaling_queue = CircularQueue(5)
user_graph = Graph()
top_artists_heap = MaxHeap()

# --- Helper: Sync Functions ---
def sync_data():
    """Fetches data from DB and rebuilds DSAs."""
    if not supabase: return
    
    # 1. Sync Stories to BST
    try:
        res = supabase.table('stories').select("*").execute()
        # Reset BST
        global stories_bst
        stories_bst = BinarySearchTree()
        for s in res.data:
            stories_bst.insert(s['title'], s)
    except Exception as e:
        print(f"Error syncing stories: {e}")

    # 2. Sync Friends to Graph
    try:
        res = supabase.table('friends').select("*").execute()
        global user_graph
        user_graph = Graph()
        for f in res.data:
            user_graph.add_edge(f['user_a'], f['user_b'])
            user_graph.add_edge(f['user_b'], f['user_a']) # Bidirectional
    except Exception as e:
        print(f"Error syncing friends: {e}")

# Call data sync on startup
# sync_data() # Need valid keys first

# --- Routes ---

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if supabase:
        try:
            res = supabase.table('users').select("*").eq("username", username).eq("password", password).execute()
            if res.data and len(res.data) > 0:
                user = res.data[0]
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                # Initialize Stack for writer
                if user['role'] == 'writer':
                    undo_stacks[user['id']] = Stack()
                return jsonify({'status': 'success', 'role': user['role']})
        except Exception as e:
            print(e)
            return jsonify({'status': 'error', 'message': 'DB Error'}), 500
            
    return jsonify({'status': 'error', 'message': 'Invalid credentials or DB not connected'}), 401

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role') 
    
    if supabase:
        try:
            # Check exist
            check = supabase.table('users').select("*").eq("username", username).execute()
            if check.data:
                 return jsonify({'status': 'error', 'message': 'User exists'}), 400
            
            # Insert
            res = supabase.table('users').insert({
                "username": username,
                "email": email,
                "password": password, 
                "role": role,
                "bio": ""
            }).execute()
            
            user = res.data[0]
            session['user_id'] = user['id']
            session['username'] = username
            session['role'] = role
            
            if role == 'writer':
                undo_stacks[user['id']] = Stack()
            user_graph.add_node(user['id'])
            
            return jsonify({'status': 'success'})
        except Exception as e:
            print(e)
            return jsonify({'status': 'error', 'message': str(e)}), 400

    return jsonify({'status': 'error', 'message': 'DB Not Configured'}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('landing'))
    # Sync DSA on home load to be sure
    sync_data() 
    return render_template('home.html', role=session['role'], username=session['username'])

@app.route('/api/story/post', methods=['POST'])
def post_story():
    if 'user_id' not in session or session['role'] != 'writer':
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403
    
    data = request.json
    title = data.get('title')
    content = data.get('content')
    is_premium = data.get('is_premium', False)
    
    if supabase:
        try:
            res = supabase.table('stories').insert({
                "title": title,
                "content": content,
                "author_id": session['user_id'],
                "author_username": session['username'],
                "is_premium": is_premium
            }).execute()
            
            story = res.data[0]
            
            # DSA: Insert into BST
            stories_bst.insert(title, story)
            
            # Queue
            if is_premium:
                priority_queue.enqueue(story, 10)
            else:
                visualization_queue.enqueue(story)
                
            # Stack
            if session['user_id'] not in undo_stacks:
                undo_stacks[session['user_id']] = Stack()
            undo_stacks[session['user_id']].push(story)

            return jsonify({'status': 'success', 'message': 'Story posted!'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'error'}), 500

@app.route('/api/story/undo', methods=['POST'])
def undo_story():
    # Only stack undo from session memory (DB doesn't support 'undo' easily without timestamps/active flag)
    # We will simulate "Undo" by deleting the last story from DB if it matches stack top
    user_id = session.get('user_id')
    if user_id in undo_stacks:
        prev_story = undo_stacks[user_id].pop()
        if prev_story and supabase:
            # Delete from DB
            supabase.table('stories').delete().eq('id', prev_story['id']).execute()
            # Remove from BST? BST lookup by key? 
            # Re-syncing is easier.
            sync_data()
            return jsonify({'status': 'success', 'restored': prev_story})
            
    return jsonify({'status': 'error', 'message': 'Nothing to undo'})

@app.route('/api/stories', methods=['GET'])
def get_stories():
    # Use BST inorder traversal (Requirement)
    sync_data() 
    stories = stories_bst.inorder_traversal()
    return jsonify(stories)

@app.route('/api/art/queue', methods=['GET'])
def get_art_queue():
    if session.get('role') != 'artist': return jsonify({'status': 'error'}), 403
    # Use In-Memory Queue (Assuming transient queue for now, or we could fetch un-visualized stories from DB)
    # For simplicity, respecting the requirement "Use Queue", we rely on the memory queue populated during post_story
    # But if server restarts, queue is empty.
    # Ideally, we should fetch stories where 'has_art' is false? 
    # Let's keep the existing memory queue logic for "Viz Queue" to strictly verify "Queue" data structure usage.
    
    tasks = []
    pq_items = priority_queue.get_all()
    tasks.extend([{'type': 'premium', 'story': s} for s in pq_items])
    q_items = visualization_queue.get_all()
    tasks.extend([{'type': 'normal', 'story': s} for s in q_items])
    return jsonify(tasks)

@app.route('/api/art/post', methods=['POST'])
def post_art():
    if session.get('role') != 'artist': return jsonify({'status': 'error'}), 403

    art_title = request.form.get('title')
    art_desc = request.form.get('description')
    story_id = request.form.get('story_id')
    story_author_id = request.form.get('story_author_id')
    file = request.files.get('file')
    
    filename = ''
    if file:
        filename = secure_filename(file.filename)
        filename = f"{uuid.uuid4().hex}_{filename}"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
    if supabase:
        try:
             supabase.table('art').insert({
                 "title": art_title,
                 "description": art_desc,
                 "artist_id": session['user_id'],
                 "artist_username": session['username'],
                 "story_id": story_id,
                 "image_url": filename # Storing filename, serving via static
             }).execute()
             
             # Friends connect
             if story_author_id:
                 add_friend_logic(session['user_id'], story_author_id)
                 
             return jsonify({'status': 'success', 'message': 'Art posted!'})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'error'}), 500

@app.route('/api/art/all', methods=['GET'])
def get_all_art():
    if supabase:
        try:
            res = supabase.table('art').select("*").execute()
            # Map 'image_url' to frontend expected 'image'
            data = []
            for item in res.data:
                item['image'] = item['image_url']
                item['artist'] = item['artist_username'] # map for frontend
                # fetch story title if needed, or join. 
                item['story_title'] = "Linked Story"
                data.append(item)
            return jsonify(data)
        except: return jsonify([])
    return jsonify([])

# --- Friends & Chat ---

def add_friend_logic(uid1, uid2):
    if not supabase: return
    # Insert both directions if not exist
    try:
        supabase.table('friends').upsert([
            {"user_a": uid1, "user_b": uid2},
            {"user_a": uid2, "user_b": uid1}
        ]).execute()
        sync_data()
    except Exception as e: print(e)

@app.route('/api/friends/add', methods=['POST'])
def add_friend():
    target_username = request.json.get('username')
    
    # Needs target ID.
    if supabase:
        res = supabase.table('users').select("id").eq("username", target_username).execute()
        if res.data:
            target_id = res.data[0]['id']
            add_friend_logic(session['user_id'], target_id)
            return jsonify({'status': 'success', 'message': f'Added {target_username}'})
    return jsonify({'status': 'error', 'message': 'User not found'})

@app.route('/api/friends', methods=['GET'])
def get_friends():
    sync_data()
    friend_ids = user_graph.get_connections(session['user_id'])
    
    # Resolve IDs to names
    friends = []
    if supabase and friend_ids:
        # DB lookup 'in'
        # Supabase-py doesn't support 'in' easily in one line without filters builder, let's loop or fetch all friends
        # Easier: fetch friends table for this user with join?
        # Simpler: We have names in the graph? No, only IDs.
        # Fetch all users? cache?
        # Let's just fetch individual names for now (N+1 but simple code)
        for fid in friend_ids:
            u = supabase.table('users').select("username").eq("id", fid).execute()
            if u.data:
                friends.append({'username': u.data[0]['username'], 'id': fid})
    return jsonify(friends)

@app.route('/api/chat/send', methods=['POST'])
def send_msg():
    data = request.json
    friend_id = data.get('friend_id')
    msg = data.get('message')
    
    if supabase:
        supabase.table('messages').insert({
            "sender_id": session['user_id'],
            "receiver_id": friend_id,
            "content": msg
        }).execute()
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'})

@app.route('/api/chat/history', methods=['GET'])
def get_chat():
    friend_id = request.args.get('friend_id')
    user_id = session['user_id']
    
    if supabase:
        # sender=me & receiver=friend OR sender=friend & receiver=me
        res = supabase.table('messages').select("*").or_(f"and(sender_id.eq.{user_id},receiver_id.eq.{friend_id}),and(sender_id.eq.{friend_id},receiver_id.eq.{user_id})").order("created_at").execute()
        
        # map to frontend format
        msgs = []
        for m in res.data:
            # Need sender name
            # Optimization: pass current user name and friend name from frontend to save lookups
            # Or simplified: just show "You" and "Friend" or lookup
            # Let's trust frontend or return sender ID
            # Frontend main.js expects 'sender' name.
            # We can cache names?
            s_name = "You" if m['sender_id'] == user_id else "Friend" # Simplified
            # Actually we can do better if we have user session name
            if m['sender_id'] == user_id: s_name = session['username']
            # else we can't easily get friend name without lookup.
            # but getting friend name from Friend ID is a look up.
            
            msgs.append({
                'sender': s_name, 
                'message': m['content'],
                'time': m['created_at'] # format this?
            })
        return jsonify(msgs)
    return jsonify([])

@app.route('/api/graph', methods=['GET'])
def view_graph():
    # Return graph connections from user_graph (Sync'd from DB)
    readable = {}
    # Graph contains IDs. We need Names.
    # This view is slow if we query DB for every node.
    # Only show current user's graph? 
    # Or just return IDs?
    # Let's return IDs for now, frontend might show IDs.
    # To fix, we should cache {id: name} map.
    return jsonify(user_graph.adj_list)

@app.route('/blogs')
def blogs():
    return render_template('blogs.html')

@app.route('/gallery')
def gallery():
    return render_template('gallery.html')

@app.route('/chat')
def chat_page():
    if 'user_id' not in session: return redirect(url_for('landing'))
    return render_template('chat.html', username=session['username'])

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('landing'))
        
    if request.method == 'POST':
        if supabase:
            supabase.table('users').update({"bio": request.json.get('bio')}).eq("id", session['user_id']).execute()
            return jsonify({'status': 'success', 'message': 'Profile updated!'})
            
    # Fetch user
    if supabase:
        res = supabase.table('users').select("*").eq("id", session['user_id']).execute()
        if res.data:
            return render_template('profile.html', user=res.data[0])
            
    return "Error loading profile"

@app.route('/about')
def about(): return render_template('about.html')

@app.route('/rules')
def rules(): return render_template('rules.html')

@app.route('/contact')
def contact(): return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
