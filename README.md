# 🚂 Levison Randles College App+ ✨

**"Where Magic Meets Education"**

A revolutionary tip-based college platform founded by the legendary Levison Randles, who famously levitated out of jail with Magneto's help and went on to create a free tuition college that operates on pure appreciation!

## 🎓 Features

### Core Features
- **🔐 User Authentication** - Student and Professor accounts
- **💸 Tips System** - CashApp integration for appreciating educators
- **🐦 Randles Twitter** - Social platform for the college community
- **🏠 Dashboard** - Personal stats and Randles Level tracking

### Coming Soon
- **🃏 StackDecks** - Share your secret web resources organized by functionality and field
- **📺 Streaming+** - Live educational streams and virtual classrooms
- **👼 Job Opper[tm]** - Revolutionary job interviews through streaming
- **🎮 Admin Portals** - Separate interfaces for students and professors

## 🌟 The Levison Randles Universe

### Characters & Themes
- **🚂 Thomas Detrain** - College train mascot (not for babies!)
- **🧙‍♂️ Professor Joker** - Wisdom through humor
- **🧪 Rick Sanchez** - Interdimensional education insights
- **⚡ Bedlam Demonz** - Chaotic creativity energy
- **🥤 Gatorade** - Hydration wisdom

### Color Scheme
- **💚 Randles Green** - Primary color (#00ff41)
- **🖤 Dark Theme** - Background (#0a0a0a)
- **💛 Gold Highlights** - Accents (#ffd700)
- **🧈 Butter** - Text color (#fff8dc)

## 🚀 Getting Started

### Prerequisites
- Node.js (v14 or higher)
- MongoDB (local or cloud instance)
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/levison-randles-college-app.git
   cd levison-randles-college-app
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MongoDB URI and other settings
   ```
   
   **Required Environment Variables:**
   - `MONGODB_URI` - Your MongoDB connection string
   - `JWT_SECRET` - A secure secret for JWT token signing (64+ characters recommended)
   - `PORT` - Server port (defaults to 3000)
   - `NODE_ENV` - Set to 'production' for deployment
   
   **For Railway Deployment:**
   1. Set `MONGODB_URI` with your actual database password
   2. Generate a strong `JWT_SECRET` (use a random string generator)
   3. Set `NODE_ENV=production`
   4. Configure any external API keys as needed

4. **Start MongoDB**
   ```bash
   # If using local MongoDB
   mongod
   ```

5. **Run the application**
   ```bash
   # Development mode
   npm run dev
   
   # Production mode
   npm start
   ```

6. **Open your browser**
   ```
   http://localhost:3000
   ```

## 📁 Project Structure

```
levison-randles-college-app/
├── 📄 server.js              # Main application server
├── 📁 models/                # Database models
│   ├── User.js              # User accounts with magical abilities
│   ├── Tip.js               # Tips and appreciation system
│   ├── Tweet.js             # Social media posts
│   └── StackDeck.js         # Web resource collections
├── 📁 routes/               # API endpoints
│   ├── auth.js              # Authentication
│   ├── users.js             # User management
│   ├── tips.js              # Tipping system
│   ├── tweets.js            # Social features
│   ├── stackdecks.js        # Resource sharing
│   ├── streaming.js         # Live streaming (coming soon)
│   └── jobopportunities.js  # Job platform (coming soon)
├── 📁 public/               # Static files
│   ├── 📁 css/
│   │   └── styles.css       # Randles-themed styling
│   ├── 📁 js/
│   │   └── app.js           # Frontend JavaScript
│   └── 📁 images/           # Assets and icons
├── 📁 views/                # HTML templates
│   └── index.html           # Main application interface
└── 📁 middleware/           # Custom middleware (future)
```

## 🎯 Core Concepts

### Randles Level System
Users progress through levels (1-100) based on:
- Tips given and received
- Quality content creation
- Community engagement
- Magical abilities displayed

### Tip Economy
- **No tuition fees** - Students pay what they can afford
- **Direct appreciation** - Tips go directly to educators
- **CashApp integration** - Seamless payment processing
- **Transparency** - Public tip leaderboards (optional)

### Magical Abilities
Each user develops magical abilities:
- 🎭 Levitation
- 🧠 Mind Reading
- ⏰ Time Manipulation
- 📚 Knowledge Absorption
- 🧪 Rick Sanchez IQ
- 🎪 Professor Joker Wisdom

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/register` - Create account
- `POST /api/auth/login` - Login
- `GET /api/auth/me` - Get current user

### Tips
- `POST /api/tips/send` - Send tip
- `GET /api/tips/history` - Get tip history
- `GET /api/tips/leaderboard` - Top tippers/receivers

### Social (Tweets)
- `GET /api/tweets` - Get tweet feed
- `POST /api/tweets` - Create tweet
- `POST /api/tweets/:id/like` - Like/unlike tweet
- `POST /api/tweets/:id/retweet` - Retweet

### Users
- `GET /api/users` - Get all users
- `GET /api/users/search` - Search users
- `PUT /api/users/profile` - Update profile

## 🎨 Themes

The app supports multiple Randles-inspired themes:
- **Green & Dark** (default) - Classic Randles
- **Gold Butter** - Luxurious learning
- **Bedlam Demons** - Chaotic creativity
- **Gatorade Fresh** - Energetic education

## 🔮 Future Features

### Phase 2: StackDecks
- Web resource sharing platform
- Categorized by field and functionality
- Community-driven curation
- Levison-approved verified decks

### Phase 3: Streaming+
- Live educational broadcasts
- Interactive virtual classrooms
- Screen sharing and collaboration
- Recording and playback

### Phase 4: Job Opper[tm]
- Streaming-based job interviews
- Real-time skill demonstrations
- Portfolio showcasing
- Direct employer connections

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Coding Standards
- Follow the Levison Randles way: **magical, simple, and totally college**
- Include appropriate emojis in commit messages 🚂
- Comment your code with Randles wisdom
- Test on both mobile and desktop

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Levison Randles** - Founder and legendary figure
- **Thomas Detrain** - Our beloved train mascot
- **Magneto** - For helping Levison escape to create this college
- **Rick Sanchez** - For interdimensional wisdom
- **Professor Joker** - For making learning fun
- **The Bedlam Demonz** - For chaotic inspiration
- **Gatorade** - For keeping us hydrated during development

## 🚂 Support

For support, email support@randlescollege.edu or join our Discord server.

**"Education through appreciation, powered by tips and levitation."** 
*- Levison Randles*

---

🎓 **All aboard the Randles Express!** 🚂💨

