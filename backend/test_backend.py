import httpx
import asyncio
import json
from datetime import datetime


class InventoryAPITester:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)
        self.test_item_id = None
        self.test_checkout_id = None

    async def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting API tests...\n")
        
        # Inventory Tests
        await self.test_add_inventory_item()
        await self.test_get_all_inventory()
        await self.test_get_inventory_item()
        await self.test_update_inventory_item()
        
        # Checkout Tests
        await self.test_checkout_item()
        await self.test_get_all_checkouts()
        await self.test_get_active_checkouts()
        await self.test_update_checkout_condition()
        await self.test_return_item()
        
        # Stats and Additional Tests
        await self.test_inventory_stats()
        await self.test_delete_inventory_item()
        
        print("\n✅ All tests completed!")
        
    async def test_add_inventory_item(self):
        """Test adding a new inventory item"""
        print("Testing POST /api/inventory - Add inventory item")
        
        item_data = {
            "item_name": f"Test Item {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "This is a test item created by the automated test script",
            "quantity": 10
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/inventory",
            json=item_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            self.test_item_id = data.get("item", {}).get("_id")
            print(f"✅ Successfully created item with ID: {self.test_item_id}")
        else:
            print(f"❌ Failed to create item: {response.text}")
            
        return response
    
    async def test_get_all_inventory(self):
        """Test getting all inventory items"""
        print("\nTesting GET /api/inventory - Get all inventory items")
        
        response = await self.client.get(f"{self.base_url}/api/inventory")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved {len(data)} inventory items")
        else:
            print(f"❌ Failed to get inventory: {response.text}")
            
        return response
    
    async def test_get_inventory_item(self):
        """Test getting a specific inventory item"""
        if not self.test_item_id:
            print("\n⚠️ Skipping get inventory item test - no item ID available")
            return None
            
        print(f"\nTesting GET /api/inventory/{self.test_item_id} - Get specific inventory item")
        
        response = await self.client.get(f"{self.base_url}/api/inventory/{self.test_item_id}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved item: {data.get('item_name', 'Unknown')}")
        else:
            print(f"❌ Failed to get item: {response.text}")
            
        return response
    
    async def test_update_inventory_item(self):
        """Test updating an inventory item"""
        if not self.test_item_id:
            print("\n⚠️ Skipping update inventory item test - no item ID available")
            return None
            
        print(f"\nTesting PUT /api/inventory/{self.test_item_id} - Update inventory item")
        
        update_data = {
            "description": f"Updated description at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "quantity": 15
        }
        
        response = await self.client.put(
            f"{self.base_url}/api/inventory/{self.test_item_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully updated item")
        else:
            print(f"❌ Failed to update item: {response.text}")
            
        return response
    
    async def test_checkout_item(self):
        """Test checking out an item"""
        if not self.test_item_id:
            print("\n⚠️ Skipping checkout item test - no item ID available")
            return None
            
        print(f"\nTesting POST /api/checkout/{self.test_item_id} - Checkout item")
        
        checkout_data = {
            "checked_out_by": "Test User",
            "condition": "Good"
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/checkout/{self.test_item_id}",
            json=checkout_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            self.test_checkout_id = data.get("checkout", {}).get("_id")
            print(f"✅ Successfully checked out item with checkout ID: {self.test_checkout_id}")
        else:
            print(f"❌ Failed to checkout item: {response.text}")
            
        return response
    
    async def test_get_all_checkouts(self):
        """Test getting all checkouts"""
        print("\nTesting GET /api/checkout - Get all checkouts")
        
        response = await self.client.get(f"{self.base_url}/api/checkout")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved {len(data)} checkout records")
        else:
            print(f"❌ Failed to get checkouts: {response.text}")
            
        return response
    
    async def test_get_active_checkouts(self):
        """Test getting active checkouts"""
        print("\nTesting GET /api/checkout/active - Get active checkouts")
        
        response = await self.client.get(f"{self.base_url}/api/checkout/active")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved {len(data)} active checkout records")
        else:
            print(f"❌ Failed to get active checkouts: {response.text}")
            
        return response
    
    async def test_update_checkout_condition(self):
        """Test updating checkout condition"""
        if not self.test_checkout_id:
            print("\n⚠️ Skipping update checkout condition test - no checkout ID available")
            return None
            
        print(f"\nTesting PUT /api/checkout/{self.test_checkout_id}/update-condition - Update checkout condition")
        
        condition_data = {
            "condition": "Damaged"
        }
        
        response = await self.client.put(
            f"{self.base_url}/api/checkout/{self.test_checkout_id}/update-condition",
            json=condition_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully updated checkout condition")
        else:
            print(f"❌ Failed to update checkout condition: {response.text}")
            
        return response
    
    async def test_return_item(self):
        """Test returning an item"""
        if not self.test_checkout_id:
            print("\n⚠️ Skipping return item test - no checkout ID available")
            return None
            
        print(f"\nTesting PUT /api/checkout/{self.test_checkout_id}/return - Return item")
        
        return_data = {
            "condition": "Damaged"
        }
        
        response = await self.client.put(
            f"{self.base_url}/api/checkout/{self.test_checkout_id}/return",
            json=return_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully returned item")
        else:
            print(f"❌ Failed to return item: {response.text}")
            
        return response
    
    async def test_inventory_stats(self):
        """Test getting inventory statistics"""
        print("\nTesting GET /api/stats/inventory - Get inventory statistics")
        
        response = await self.client.get(f"{self.base_url}/api/stats/inventory")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved inventory stats")
            print(f"   Total unique items: {data.get('total_unique_items')}")
            print(f"   Out of stock items: {data.get('out_of_stock_items')}")
        else:
            print(f"❌ Failed to get inventory stats: {response.text}")
            
        return response
    
    async def test_delete_inventory_item(self):
        """Test deleting an inventory item"""
        if not self.test_item_id:
            print("\n⚠️ Skipping delete inventory item test - no item ID available")
            return None
            
        print(f"\nTesting DELETE /api/inventory/{self.test_item_id} - Delete inventory item")
        
        response = await self.client.delete(f"{self.base_url}/api/inventory/{self.test_item_id}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully deleted item")
        else:
            print(f"❌ Failed to delete item: {response.text}")
            
        return response
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


async def main():
    """Main entry point for running the tests"""
    try:
        tester = InventoryAPITester()
        await tester.run_all_tests()
        await tester.close()
    except Exception as e:
        print(f"Error during test execution: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(main())