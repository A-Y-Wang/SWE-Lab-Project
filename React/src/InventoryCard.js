import React from 'react';
import "./css/InventoryCard.css"; 

const InventoryCard = ({ itemName, itemsAvailable, itemsTotal }) => {
  return (
    <div className="inventory-card">
      <div className="item-image"></div>
      
      <div className="item-info">
        <p><span>Item Name:</span> {itemName}</p>
        <p><span>Items Available:</span> {itemsAvailable}</p>
        <p><span>Items Total In Storage:</span> {itemsTotal}</p>
      </div>
      
      <div className="action-buttons">
        <div className="button-row">
          <input type ="number" className="qty-input" placeholder='Enter Qty'/>
          <button className="check-button">Check-In</button>
        </div>
        <div className="button-row">
          <input type ="number" className='qty-input' placeholder= 'Enter Qty'/>
          <button className="check-button">Check-Out</button>
        </div>
      </div>
    </div>
  );
};

export default InventoryCard;
