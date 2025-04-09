import React, { useEffect, useState } from 'react';
import './css/checkout.css';
import ProjectItemList from './Items';
import "./css/App.css"


function Checkout() {
    const [user, setUser] = useState(null);

    // Retrieve the user data from localStorage when the component mounts
    useEffect(() => {
      const storedUser = localStorage.getItem('user');
      if (storedUser) {
        setUser(JSON.parse(storedUser));
      }
    }, []);

    return (
        <div className="app-container">
            {user ? (
            <h1 className="hi-user">Hi, {user.Username}</h1>
            ) : (
            <h1>Loading...</h1>
            )}
            <div className="scroll-bar items">
                <h1>Checkout Items</h1>
                {user && <ProjectItemList user = {user} />}
            </div>
        </div>
    )
}

export default Checkout;