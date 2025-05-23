import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import './css/signup.css';

export default function SignUp() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [passwordCheck, setPasswordCheck] = useState("");
    const navigate = useNavigate();
  
    const handleSubmit = async (e) => {
      e.preventDefault();
      console.log("Username:", username, "Password:", password);
      if (password !== passwordCheck){
        alert("passwords dont match");
        return
      }
      try{
        await fetch("/signup", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            username: username,
            password: password,
          }),
        })
        .then((response) => {
          if(response.status === 201){
            navigate("/");
          }
          else{
            alert(response.data.error);
          }
        })

        
      } catch (error) {
        console.error("registration failed",error);
        alert("Registration Failed, Try again");
      }
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