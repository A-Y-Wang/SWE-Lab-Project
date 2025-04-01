import InventoryCard from './InventoryCard'; 
import './css/Homepage_layout.css'; 

function Homepage_layout() { 
  const inventoryItems = [ 
    { itemName: 'Item 1', itemsAvailable: 10, itemsTotal: 20 }, 
    { itemName: 'Item 2', itemsAvailable: 5, itemsTotal: 15 }, 
    { itemName: 'Item 3', itemsAvailable: 8, itemsTotal: 25 }, 
    { itemName: 'Item 4', itemsAvailable: 12, itemsTotal: 30 }, 
    { itemName: 'Item 5', itemsAvailable: 7, itemsTotal: 18 }, 
    { itemName: 'Item 6', itemsAvailable: 3, itemsTotal: 10 }, 
    { itemName: 'Item 7', itemsAvailable: 6, itemsTotal: 22 }, 
    { itemName: 'Item 8', itemsAvailable: 9, itemsTotal: 27 }, 
  ]; 
  
  return (
    <div className="Homepage_layout">
      {inventoryItems.map((item, index) => (
        <InventoryCard
          key={index}
          itemName={item.itemName}
          itemsAvailable={item.itemsAvailable}
          itemsTotal={item.itemsTotal}
        />
      ))}
    </div>
  );
}

export default Homepage_layout;
