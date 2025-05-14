from abc import ABC, abstractmethod
import datetime
import json
from datetime import datetime
import time

class Product(ABC):
    def __init__(self, product_id, name, price, quantity_in_stock):
        self._product_id = product_id
        self._name = name
        self._price = price
        self._quantity_in_stock = quantity_in_stock

    
    @abstractmethod
    def restock(self, amount):
        pass

    @abstractmethod
    def sell(self, quantity):
        pass

    def get_total_value(self):
        return self._price * self._quantity_in_stock
    
    @abstractmethod
    def __str__(self): # type: ignore
        pass


class Electronics(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, warranty, brand):
        super().__init__(product_id, name, price, quantity_in_stock) 
        self._warranty  = warranty
        self._brand = brand

    def restock(self, amount):
        if amount > 0:
            self._quantity_in_stock += amount

    def sell(self, quantity): # type: ignore
        if quantity <= self._quantity_in_stock:
            self._quantity_in_stock -= quantity
            return True
        return False
    
    def __str__(self): # type: ignore
        return (f"Electronics - ID: {self._product_id}, Name: {self._name}, "
                f"Brand: {self._brand}, Price: ${self._price}, "
                f"Stock: {self._quantity_in_stock}, Warranty: {self._warranty} years")

class Grocery(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, expiry_date):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d").date()

    def isExpired(self):
        return datetime.now().date() > self._expiry_date

    def restock(self, amount):
        if amount > 0:
            self.restock += amount

    def sell(self, quantity): # type: ignore
        if self.isExpired():
            raise Exception("Product has been Expried")
        if quantity <= self._quantity_in_stock:
            self._quantity_in_stock -= quantity
        else:
            raise Exception("Stocks not available")
        
    
    def __str__(self): # type: ignore
        return f"[Grocery] {self._name} | Expiry: {self._expiry_date} | Stock: {self._quantity_in_stock}"

class Clothing(Product):
    def __init__(self, product_id, name, price, quantity_in_stock, size, material):
        super().__init__(product_id, name, price, quantity_in_stock)
        self._size = size
        self._material = material

    def restock(self, amount):
        if amount > 0:
            self._quantity_in_stock += amount
            return True
        return False

    def sell(self, quantity):
        if quantity <= self._quantity_in_stock:
            self._quantity_in_stock -= quantity
            return True
        return False

    def __str__(self):
        return (f"Clothing - ID: {self._product_id}, Name: {self._name}, "
                f"Size: {self._size}, Material: {self._material}, "
                f"Price: ${self._price}, Stock: {self._quantity_in_stock}")
            
class Inventory:
    def __init__(self):
        self._products = {}  # product_id -> product object

    def add_product(self, product):
        if product._product_id in self._products:
            raise DuplicateProductError(f"Product ID {product._product_id} already exists")
        self._products[product._product_id] = product

    def remove_product(self, product_id):
        if product_id in self._products:
            del self._products[product_id]
            return True
        return False

    def search_by_name(self, name):
        return [p for p in self._products.values() if name.lower() in p._name.lower()]

    def search_by_type(self, product_type):
        return [p for p in self._products.values() if isinstance(p, product_type)]

    def list_all_products(self):
        return list(self._products.values())

    def sell_product(self, product_id, quantity):
        if product_id not in self._products:
            raise ProductNotFoundError(f"Product ID {product_id} not found")
        
        product = self._products[product_id]
        if not product.sell(quantity):
            raise InsufficientStockError(f"Not enough stock for product {product_id}")
        return True

    def restock_product(self, product_id, quantity):
        if product_id not in self._products:
            raise ProductNotFoundError(f"Product ID {product_id} not found")
        
        product = self._products[product_id]
        if not product.restock(quantity):
            raise InvalidRestockError(f"Cannot restock product {product_id}")
        return True

    def total_inventory_value(self):
        return sum(p.get_total_value() for p in self._products.values())

    def remove_expired_products(self):
        expired = [pid for pid, p in self._products.items() 
                 if isinstance(p, Grocery) and p.is_expired()]
        for pid in expired:
            del self._products[pid]
        return len(expired)

    def save_to_file(self, filename):
        data = []
        for product in self._products.values():
            prod_data = {
                'type': product.__class__.__name__,
                'id': product._product_id,
                'name': product._name,
                'price': product._price,
                'stock': product._quantity_in_stock
            }
            
            # Extra attributes based on type
            if isinstance(product, Electronics):
                prod_data.update({
                    'warranty': product._warranty_years,
                    'brand': product._brand
                })
            elif isinstance(product, Grocery):
                prod_data.update({
                    'expiry': product._expiry_date.strftime("%Y-%m-%d")
                })
            elif isinstance(product, Clothing):
                prod_data.update({
                    'size': product._size,
                    'material': product._material
                })
                
            data.append(prod_data)
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load_from_file(self, filename):
        with open(filename, 'r') as f:
            data = json.load(f)
        
        self._products = {}
        for item in data:
            try:
                if item['type'] == 'Electronics':
                    product = Electronics(
                        item['id'], item['name'], item['price'], item['stock'],
                        item['warranty'], item['brand']
                    )
                elif item['type'] == 'Grocery':
                    product = Grocery(
                        item['id'], item['name'], item['price'], item['stock'],
                        item['expiry']
                    )
                elif item['type'] == 'Clothing':
                    product = Clothing(
                        item['id'], item['name'], item['price'], item['stock'],
                        item['size'], item['material']
                    )
                else:
                    continue
                    
                self._products[product._product_id] = product
            except (KeyError, ValueError) as e:
                print(f"Error loading product: {e}")
                continue

def display_menu():
    print("\nInventory Management System")
    print("1. Add Product")
    print("2. Sell Product")
    print("3. Search Products")
    print("4. View All Products")
    print("5. Save Inventory")
    print("6. Load Inventory")
    print("7. Remove Expired Groceries")
    print("8. Show Total Inventory Value")
    print("9. Exit")

def get_product_input():
    print("\nSelect Product Type:")
    print("1. Electronics")
    print("2. Grocery")
    print("3. Clothing")
    choice = input("Enter type (1-3): ")
    
    product_id = input("Enter product ID: ")
    name = input("Enter product name: ")
    price = float(input("Enter price: "))
    quantity = int(input("Enter initial quantity: "))
    
    if choice == '1':
        warranty = int(input("Enter warranty years: "))
        brand = input("Enter brand: ")
        return Electronics(product_id, name, price, quantity, warranty, brand)
    elif choice == '2':
        expiry = input("Enter expiry date (YYYY-MM-DD): ")
        return Grocery(product_id, name, price, quantity, expiry)
    elif choice == '3':
        size = input("Enter size: ")
        material = input("Enter material: ")
        return Clothing(product_id, name, price, quantity, size, material)
    else:
        print("Invalid choice")
        return None

def main():
    inventory = Inventory()
    
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-9): ")
        
        try:
            if choice == '1':  # Add Product
                product = get_product_input()
                if product:
                    inventory.add_product(product)
                    print("Product added successfully!")
                    
            elif choice == '2':  # Sell Product
                product_id = input("Enter product ID to sell: ")
                quantity = int(input("Enter quantity to sell: "))
                if inventory.sell_product(product_id, quantity):
                    print("Sale completed successfully!")
                    
            elif choice == '3':  # Search Products
                print("\nSearch Options:")
                print("1. By Name")
                print("2. By Type")
                search_choice = input("Enter search option (1-2): ")
                
                if search_choice == '1':
                    name = input("Enter product name to search: ")
                    results = inventory.search_by_name(name)
                elif search_choice == '2':
                    print("\nProduct Types:")
                    print("1. Electronics")
                    print("2. Grocery")
                    print("3. Clothing")
                    type_choice = input("Enter type to search (1-3): ")
                    
                    if type_choice == '1':
                        results = inventory.search_by_type(Electronics)
                    elif type_choice == '2':
                        results = inventory.search_by_type(Grocery)
                    elif type_choice == '3':
                        results = inventory.search_by_type(Clothing)
                    else:
                        print("Invalid choice")
                        continue
                else:
                    print("Invalid choice")
                    continue
                
                if results:
                    print("\nSearch Results:")
                    for product in results:
                        print(product)
                else:
                    print("No products found")
                    
            elif choice == '4':  # View All Products
                products = inventory.list_all_products()
                if products:
                    print("\nAll Products:")
                    for product in products:
                        print(product)
                else:
                    print("Inventory is empty")
                    
            elif choice == '5':  # Save Inventory
                filename = input("Enter filename to save: ")
                inventory.save_to_file(filename)
                print(f"Inventory saved to {filename}")
                
            elif choice == '6':  # Load Inventory
                filename = input("Enter filename to load: ")
                inventory.load_from_file(filename)
                print(f"Inventory loaded from {filename}")
                
            elif choice == '7':  # Remove Expired Groceries
                count = inventory.remove_expired_products()
                print(f"Removed {count} expired grocery items")
                
            elif choice == '8':  # Total Inventory Value
                total = inventory.total_inventory_value()
                print(f"Total inventory value: ${total:.2f}")
                
            elif choice == '9':  # Exit
                print("Exiting program...")
                break
                
            else:
                print("Invalid choice. Please try again.")
                
        except InventoryError as e:
            print(f"Error: {e}")
        except ValueError:
            print("Error: Invalid input format")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
    
    