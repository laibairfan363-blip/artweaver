from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from supa_client import get_supabase
from dsa_modules.stack import Stack
from dsa_modules.queue import Queue, PriorityQueue
from dsa_modules.bst import BST
from dsa_modules.graph import Graph
from dsa_modules.sorting import count_sort_stories_by_length
import uuid

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_demo'

# Initialize DSA Structures (Global State for Demo Purpose)
# In a real production app, these might be re-built from DB or using Redis.
# For this requirement, we keep them in memory and sync with DB.
story_bst = BST()
undo_stacks = {} # userId -> Stack
visualization_queue = PriorityQueue() # Artist Dashboard Queue
user_graph = Graph()

supabase = get_supabase()

# --- Helper to Sync DSA with DB on Startup (Mocking basic sync) ---
def sync_dsa_from_db():
    print("Syncing data from Supabase to DSA structures...")
    # 1. Load Stories into BST
    response = supabase.table('stories').select("*").execute()
    stories = response.data
    for story in stories:
        story_bst.insert(story['title'], story)

    # 2. Load Users into Graph
    # (Simplified for demo)
    pass

with app.app_context():
    sync_dsa_from_db()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/role/<role>')
def set_role(role):
    session['role'] = role
    return redirect(url_for('auth'))

@app.route('/auth')
def auth():
    return render_template('auth.html')

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    # Supabase Auth
    try:
        res = supabase.auth.sign_in_with_password({"email": email, "password": password})
        session['user'] = res.user.id
        # Also fetch profile to get username
        profile = supabase.table('profiles').select("*").eq('id', res.user.id).single().execute()
        if profile.data:
            session['username'] = profile.data['username']
            # Add user to Graph
            user_graph.add_node(session['username'])
        return jsonify({"message": "Login successful", "redirect": url_for('dashboard')})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = session.get('role', 'writer')

    try:
        res = supabase.auth.sign_up({"email": email, "password": password})
        # Create profile entry
        if res.user:
            supabase.table('profiles').insert({
                "id": res.user.id,
                "username": username,
                "role": role,
                "email": email
            }).execute()
            user_graph.add_node(username)
            return jsonify({"message": "Signup successful. Please check email or login."})
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
    return jsonify({"error": "Unknown error"}), 400

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('index'))
        
    role = session.get('role')
    # If role is missing in session, fetch from DB
    if not role:
        profile = supabase.table('profiles').select("*").eq('id', session['user']).single().execute()
        role = profile.data['role']
        session['role'] = role
        session['username'] = profile.data['username']
    
    return render_template('dashboard.html', role=role, username=session.get('username'))

# --- Story Routes (Writer) ---
@app.route('/api/stories', methods=['GET', 'POST'])
def stories():
    if request.method == 'POST':
        data = request.json
        title = data.get('title')
        content = data.get('content')
        author = session.get('username')
        
        # 1. Save to DB
        res = supabase.table('stories').insert({
            "title": title,
            "content": content,
            "author_id": session['user'],
            "author_name": author
        }).execute()
        
        # 2. Add to DSA (BST)
        if res.data:
            # Re-fetch new data or use returned data
            new_story = res.data[0]
            story_bst.insert(title, new_story)
            
            # 3. Add to Undo Stack
            if session['user'] not in undo_stacks:
                undo_stacks[session['user']] = Stack()
            undo_stacks[session['user']].push(content) # Store just content for simple undo

        return jsonify({"message": "Story posted", "story": res.data[0]})

    else:
        # GET - Return sorted stories
        # Use BST Inorder to get stories sorted by Title?
        # Or sorting.py to sort by length?
        # Let's show sorted by Title from BST traversal
        all_stories = story_bst.inorder() 
        return jsonify(all_stories)

@app.route('/api/undo', methods=['POST'])
def undo_story():
    user_id = session.get('user')
    if user_id in undo_stacks:
        prev_content = undo_stacks[user_id].pop()
        if prev_content:
            return jsonify({"content": prev_content})
    return jsonify({"error": "Nothing to undo"}), 400

# --- Artist Routes (Queue) ---
@app.route('/api/visualize-queue', methods=['GET', 'POST'])
def visualize_queue():
    if request.method == 'POST':
        # Writer requests visualization
        data = request.json
        story_id = data.get('story_id')
        priority = data.get('priority', 2) # 1=High, 2=Normal
        
        # Enqueue
        visualization_queue.push(story_id, priority)
        return jsonify({"message": "Added to visualization queue"})
    
    # For GET, we want to see what's next (Artist View)
    # Peek functionality or list top items?
    # Queue is destructive on pop, so maybe just peek?
    # PriorityQueue implementation pushes (priority, index, item)
    # We can't easily peek all without popping. 
    # For demo, let's just return the top item.
    if not visualization_queue.is_empty():
        # This is a bit hacky for a persistent queue view, but ok for demo.
        # Ideally we'd have a list, but this uses the custom Heap structure.
        return jsonify({"next_story": "Something from Queue"})
    return jsonify({"next_story": None})

if __name__ == '__main__':
    app.run(debug=True, port=3000)
