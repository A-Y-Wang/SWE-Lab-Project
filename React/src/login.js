import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./css/login.css"

export default function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    console.log("Username:", username, "Password:", password);
    //add login logic here
    try{
      await fetch("http://localhost:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          username: username,
          password: password,
        }),
      })
      .then(async(response) => {
        if (response.status === 200) {
          // const userdata = response.data; //a successful login will send the user document back
          const userdata = await response.json();
          console.log(userdata);
          localStorage.setItem('user', JSON.stringify(userdata)); //storing user data in a local storage
          navigate("/checkout"); //redirects to new page
        } else {
          alert(response.data.error);
        }
      })
      
    } catch (error) {
      console.error("Login failed",error);
      alert("Login Failed, Try again");
    }
  };

  return (
    <div className="login">
        <h2>LOGIN</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="username"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            className="w-full p-2 border border-gray-300 rounded"
          />
          <br />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full p-2 border border-gray-300 rounded"
          />
          <br />
          <button type="submit" >
            Login
          </button>
        </form>
        <br />
        <p>Don't have an account? <a href="/signup">Sign Up</a></p>
    </div>
  );
}