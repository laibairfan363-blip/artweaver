-- Enable UUID extension
create extension if not exists "uuid-ossp";

-- 1. Users Table
create table public.users (
  id uuid primary key default uuid_generate_v4(),
  username text unique not null,
  email text unique,
  password text not null, -- In production, hash this!
  role text check (role in ('writer', 'artist')) not null,
  bio text,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 2. Stories Table
create table public.stories (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  content text not null,
  author_id uuid references public.users(id) not null,
  author_username text not null, -- Cached for performance or join users
  is_premium boolean default false,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 3. Art Table
create table public.art (
  id uuid primary key default uuid_generate_v4(),
  title text not null,
  description text,
  artist_id uuid references public.users(id) not null, -- Assuming logged in artist
  artist_username text not null,
  story_id uuid references public.stories(id), -- Optional link to story
  image_url text, -- Path in Supabase Storage
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- 4. Friends (Graph) Table
-- Initializing as separate rows for bidirectional, or enforce order.
-- Simple approach: bidirectional rows needed for easy querying? 
-- Or just one row per pair. Let's do unique pair.
create table public.friends (
  id uuid primary key default uuid_generate_v4(),
  user_a uuid references public.users(id) not null,
  user_b uuid references public.users(id) not null,
  status text default 'accepted',
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  unique (user_a, user_b)
);

-- 5. Chat Messages Table
create table public.messages (
  id uuid primary key default uuid_generate_v4(),
  sender_id uuid references public.users(id) not null,
  receiver_id uuid references public.users(id) not null,
  content text not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Row Level Security (RLS) - Optional for now but good practice
alter table public.users enable row level security;
alter table public.stories enable row level security;
alter table public.art enable row level security;
alter table public.friends enable row level security;
alter table public.messages enable row level security;

-- Policies (Open for all for demo purposes, restrict in production)
create policy "Public Usage" on public.users for all using (true);
create policy "Public Usage" on public.stories for all using (true);
create policy "Public Usage" on public.art for all using (true);
create policy "Public Usage" on public.friends for all using (true);
create policy "Public Usage" on public.messages for all using (true);
