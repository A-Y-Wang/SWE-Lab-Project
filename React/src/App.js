import './App.css';
import ItemList from './Items.js';

function App() {
  return (
    <div className="app-container">
      <div className="scroll-bar items">
        <h2>Checkout Items</h2>
        <ItemList />
      </div>

      <div className="scroll-bar projects">
        <h2>My Projects</h2>
      </div>
    </div>
  );
}

// const ItemList = () => {
//   const [items, setItems] = useState([]); 
//   useEffect(() => {
//     fetch("https://api.example.com/items")
//       .then(response => response.json())
//       .then(data => setItems(data)) 
//       .catch(error => console.error("Error fetching items:", error));
//   }, []); //pulls items from the API store of hardware

//test items in scroll bar for now

export default App;
