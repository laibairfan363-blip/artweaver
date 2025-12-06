async function signup() {
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const res = await fetch('/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, email, password })
    });
    const data = await res.json();
    alert(data.message || data.error);
}

async function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    const res = await fetch('/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (data.redirect) {
        window.location.href = data.redirect;
    } else {
        alert(data.error);
    }
}

async function postStory() {
    const content = document.getElementById('storyInput').value;
    const title = "Story " + new Date().toLocaleTimeString(); // Simple auto-title for demo

    const res = await fetch('/api/stories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content })
    });
    const data = await res.json();
    if (data.message) {
        document.getElementById('storyInput').value = '';
        loadStories();
    }
}

async function undoStory() {
    const res = await fetch('/api/undo', { method: 'POST' });
    const data = await res.json();
    if (data.content) {
        document.getElementById('storyInput').value = data.content;
    } else {
        alert("Nothing to undo!");
    }
}

async function loadStories() {
    const feed = document.getElementById('feed');
    if (!feed) return;

    const res = await fetch('/api/stories');
    const stories = await res.json();

    feed.innerHTML = '';
    stories.forEach(story => {
        const div = document.createElement('div');
        div.className = 'story-item';
        // Displaying extra details
        div.innerHTML = `<strong>${story.title}</strong><p>${story.content}</p><small>By ${story.author_name || 'Anonymous'}</small>`;
        feed.appendChild(div);
    });
}

// Load stories on dashboard load
if (document.getElementById('feed')) {
    loadStories();
}
