import './App.css'
import { useState } from "react";


const ItemList = () => {
    const [items, setItems] = useState([
      { id: 1, name: "Apple", quantity: 10, details: "crunchy, red, and sweet"},
      { id: 2, name: "Banana", quantity: 10, details: "yellow, mushy, potassium"},
      { id: 3, name: "Cherry", quantity: 10, details: "shiny, juicy, sweet"},
      { id: 4, name: "Orange", quantity: 10, details: "tart, sweet, citrus"},
      { id: 5, name: "Peach", quantity: 10, details: "sweet and pink"},
      { id: 6, name: "Pear", quantity: 10, details: "golden and crunchy"},
      { id: 7, name: "Raspberry", quantity: 10, details: "tiny, tart, red"},
      { id: 8, name: "Pineapple", quantity: 10, details: "pina colada"}
    ]);

    const [expandedItems, setExpandedItems] = useState({});
    const [clickedItems, setClickedItems] = useState({}); 

    const dropDetails = (id) => {
        setExpandedItems((prevState) => ({
          ...prevState,
          [id]: !prevState[id], // expanded state
        }));
      };

    const checkoutButton = (id) => {
        setClickedItems(prevState => ({
          ...prevState,
          [id]: !prevState[id] // green state
        }));
      };
  
    return (
      <>
        {items.map((item) => (
          <div key={item.id} className="item-container">
            <div className="item-block">
                <div className="item-details">
                    <p><strong>Name:</strong> {item.name}</p>
                    <p><strong>Quantity:</strong> {item.quantity}</p>
                </div>

                <button onClick = {() => dropDetails(item.id)}>
                    {expandedItems[item.id] ? "Less" : "More"}
                </button>
            </div>
            
            {expandedItems[item.id] && (
               <div className = "details-box show">
                <p>{item.details}</p> 

                <button 
                    className={`toggle-btn ${clickedItems[item.id] ? "green" : ""}`} 
                    onClick={() => checkoutButton(item.id)}
                >
                    {clickedItems[item.id] ? "Clicked!" : "Click Me"}
                </button>
            </div>
            )}
          </div>
        ))}
      </>
    );
  };
  
  export default ItemList;