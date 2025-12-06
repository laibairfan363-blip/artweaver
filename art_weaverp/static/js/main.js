
// main.js

// --- Utility Functions ---
function showElement(id) {
    const el = document.getElementById(id);
    if (el) el.classList.remove('hidden');
}

function hideElement(id) {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
}

// --- Profile Logic ---
async function saveProfile() {
    const bio = document.getElementById('pBio').value;

    try {
        const res = await fetch('/profile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ bio })
        });
        const data = await res.json();
        alert(data.message);
    } catch (err) {
        console.error(err);
        alert('Error saving profile');
    }
}

// --- Navigation & Role Selection ---
function showRoleSelection() {
    hideElement('landing');
    showElement('role-selection');
}

function hideRoleSelection() {
    hideElement('role-selection');
    showElement('landing');
}

function showSignup(role) {
    // Set role in hidden input
    document.getElementById('selectedRole').value = role;
    hideElement('role-selection');
    showElement('signup-form');
    // Default to Signup mode
    toggleAuth('signup');
}

function toggleAuth(mode) {
    const title = document.querySelector('#signup-form h1');
    const emailInput = document.getElementById('email');
    const authMode = document.getElementById('authMode');

    authMode.value = mode;

    if (mode === 'login') {
        title.innerText = 'Log In';
        emailInput.style.display = 'none';
        emailInput.required = false;
    } else {
        title.innerText = 'Sign Up';
        emailInput.style.display = 'block';
        emailInput.required = true;
    }
}

// --- Auth Handling ---
async function handleAuth(event) {
    event.preventDefault();
    const mode = document.getElementById('authMode').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;
    const role = document.getElementById('selectedRole').value;

    const endpoint = mode === 'login' ? '/login' : '/signup';
    const payload = mode === 'login'
        ? { username, password }
        : { username, email, password, role };

    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.status === 'success') {
            window.location.href = '/home';
        } else {
            alert(data.message || 'Authentication failed');
        }
    } catch (err) {
        console.error(err);
        alert('An error occurred');
    }
}

// --- Home Dashboard Logic ---

// Fetch functions to populate feeds
async function loadWriterFeed() {
    try {
        const res = await fetch('/api/stories');
        const stories = await res.json();
        const feed = document.getElementById('feed');
        if (!feed) return;

        feed.innerHTML = '';
        stories.forEach(story => {
            const div = document.createElement('div');
            div.className = 'feed-item';
            div.innerHTML = `<h3>${story.title}</h3><p>${story.content}</p><small>By ${story.author}</small>`;
            feed.appendChild(div);
        });

    } catch (err) {
        console.error("Error loading feed:", err);
    }
}

async function loadArtistQueue() {
    try {
        const res = await fetch('/api/art/queue');
        const tasks = await res.json();
        const queueDiv = document.getElementById('taskQueue');
        const select = document.getElementById('storySelect');

        if (!queueDiv) return;

        queueDiv.innerHTML = '';
        select.innerHTML = '<option value="">Select a Story to Visualize</option>';

        if (tasks.length === 0) {
            queueDiv.innerHTML = 'No stories pending visualization.';
            return;
        }

        tasks.forEach(task => {
            const story = task.story;
            // Add to visualization queue list
            const div = document.createElement('div');
            div.className = 'feed-item';
            div.style.borderLeft = task.type === 'premium' ? '5px solid gold' : '5px solid #ccc';
            div.innerHTML = `<strong>${story.title}</strong> (${task.type})<br>${story.content.substring(0, 50)}...<br><small>Author: ${story.author}</small>`;
            queueDiv.appendChild(div);

            // Add to dropdown
            const opt = document.createElement('option');
            opt.value = story.id;
            opt.setAttribute('data-author-id', story.author_id);
            opt.innerText = story.title;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error("Error loading queue:", err);
    }
}

async function loadGraph() {
    try {
        const res = await fetch('/api/graph');
        const graph = await res.json();
        const div = document.getElementById('graphView');
        if (!div) return;

        let html = '<ul style="list-style:none; padding-left:0;">';
        for (const [user, connections] of Object.entries(graph)) {
            if (connections.length > 0) {
                html += `<li><strong>${user}</strong> is connected to: ${connections.join(', ')}</li>`;
            } else {
                html += `<li><strong>${user}</strong> has no connections yet.</li>`;
            }
        }
        html += '</ul>';
        div.innerHTML = html;
    } catch (err) {
        console.error(err);
    }
}

async function postStory(e) {
    e.preventDefault();
    const title = document.getElementById('storyTitle').value;
    const content = document.getElementById('storyInput').value;
    const isPremium = document.getElementById('isPremium').checked;

    const res = await fetch('/api/story/post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, is_premium: isPremium })
    });
    const data = await res.json();
    alert(data.message);
    loadWriterFeed(); // Refresh
}

async function undoStory() {
    const res = await fetch('/api/story/undo', { method: 'POST' });
    const data = await res.json();
    if (data.status === 'success') {
        alert('Undid: ' + data.restored.title);
        loadWriterFeed();
    } else {
        alert(data.message);
    }
}

async function postArt(e) {
    e.preventDefault();
    const select = document.getElementById('storySelect');
    const storyId = select.value;
    const authorId = select.options[select.selectedIndex].getAttribute('data-author-id');
    const title = document.getElementById('artTitle').value;
    const desc = document.getElementById('artDesc').value;
    const fileInput = document.getElementById('artFile');

    if (!storyId) {
        alert("Please select a story to visualize!");
        return;
    }

    const formData = new FormData();
    formData.append('story_id', storyId);
    formData.append('story_author_id', authorId);
    formData.append('title', title);
    formData.append('description', desc);
    if (fileInput && fileInput.files[0]) {
        formData.append('file', fileInput.files[0]);
    }

    const res = await fetch('/api/art/post', {
        method: 'POST',
        body: formData // No Content-Type header when sending FormData
    });
    const data = await res.json();
    alert(data.message);
    // Refresh queue and graph
    loadArtistQueue();
    loadGraph();
}

// --- Initialization ---
document.addEventListener('DOMContentLoaded', () => {
    // If we are on home page
    if (document.getElementById('home')) {
        // Check role based on content presence
        if (document.getElementById('storyTitle')) {
            // Writer
            loadWriterFeed();
        } else {
            // Artist
            loadArtistQueue();
        }
        loadGraph();
    }
});
