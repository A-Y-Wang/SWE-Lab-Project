import './css/checkout.css'
import { useState, useEffect} from "react";
import "./css/App.css"

//Populating item catalog with the backend DB items
const ProjectItemList = ({user}) => {
    const [projects, setProjects] = useState([]);
    // const [items, setItems] = useState([]);//remove later maybe
    const [clickedCheckoutItems, setClickedCheckoutItems] = useState({}); 
    const [clickedCheckinItems, setClickedCheckinItems] = useState({}); 
    const [checkoutQuantities, setCheckoutQuantities] = useState({});
    const [checkinQuantities, setCheckinQuantities] = useState({});
    
    //extract the userId and save it
    const userId = user ? user.UserId : null;

    //API routes
    const fetchProjects = () => {
      if(!userId) return;
      fetch(`/user/${userId}/projects/inventory`)
        .then((res)=> res.json())
        .then((data) => {
          console.log("Fetched projects with items:", data);
          setProjects(data);
        })
        .catch((error) => console.error("Error fetching projects:", error));
    }

    // const fetchInventory = () => {
    //   fetch('http://localhost:5000/api/inventory')
    //     .then((res) => res.json())
    //     .then((data) => {
    //       console.log("Fetched data:", data);
    //       setItems(data);
    //     })
    //     .catch((error) => console.error("Error fetching inventory", error));
    // };

    // Helper function to find an item by id across all projects
    const getItemById = (id) => {
      for (let project of projects) {
        const found = project.items.find(item => item._id === id);
        if (found) return found;
      }
      return null;
    };

    useEffect(()=> {
      fetchProjects();
    }, [userId]);


    const checkoutButton = (id) => {
      const inputQuantity = parseInt(checkoutQuantities[id], 10);
      if(!isNaN(inputQuantity) && inputQuantity > 0){
        const item = getItemById(id);
        if(!item)return;

        const newQuant = item.quantity - inputQuantity
        const updatedQuant = newQuant >= 0? newQuant : 0;

        fetch(`/inventory/${id}`, {
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
            fetchProjects();
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
        const item = getItemById(id);
        if(!item)return;

        const newQuantity = item.quantity + inputQuantity;
        const updatedQuantity = newQuantity > item.capacity ? item.capacity : newQuantity;

        fetch(`/inventory/${id}`,{
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
            fetchProjects();
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
      {projects.map((project)=>(
        <div key={project.project_id} className="project-container">
          <div className="project-header">
            <h3>{project.project_name}</h3>
            <h3>Desciption: {project.project_description}</h3>
          </div>
          {project.items && project.items.length > 0 ? (
            project.items.map((item) => (
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
            ))
          ) : (
            <p> No items found for this project.</p>
          )}
          </div>
          ))}
        </>
      );
    };
  
export default ProjectItemList;