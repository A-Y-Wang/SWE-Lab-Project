import './css/checkout.css';
import ItemList from './Items';
import "./css/App.css"


function Checkout() {
    return (
        <div className="app-container">
            <div className="scroll-bar items">
                <h1>Checkout Items</h1>
                <ItemList />
            </div>
        </div>
    )
}

export default Checkout;