import './App.css';
import ItemList from './Items';

function Checkout() {
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
    )
}

export default Checkout;