import './css/checkout.css';
import ItemList from './Items';

function Checkout() {
    return (
        <div className="app-container">
            <div className="scroll-bar items">
                <h2>Checkout Items</h2>
                <ItemList />
            </div>
        </div>
    )
}

export default Checkout;