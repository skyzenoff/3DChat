# 3DS Discord

## Overview

3DS Discord is a lightweight chat application specifically optimized for Nintendo 3DS/2DS browsers. The application provides a Discord-like chat experience with multiple rooms, real-time messaging, and user presence tracking. It's built with Flask and uses in-memory storage to maintain simplicity and reduce resource usage on the constrained 3DS hardware.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Lightweight HTML/CSS/JS**: Designed for compatibility with the 3DS browser's limited capabilities
- **Polling-based Updates**: Uses XMLHttpRequest with 3-second intervals instead of WebSockets due to 3DS browser limitations
- **Responsive Design**: Optimized for 400px width screens typical of 3DS devices
- **No Modern JavaScript**: Avoids ES6+ features and modern APIs for maximum compatibility

### Backend Architecture
- **Flask Web Framework**: Lightweight Python web framework for simple routing and templating
- **Session-based Authentication**: Uses Flask sessions for user authentication without requiring passwords
- **In-memory Data Storage**: All data (messages, users, rooms) stored in Python dictionaries and sets
- **Stateless Design**: Each request is independent, making the app simple and predictable

### Data Management
- **Room System**: Three predefined chat rooms (General, Gaming, Help) with message history
- **User Presence**: Tracks connected users globally and per-room using Python sets
- **Message Structure**: Simple dictionary-based messages with username, timestamp, and text
- **Memory-only Persistence**: No database - all data resets on server restart

### Authentication & Authorization
- **Simple Username System**: Users only need to provide a username (max 20 characters)
- **Session Management**: Flask sessions track logged-in users
- **No Password Protection**: Simplified for ease of use on 3DS devices
- **Automatic Cleanup**: Users are removed from rooms and global user list on logout

## External Dependencies

### Python Packages
- **Flask**: Core web framework for routing, templating, and session management
- **Standard Library**: Uses only built-in Python modules (os, datetime) for core functionality

### Browser Compatibility
- **Legacy JavaScript**: Compatible with older JavaScript engines found in 3DS browsers
- **XMLHttpRequest**: Uses older AJAX methods instead of modern fetch API
- **Basic CSS**: Avoids modern CSS features that may not be supported

### Infrastructure
- **No Database**: Intentionally avoids external database dependencies
- **No WebSocket Server**: Uses HTTP polling instead of real-time connections
- **Environment Variables**: Uses SESSION_SECRET for Flask session security
- **Static File Serving**: Flask serves CSS and JavaScript files directly