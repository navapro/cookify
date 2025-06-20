# Cookify - Spotify but for recipes

A full-stack web application for recipe management with user profiles, cooklists, and a gamified leveling system.

## Quick Start

### Launch the Application
```bash
./launch_app
```
This script starts both the frontend (React) and backend (Flask) servers.

## Testing

### Database Testing
```bash
cd sql
./reset-and-test.sh
```
This script resets the database, creates tables, and runs test queries for user profile creation.

### Manual Testing
1. **User Registration**: Visit `/register` to create a new account
2. **User Login**: Visit `/login` to authenticate
3. **Profile View**: Visit `/profile` to see user stats and chef level
4. **Recipe Management**: Browse and create recipes from the main dashboard

## Technologies Used

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Lucide React** - Icons
- **Shadcn/ui** - Component library

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM
- **MySQL** - Database
- **JWT** - Authentication
- **Werkzeug** - Password hashing

### Database
- **MySQL 8.0** - DBSM

### Development Tools
- **Git** - Version control
- **Shell Scripts** - Database management and app launching 
