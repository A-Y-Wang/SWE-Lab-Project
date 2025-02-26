import './css/App.css';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LoginPage from './login';
import Navbar from './Navbar';
import DummyPage from './dummyPage'; 

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/dummyPage" element={<DummyPage />} /> {/* Define the route for the new page */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;
