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
![Homepage](screenshots/homepage.png)

### Real-time Notification
![Notification](screenshots/notification.png)

### User Profile with Follow System
![Profile](screenshots/profile.png)

### Post Detail with Comments
![Post Detail](screenshots/post-detail.png)

## 🏗️ Project Structure
