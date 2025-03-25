import './css/App.css';
import './css/checkout.css';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from './login';
import Navbar from './Navbar';
import Checkout from './checkout'; 
import SignUp from './signup'; 

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/checkout" element={<Checkout />} /> {/* Define the route for the new page */}
        </Routes>
      </div>
    </Router>
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
