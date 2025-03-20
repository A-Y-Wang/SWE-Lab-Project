import './css/checkout.css'
import { useState } from "react";
import "./css/App.css"


const ItemList = () => {
    const [items, setItems] = useState([
      { id: 1, name: "Apple", quantity: 10, details: "crunchy, red, and sweet"},
      { id: 2, name: "Banana", quantity: 10, details: "yellow, mushy, potassium"},
      { id: 3, name: "Cherry", quantity: 10, details: "shiny, juicy, sweet"},
      { id: 4, name: "Orange", quantity: 10, details: "tart, sweet, citrus"},
      { id: 5, name: "Peach", quantity: 10, details: "sweet and pink"},
      { id: 6, name: "Pear", quantity: 10, details: "golden and crunchy"},
      { id: 7, name: "Raspberry", quantity: 10, details: "tiny, tart, red"},
      { id: 8, name: "Pineapple", quantity: 10, details: "pina colada"},
      { id: 9, name: "Blackberry", quantity: 10, details: "black raspberry"},
      { id: 10, name: "Apricot", quantity: 10, details: "yummy in jam"}
    ]);

    const [expandedItems, setExpandedItems] = useState({});
    const [clickedItems, setClickedItems] = useState({}); 
    const [checkoutQuantities, setCheckoutQuantities] = useState({});

    const dropDetails = (id) => {
        setExpandedItems((prevState) => 
          ({...prevState, [id]: !prevState[id], // expanded state
        }));
      };

    const checkoutButton = (id) => {
      const inputQuantity = parseInt(checkoutQuantities[id], 10);
      if(!isNaN(inputQuantity) && inputQuantity > 0){
        setItems(prevItems =>
          prevItems.map(item =>{
            if (item.id === id){
              const newQuantity = item.quantity - inputQuantity;
              return {...item, quantity: newQuantity >=0 ? newQuantity : 0};
            }
            return item;
          })
        );
      }
        setCheckoutQuantities(prev => ({...prev, [id]: ""}));
        setClickedItems(prev => ({...prev, [id]: true}));

        setTimeout(() => {
          setClickedItems((prev) => ({...prev, [id]: false}));
        }, 3000);
    }
  
    return (
      <>
        {items.map((item) => (
          <div key={item.id} className="item-container">
            <div className="item-block">
                <div className="item-details">
                    <p><strong>Name:</strong> {item.name}</p>
                    <p><strong>Quantity:</strong> {item.quantity}</p>

                </div>
                <div className="details-container">
                  <p><strong>Details:</strong> {item.details}</p>
                </div>
                <button onClick = {() => dropDetails(item.id)}>
                    {expandedItems[item.id] ? "Less" : "More"}
                </button>
            </div>
            
            {expandedItems[item.id] && (
               <div className = "details-box show">
                <input
                  type="number"
                  placeholder="Enter Quantity"
                  value={checkoutQuantities[item.id] || ""}
                  onChange={(e) =>
                    setCheckoutQuantities(prev => ({
                      ...prev,
                      [item.id]: e.target.value,
                    }))
                  }
                />

                <button 
                    className={`toggle-btn ${clickedItems[item.id] ? "green" : ""}`} 
                    onClick={() => checkoutButton(item.id)}
                >
                    {clickedItems[item.id] ? "Complete!" : "Checkout"}
                </button>
               </div>
            )}
          </div>
        ))}
      </>
    );
  };
  
export default ItemList;