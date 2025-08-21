# 3DS Discord Homebrew

## Overview

3DS Discord is a native homebrew chat application for Nintendo 3DS/2DS consoles. The application provides a Discord-like chat experience with multiple rooms, real-time messaging, and user presence tracking. It's built with C using libctru and includes both a native 3DS client and a Flask web server backend for data synchronization.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Lightweight HTML/CSS/JS**: Designed for compatibility with the 3DS browser's limited capabilities
- **Polling-based Updates**: Uses XMLHttpRequest with 3-second intervals instead of WebSockets due to 3DS browser limitations
- **Responsive Design**: Optimized for 400px width screens typical of 3DS devices
- **No Modern JavaScript**: Avoids ES6+ features and modern APIs for maximum compatibility

### Backend Architecture
- **Flask Web Framework**: Full-featured web framework with PostgreSQL database integration
- **User Authentication**: Complete registration/login system with password hashing
- **PostgreSQL Database**: Persistent storage for users, messages, rooms, and relationships
- **REST API**: JSON endpoints for native 3DS homebrew communication

### Data Management
- **Room System**: Dynamic chat rooms with database persistence and member management
- **User Presence**: Online/offline status tracking with last seen timestamps
- **Message Structure**: Rich messages with user references, timestamps, and room associations
- **Database Persistence**: Full PostgreSQL schema with proper relationships and constraints

### Authentication & Authorization
- **Complete User System**: Registration with username, email, and secure password hashing
- **Session Management**: Flask-Login for secure user session management
- **Friends System**: User relationships, friend requests, and private messaging
- **Room Permissions**: Public/private rooms with member management

## External Dependencies

### Python Packages (Web Server)
- **Flask**: Core web framework for routing, templating, and session management
- **PostgreSQL**: Database for user accounts, messages, and room data
- **Flask-SQLAlchemy**: ORM for database operations
- **Flask-Login**: User session management

### Native 3DS Homebrew (C/libctru)
- **libctru**: Core Nintendo 3DS development library
- **No External Dependencies**: Current version works offline with demo data
- **Future Network Support**: Will use libcurl and json-c for server communication

### Infrastructure
- **PostgreSQL Database**: Full-featured database for web and API
- **REST API Endpoints**: JSON API for homebrew communication
- **Session-based Web Auth**: Flask sessions for web interface
- **Hybrid Architecture**: Web interface + native 3DS client