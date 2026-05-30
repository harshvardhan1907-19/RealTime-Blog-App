# 📝 RealTime BlogApp - A Modern Blog Platform with Real-Time Notifications

![Django](https://img.shields.io/badge/Django-5.2-green)
![Channels](https://img.shields.io/badge/Channels-4.1-blue)
![WebSocket](https://img.shields.io/badge/WebSocket-Ready-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Render](https://img.shields.io/badge/Render-Deployed-success)

A **feature-rich, production-ready blog platform** built with Django that provides **real-time notifications** using WebSockets. Users can create posts, engage with content through likes and comments, follow other users, and receive **instant desktop notifications** when someone interacts with their content.

## 🚀 Live Demo

🔗 **Live Website:** [https://realtime-blog-app.onrender.com](https://realtime-blog-app.onrender.com)

## ✨ Features

### Core Features
- 🔐 **User Authentication** - Register, login, profile management with username/email login
- 📝 **CRUD Operations** - Create, Read, Update, Delete blog posts
- 💬 **Comment System** - Nested comments with replies (Instagram-style flat threading)
- ❤️ **Like System** - Like/unlike posts with real-time updates
- 👥 **Follow System** - Follow/unfollow users (Instagram-style)
- 🏷️ **Categories** - Organize posts by categories
- 🔍 **Search** - Search posts by title or content
- 📸 **Image Upload** - Add images to blog posts with Cloudinary storage

### Real-Time Features (WebSocket)
- 🔔 **Instant Notifications** - Real-time desktop notifications for likes and comments
- 👥 **User-specific notifications** - Each user gets their own notifications via WebSocket groups
- 📬 **Notification Center** - View all notifications with read/unread status
- 💻 **Desktop Alerts** - Browser notifications with click-to-mark-read functionality

### UI/UX Features
- 🎨 **Modern Design** - Clean, responsive interface with gradient accents
- 📱 **Mobile Responsive** - Fully responsive design that works on all devices
- 🖼️ **Image Modal** - Click profile pictures to view enlarged version
- ♾️ **Infinite Scroll** - Smooth infinite scroll pagination with filter/sort persistence
- 🔄 **Real-time Filters** - Filter by category, search, sort by newest/views/likes without page reload
- 👤 **User Profiles** - Custom profile pictures with WhatsApp-style avatars

### Technical Highlights
- ⚡ **WebSocket Integration** - Django Channels for real-time communication
- 🗄️ **PostgreSQL Database** - Production-ready database on Render
- ☁️ **Cloudinary Storage** - Persistent image storage with CDN delivery
- 🔄 **REST API** - Ready for mobile app integration
- 🛡️ **Security** - CSRF protection, secure cookies, production-ready settings

## 🛠️ Tech Stack

| Technology | Purpose |
|------------|---------|
| **Django 5.2** | Backend Framework |
| **Django Channels** | WebSocket Support |
| **Daphne** | ASGI Server for WebSockets |
| **PostgreSQL** | Production Database |
| **Cloudinary** | Image Storage & CDN |
| **Bootstrap 5** | Frontend UI Framework |
| **JavaScript (Vanilla)** | Frontend interactivity, infinite scroll, WebSocket client |
| **Render** | Cloud Deployment |
| **GitHub** | Version Control |

## 📸 Screenshots

### Homepage with Modern Grid Layout
![Homepage](https://github.com/user-attachments/assets/273b004b-d6a1-4486-9425-8a231d69ebd4)

### Real-time Notification
![Notification](https://github.com/user-attachments/assets/d974ab64-6476-4102-afd5-52f4ffc3271c)

### User Profile with Follow System
![Profile](https://github.com/user-attachments/assets/d0960718-5211-4c59-85fa-a7f8320c47e0)

### Post Detail with Comments
![Post Detail](https://github.com/user-attachments/assets/de6b69b9-af37-48cf-ace1-af5345a12608)

## 🏗️ Project Structure

blog_project/
├── blogapp/ # Main application
│ ├── static/ # Static files (CSS, JS, images)
│ │ ├── css/
│ │ ├── js/
│ │ └── images/
│ ├── templates/ # HTML templates
│ │ └── blog/
│ ├── migrations/ # Database migrations
│ ├── models.py # Database models
│ ├── views.py # View logic
│ ├── consumers.py # WebSocket consumers
│ ├── routing.py # WebSocket URL routing
│ ├── forms.py # Custom forms
│ ├── backends.py # Custom authentication backend
│ └── context_processors.py # Global context
├── blogproject/ # Project configuration
│ ├── settings.py # Django settings
│ ├── urls.py # URL configuration
│ └── asgi.py # ASGI config for WebSockets
├── staticfiles/ # Collected static files (production)
├── media/ # User-uploaded media (local development)
├── manage.py # Django management script
├── requirements.txt # Python dependencies
└── runtime.txt # Python version specification


## 📊 Database Schema

- **User** - Django's built-in User model
- **Profile** - Extended user profile with bio, profile picture, followers
- **Post** - Blog posts with title, content, image, category, likes, views
- **Comment** - Nested comments with parent-child relationship
- **Notification** - User notifications with read/unread status
- **Category** - Post categories
- **Follow** - User follow relationships (via ManyToMany)

## 🚀 Installation

### Prerequisites
- Python 3.11+
- pip
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the repository**
```bash
git clone https://github.com/harshvardhan1907-19/RealTime-Blog-App.git
cd RealTime-Blog-App

2. Create virtual environment
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate

3. Install dependencies
pip install -r requirements.txt

4. Set up environment variables
# Create .env file
echo "DATABASE_URL=sqlite:///db.sqlite3" > .env

5. Create superuser
python manage.py createsuperuser

6. Run Development server
python -m daphne blogproject.asgi:application
