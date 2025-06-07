const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path');
const socketIo = require('socket.io');
const http = require('http');
require('dotenv').config();

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"]
  }
});

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, 'public')));

// Routes
app.use('/api/auth', require('./routes/auth'));
app.use('/api/users', require('./routes/users'));
app.use('/api/tips', require('./routes/tips'));
app.use('/api/tweets', require('./routes/tweets'));
app.use('/api/stackdecks', require('./routes/stackdecks'));
app.use('/api/streaming', require('./routes/streaming'));
app.use('/api/jobopportunities', require('./routes/jobopportunities'));

// Socket.io for real-time features
io.on('connection', (socket) => {
  console.log('🚂 Thomas Detrain says: New user connected to the Randles Express!');
  
  socket.on('join-stream', (roomId) => {
    socket.join(roomId);
    socket.to(roomId).emit('user-joined', socket.id);
  });
  
  socket.on('stream-data', (data) => {
    socket.to(data.roomId).emit('stream-data', data);
  });
  
  socket.on('new-tweet', (tweet) => {
    io.emit('tweet-update', tweet);
  });
  
  socket.on('tip-sent', (tipData) => {
    io.emit('tip-notification', tipData);
  });
  
  socket.on('disconnect', () => {
    console.log('🚂 User left the Randles Express');
  });
});

// Serve main app
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'views', 'index.html'));
});

// Connect to MongoDB
mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/levison-randles-college', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
})
.then(() => console.log('🔥 Connected to MongoDB - Levison would be proud!'))
.catch(err => console.error('MongoDB connection error:', err));

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => {
  console.log(`🚂🔥 Levison Randles College App+ running on port ${PORT}`);
  console.log('🎓 Welcome to the magical world of tip-based education!');
  console.log('💚 Green & Dark theme activated with gold highlights ✨');
});

// Make io accessible to routes
app.set('socketio', io);

