import React, { useState } from 'react';
import './css/signup.css';

export default function SignUp() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [passwordCheck, setPasswordCheck] = useState("");
  
    const handleSubmit = (e) => {
      e.preventDefault();
      console.log("Username:", username, "Password:", password);
    };
  
    return (
      <div className="signup">
          <h2>SIGN UP</h2>
          <form onSubmit={handleSubmit}>
            <input
              type="username"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
            <br />
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <br />
            <input
              type="password"
              placeholder="Confirm Password"
              value={passwordCheck}
              onChange={(e) => setPasswordCheck(e.target.value)}
              required
            />
            <br />
            <button type="submit" >
              Register
            </button>
          </form>
      </div>
    );
  }