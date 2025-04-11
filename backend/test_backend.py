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
        self.test_project_id = None
        self.test_user_id = None

    async def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting API tests...\n")
        
        # User Tests (needed for project tests)
        await self.test_user_signup()
        await self.test_user_login()
        
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
        
        # Project Tests
        await self.test_create_project()
        await self.test_get_all_projects()
        await self.test_get_project()
        await self.test_update_project()
        await self.test_add_item_to_project()
        await self.test_get_project_items()
        await self.test_get_user_projects()
        await self.test_remove_item_from_project()
        
        # Cleanup Tests
        await self.test_delete_project()
        await self.test_delete_inventory_item()
        
        print("\n✅ All tests completed!")
    
    async def test_user_signup(self):
        """Test signing up a user"""
        print("Testing POST /signup - Register a new user")
        
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        user_data = {
            "username": f"testuser_{timestamp}",
            "password": "testpassword123"
        }
        
        response = await self.client.post(
            f"{self.base_url}/signup",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print(f"✅ Successfully registered user: {user_data['username']}")
        else:
            print(f"❌ Failed to register user: {response.text}")
            
        return response
    
    async def test_user_login(self):
        """Test logging in a user"""
        print("\nTesting POST /login - Login with credentials")
        
        # Assuming we have a user from the signup test or use a known test user
        login_data = {
            "username": "testuser_20250410181204", # You might need to adjust this based on existing users
            "password": "testpassword123"
        }
        
        response = await self.client.post(
            f"{self.base_url}/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            self.test_user_id = data.get("UserId")
            print(f"✅ Successfully logged in user with ID: {self.test_user_id}")
        else:
            print(f"❌ Failed to login: {response.text}")
            
        return response
        
    async def test_add_inventory_item(self):
        """Test adding a new inventory item"""
        print("\nTesting POST /api/inventory - Add inventory item")
        
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
    
    async def test_create_project(self):
        """Test creating a new project"""
        if not self.test_user_id:
            print("\n⚠️ Skipping create project test - no user ID available")
            return None
            
        print("\nTesting POST /api/projects - Create a new project")
        
        project_data = {
            "project_name": f"Test Project {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "This is a test project created by the automated test script",
            "created_by": self.test_user_id
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/projects",
            json=project_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            self.test_project_id = data.get("project", {}).get("project_id")
            print(f"✅ Successfully created project with ID: {self.test_project_id}")
        else:
            print(f"❌ Failed to create project: {response.text}")
            
        return response
    
    async def test_get_all_projects(self):
        """Test getting all projects"""
        print("\nTesting GET /api/projects - Get all projects")
        
        response = await self.client.get(f"{self.base_url}/api/projects")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved {len(data)} projects")
        else:
            print(f"❌ Failed to get projects: {response.text}")
            
        return response
    
    async def test_get_project(self):
        """Test getting a specific project"""
        if not self.test_project_id:
            print("\n⚠️ Skipping get project test - no project ID available")
            return None
            
        print(f"\nTesting GET /api/projects/{self.test_project_id} - Get specific project")
        
        response = await self.client.get(f"{self.base_url}/api/projects/{self.test_project_id}")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved project: {data.get('project_name', 'Unknown')}")
        else:
            print(f"❌ Failed to get project: {response.text}")
            
        return response
    
    async def test_update_project(self):
        """Test updating a project"""
        if not self.test_project_id or not self.test_user_id:
            print("\n⚠️ Skipping update project test - no project or user ID available")
            return None
            
        print(f"\nTesting PUT /api/projects/{self.test_project_id} - Update project")
        
        update_data = {
            "project_name": f"Updated Project {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": f"Updated description at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "user_id": self.test_user_id
        }
        
        response = await self.client.put(
            f"{self.base_url}/api/projects/{self.test_project_id}",
            json=update_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully updated project")
        else:
            print(f"❌ Failed to update project: {response.text}")
            
        return response
    
    async def test_add_item_to_project(self):
        """Test adding an item to a project"""
        if not self.test_project_id or not self.test_item_id or not self.test_user_id:
            print("\n⚠️ Skipping add item to project test - missing required IDs")
            return None
            
        print(f"\nTesting POST /api/projects/{self.test_project_id}/items - Add item to project")
        
        item_data = {
            "item_id": self.test_item_id,
            "user_id": self.test_user_id
        }
        
        response = await self.client.post(
            f"{self.base_url}/api/projects/{self.test_project_id}/items",
            json=item_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully added item to project")
        else:
            print(f"❌ Failed to add item to project: {response.text}")
            
        return response
    
    async def test_get_project_items(self):
        """Test getting items in a project"""
        if not self.test_project_id:
            print("\n⚠️ Skipping get project items test - no project ID available")
            return None
            
        print(f"\nTesting GET /api/projects/{self.test_project_id}/items - Get project items")
        
        response = await self.client.get(f"{self.base_url}/api/projects/{self.test_project_id}/items")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved {len(data)} items from project")
        else:
            print(f"❌ Failed to get project items: {response.text}")
            
        return response
    
    async def test_get_user_projects(self):
        """Test getting projects for a user"""
        if not self.test_user_id:
            print("\n⚠️ Skipping get user projects test - no user ID available")
            return None
            
        print(f"\nTesting GET /api/user/{self.test_user_id}/projects - Get user projects")
        
        response = await self.client.get(f"{self.base_url}/api/user/{self.test_user_id}/projects")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully retrieved {len(data)} projects for user")
        else:
            print(f"❌ Failed to get user projects: {response.text}")
            
        return response
    
    async def test_remove_item_from_project(self):
        """Test removing an item from a project"""
        if not self.test_project_id or not self.test_item_id or not self.test_user_id:
            print("\n⚠️ Skipping remove item from project test - missing required IDs")
            return None
            
        print(f"\nTesting DELETE /api/projects/{self.test_project_id}/items/{self.test_item_id} - Remove item from project")
        
        # Add the Content-Type header for DELETE request
        response = await self.client.delete(
            f"{self.base_url}/api/projects/{self.test_project_id}/items/{self.test_item_id}?user_id={self.test_user_id}",
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully removed item from project")
        else:
            print(f"❌ Failed to remove item from project: {response.text}")
            
        return response
    
    async def test_delete_project(self):
        """Test deleting a project"""
        if not self.test_project_id or not self.test_user_id:
            print("\n⚠️ Skipping delete project test - no project or user ID available")
            return None
            
        print(f"\nTesting DELETE /api/projects/{self.test_project_id} - Delete project")
        
        # Add the Content-Type header for DELETE request
        response = await self.client.delete(
            f"{self.base_url}/api/projects/{self.test_project_id}?user_id={self.test_user_id}",
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Successfully deleted project")
        else:
            print(f"❌ Failed to delete project: {response.text}")
            
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
