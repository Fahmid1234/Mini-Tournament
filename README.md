# 🏏 Gali Premier League Mini Tournament

A comprehensive cricket tournament management system built with Django, featuring a 5-over match format and detailed player statistics tracking.

## ✨ Features

### 🏆 Core Tournament Features
- **5-Over Match Format**: Fast-paced cricket matches with 5 overs per innings
- **Team Management**: Create and manage teams with custom logos and color themes
- **Match Scheduling**: Schedule matches with automatic fixture generation
- **Results Tracking**: Record match results and update points table automatically
- **Points Table**: Real-time standings with Net Run Rate (NRR) calculations

### 🏏 Player Performance Tracking
- **Individual Player Statistics**: Track detailed performance metrics for each player
- **Batting Statistics**: Runs scored, balls faced, strike rate, fours, sixes
- **Bowling Statistics**: Wickets taken, runs conceded, overs bowled, economy rate
- **Fielding Statistics**: Catches taken, stumpings
- **All-Rounder Rankings**: Combined performance scoring for versatile players

### 🏅 Tournament Awards System
- **Player of the Match**: Awarded to the best performer in each match
- **Player of the Tournament**: Overall best performer based on comprehensive scoring
- **Highest Run Scorer**: Player with most runs in the tournament
- **Highest Wicket Taker**: Player with most wickets in the tournament
- **Automatic Award Calculation**: Awards are calculated and updated automatically

### 📊 Advanced Statistics
- **Real-time Rankings**: Live player rankings in batting, bowling, and all-rounder categories
- **Performance Analytics**: Detailed statistics with averages and rates
- **Team Performance**: Comprehensive team statistics and analysis
- **Match History**: Complete match records with player performances

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 5.0+
- SQLite (default) or PostgreSQL

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Mini-Tournament
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   python manage.py migrate
   ```

4. **Create sample data**
   ```bash
   python manage.py create_sample_data
   ```

5. **Calculate awards**
   ```bash
   python manage.py calculate_awards
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://127.0.0.1:8000
   - Admin panel: http://127.0.0.1:8000/admin

## 📱 Available Pages

### 🏠 Home Page
- Tournament overview and statistics
- Upcoming and recent matches
- Points table preview
- Quick access to new features

### 👥 Teams
- Team listings with logos and details
- Individual team pages
- Player rosters

### 📅 Schedule
- Complete match schedule
- Match details and status
- 5-over format information

### 🏆 Results
- Match results and scores
- Player of the match awards
- Match statistics

### 📊 Points Table
- Team standings with NRR
- Win/loss records
- Performance indicators

### 🏏 Player Statistics
- **Batting Rankings**: Top run scorers with detailed stats
- **Bowling Rankings**: Top wicket takers with economy rates
- **All-Rounder Rankings**: Best performing all-rounders
- **Individual Performance**: Detailed player analysis

### 🏅 Tournament Awards
- **Major Awards**: Player of the Tournament, Highest Run Scorer, Highest Wicket Taker
- **Award History**: Complete list of all tournament awards
- **Performance Recognition**: Celebrating outstanding achievements

## 🛠️ Management Commands

### Create Sample Data
```bash
python manage.py create_sample_data
```
Creates teams, players, matches, and player performances for testing.

### Calculate Awards
```bash
python manage.py calculate_awards
```
Calculates and updates tournament awards based on current player performances.

## 🎮 Admin Panel Features

### Match Management
- Create and edit matches
- Set 5-over format
- Assign Player of the Match
- Update scores and results

### Player Performance Management
- Record detailed player statistics
- Track batting and bowling performances
- Manage fielding statistics
- Automatic calculation of rates and averages

### Tournament Awards Management
- View and manage tournament awards
- Automatic award calculations
- Award history tracking

### Points Table Management
- Real-time points table updates
- NRR calculations
- Team performance tracking

## 🏏 Tournament Format

### Match Structure
- **Format**: 5 overs per innings
- **Duration**: Approximately 30-45 minutes per match
- **Teams**: 4-8 players per team
- **Scoring**: Standard cricket rules with T20 adaptations

### Points System
- **Win**: 2 points
- **Loss**: 0 points
- **Tiebreaker**: Net Run Rate (NRR)

### Award Scoring
- **Player of the Tournament**: Best overall performance (runs + wickets × 25)
- **Highest Run Scorer**: Most runs in tournament
- **Highest Wicket Taker**: Most wickets in tournament

## 🎨 Design Features

### Modern UI/UX
- Responsive design for all devices
- Beautiful gradient backgrounds
- Interactive hover effects
- Mobile-friendly navigation

### Visual Elements
- Team color themes
- Performance indicators
- Award badges and icons
- Statistics visualizations

## 🔧 Technical Features

### Database Models
- **Team**: Team information and branding
- **Player**: Player details and roles
- **Match**: Match scheduling and results
- **PlayerMatchPerformance**: Detailed player statistics
- **TournamentAwards**: Award tracking and history
- **PointsTableEntry**: Team standings and NRR

### Admin Interface
- Comprehensive admin panel
- Bulk operations
- Data import/export
- Performance monitoring

### API Ready
- RESTful URL structure
- JSON-compatible data models
- Extensible architecture

## 🚀 Future Enhancements

### Planned Features
- **Live Scoring**: Real-time match updates
- **Player Profiles**: Detailed player pages
- **Match Commentary**: Live match commentary
- **Statistics Export**: PDF/Excel reports
- **Mobile App**: Native mobile application
- **Social Features**: Player and team social media integration

### Technical Improvements
- **Caching**: Redis integration for performance
- **Search**: Advanced search functionality
- **Notifications**: Email/SMS notifications
- **Analytics**: Advanced performance analytics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🏏 About Gali Premier League

The Gali Premier League Mini Tournament is designed to bring the excitement of cricket to local communities with a fast-paced, engaging format that's perfect for quick matches and tournament play.

---

**🏏 Experience the thrill of cricket with our mini tournament! 🏆** 