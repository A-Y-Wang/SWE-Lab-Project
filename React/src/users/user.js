const mongoose = require('mongoose');
const Schema = mongoose.Schema;

const userItemsSchema = new Schema({
  name: {
    type: String,
    required: true
  },
  project: {
    type: String,
    required: true
  },
  itemId: {
    type: String,
    required: true
  }
});

const userSchema = new Schema({
  username: {
    type: String,
    required: true,
    unique: true
  },
  userItems: [userItemsSchema]
});

const User = mongoose.model('User', userSchema);

module.exports = User;
