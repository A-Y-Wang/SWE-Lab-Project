import './css/checkout.css'
import { useState, useEffect} from "react";
import "./css/App.css"

//Populating item catalog with the backend DB items
const ItemList = () => {
    const[items, setItems] = useState([]);
    const [expandedItems, setExpandedItems] = useState({});
    const [clickedCheckoutItems, setClickedCheckoutItems] = useState({}); 
    const [clickedCheckinItems, setClickedCheckinItems] = useState({}); 
    const [checkoutQuantities, setCheckoutQuantities] = useState({});
    const [checkinQuantities, setCheckinQuantities] = useState({});

    //API routes
    const fetchInventory = () => {
      fetch('http://localhost:5000/api/inventory')
        .then((res) => res.json())
        .then((data) => {
          console.log("Fetched data:", data);
          setItems(data);
        })
        .catch((error) => console.error("Error fetching inventory", error));
    };

    useEffect(()=> {
      fetchInventory();
    }, []);

    const dropDetails = (id) => {
        setExpandedItems((prevState) => 
          ({...prevState, [id]: !prevState[id],
        }));
      };

    const checkoutButton = (id) => {
      const inputQuantity = parseInt(checkoutQuantities[id], 10);
      if(!isNaN(inputQuantity) && inputQuantity > 0){
        const item = items.find((item)=> item._id === id);
        if(!item)return;

        const newQuant = item.quantity - inputQuantity
        const updatedQuant = newQuant >= 0? newQuant : 0;

        fetch(`http://localhost:5000/api/inventory/${id}`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({quantity: updatedQuant})
        })
          .then((res)=> {
            if(!res.ok){
              throw new Error("Failed to update item")
            }
            return res.json();
          })
          .then(() =>{
            fetchInventory();
          })
          .catch((error) => {
            console.error("Error updating item:", error);
          });
        }
        setCheckoutQuantities(prev => ({ ...prev, [id]: "" }));
        setClickedCheckoutItems(prev => ({ ...prev, [id]: true }));
      
        setTimeout(() => {
          setClickedCheckoutItems(prev => ({ ...prev, [id]: false }));
        }, 3000);
      };

    const checkinButton = (id) => {
      const inputQuantity = parseInt(checkinQuantities[id], 10)

      if(!isNaN(inputQuantity)&&inputQuantity>0){
        const item = items.find((item)=> item._id === id);
        if(!item)return;

        const newQuantity = item.quantity + inputQuantity;
        const updatedQuantity = newQuantity > item.capacity ? item.capacity : newQuantity;

        fetch(`http://localhost:5000/api/inventory/${id}`,{
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json'
          },
          body : JSON.stringify({quantity:updatedQuantity})
        })
          .then((res)=>{
            if(!res.ok){
              throw new Error("Failed to update item");
            }
            return res.json();
          })
          .then(()=>{
            fetchInventory();
          })
          .catch((error)=>{
            console.error("Error updating item:", error);
          });
      }
      setCheckinQuantities((prev) => ({ ...prev, [id]: "" }));
      setClickedCheckinItems((prev) => ({ ...prev, [id]: true }));
      setTimeout(() => {
        setClickedCheckinItems((prev) => ({ ...prev, [id]: false }));
      }, 3000);
    };
    

      
  
    //displaying the page
    return (
      <>
        {items.map((item) => (
          <div key={item._id} className="item-container">
            <div className="item-block">
                <div className="item-details">
                    <p><strong>Name:</strong> {item.item_name}</p>
                    <p><strong>Decription:</strong> {item.description}</p>

                </div>
                <div className="details-container">
                  <p><strong>Quantity:</strong> {item.quantity}/{item.capacity}</p>
                </div>
                <div className="right-side">
                <div className = "checkout-box">
                  <input
                    type="number"
                    placeholder="Enter Quantity"
                    value={checkoutQuantities[item._id] || ""}
                    onChange={(e) =>
                      setCheckoutQuantities(prev => ({
                        ...prev,
                        [item._id]: e.target.value,
                      }))
                    }
                  />
                  <button 
                      className={`toggle-btn ${clickedCheckoutItems[item._id] ? "green" : ""}`} 
                      onClick={() => checkoutButton(item._id)}
                  >
                      {clickedCheckoutItems[item._id] ? "Complete!" : "Checkout"}
                  </button>
                </div>
                <div className="checkin-box">
                  <input
                    type="number"
                    placeholder="Enter Quantity"
                    value={checkinQuantities[item._id] || ""}
                    onChange={(e) =>
                      setCheckinQuantities((prev)=>({
                        ...prev,
                        [item._id]: e.target.value,
                      }))
                    }
                  />
                  <button
                      className={`toggle-btn ${clickedCheckinItems[item._id] ? "green" : ""}`}
                      onClick={() => checkinButton(item._id)}
                  >
                      {clickedCheckinItems[item._id] ? "Complete!" : "Checkin"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        ))}
      </>
    );
  };
  
export default ItemList;