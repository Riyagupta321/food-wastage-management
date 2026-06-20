import sqlite3
import pandas as pd

# Connect to our database
conn = sqlite3.connect("food_wastage.db")

# ===== QUESTION 1: Har city mein kitne food providers aur receivers hain? =====

query1a = """
SELECT City, COUNT(*) AS Total_Providers
FROM providers
GROUP BY City
ORDER BY Total_Providers DESC;
"""

result1a = pd.read_sql_query(query1a, conn)
print("===== Providers per City =====")
print(result1a)
print()

query1b = """
SELECT City, COUNT(*) AS Total_Receivers
FROM receivers
GROUP BY City
ORDER BY Total_Receivers DESC;
"""

result1b = pd.read_sql_query(query1b, conn)
print("===== Receivers per City =====")
print(result1b)
# ===== QUESTION 2: Kaunsa provider type sabse zyada food contribute karta hai? =====

query2 = """
SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
FROM food_listings
GROUP BY Provider_Type
ORDER BY Total_Quantity DESC;
"""

result2 = pd.read_sql_query(query2, conn)
print("===== Food Contribution by Provider Type =====")
print(result2)
print()
# ===== QUESTION 3: Kisi specific city mein providers ki contact info =====

city_name = "New Carol"   # yahan koi bhi city ka naam daal sakte ho

query3 = """
SELECT Name, Type, Address, Contact
FROM providers
WHERE City = ?;
"""

result3 = pd.read_sql_query(query3, conn, params=(city_name,))
print(f"===== Providers in {city_name} =====")
print(result3)
print()
# ===== QUESTION 4: Kaunse receivers ne sabse zyada food claim kiya? =====

query4 = """
SELECT r.Name, r.Type, COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Receiver_ID
ORDER BY Total_Claims DESC
LIMIT 10;
"""

result4 = pd.read_sql_query(query4, conn)
print("===== Top 10 Receivers by Total Claims =====")
print(result4)
print()
# ===== QUESTION 5: Total quantity of food available =====

query5 = """
SELECT SUM(Quantity) AS Total_Food_Available
FROM food_listings;
"""

result5 = pd.read_sql_query(query5, conn)
print("===== Total Food Available (all providers) =====")
print(result5)
print()
# ===== QUESTION 6: Kaunse city mein sabse zyada food listings hain? =====

query6 = """
SELECT Location AS City, COUNT(*) AS Total_Listings
FROM food_listings
GROUP BY Location
ORDER BY Total_Listings DESC
LIMIT 10;
"""

result6 = pd.read_sql_query(query6, conn)
print("===== Top 10 Cities by Food Listings =====")
print(result6)
print()
# ===== QUESTION 7: Sabse common food types =====

query7 = """
SELECT Food_Type, COUNT(*) AS Total_Items
FROM food_listings
GROUP BY Food_Type
ORDER BY Total_Items DESC;
"""

result7 = pd.read_sql_query(query7, conn)
print("===== Most Common Food Types =====")
print(result7)
print()
# ===== QUESTION 8: Har food item ke liye kitne claims hue =====

query8 = """
SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Food_Name
ORDER BY Total_Claims DESC;
"""

result8 = pd.read_sql_query(query8, conn)
print("===== Claims per Food Item =====")
print(result8)
print()
# ===== QUESTION 9: Kaunse provider ke sabse zyada successful claims hue =====

query9 = """
SELECT p.Name AS Provider_Name, COUNT(c.Claim_ID) AS Successful_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
JOIN providers p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID
ORDER BY Successful_Claims DESC
LIMIT 10;
"""

result9 = pd.read_sql_query(query9, conn)
print("===== Top 10 Providers by Successful Claims =====")
print(result9)
print()
# ===== QUESTION 10: % of claims completed vs pending vs cancelled =====

query10 = """
SELECT Status, COUNT(*) AS Total,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
FROM claims
GROUP BY Status;
"""

result10 = pd.read_sql_query(query10, conn)
print("===== Claims Status Breakdown =====")
print(result10)
print()
# ===== QUESTION 11: Average quantity claimed per receiver =====

query11 = """
SELECT r.Name AS Receiver_Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.Receiver_ID
ORDER BY Avg_Quantity_Claimed DESC
LIMIT 10;
"""

result11 = pd.read_sql_query(query11, conn)
print("===== Top 10 Receivers by Average Quantity Claimed =====")
print(result11)
print()
# ===== QUESTION 12: Kaunsa meal type sabse zyada claim hota hai =====

query12 = """
SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Meal_Type
ORDER BY Total_Claims DESC;
"""

result12 = pd.read_sql_query(query12, conn)
print("===== Claims by Meal Type =====")
print(result12)
print()
# ===== QUESTION 13: Total quantity donated by each provider =====

query13 = """
SELECT p.Name AS Provider_Name, SUM(f.Quantity) AS Total_Quantity_Donated
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Provider_ID
ORDER BY Total_Quantity_Donated DESC
LIMIT 10;
"""

result13 = pd.read_sql_query(query13, conn)
print("===== Top 10 Providers by Total Quantity Donated =====")
print(result13)
print()
# ===== QUESTION 14: Food items closest to expiry (not yet claimed as Completed) =====

query14 = """
SELECT f.Food_Name, f.Quantity, f.Expiry_Date, p.Name AS Provider_Name
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
ORDER BY f.Expiry_Date ASC
LIMIT 10;
"""

result14 = pd.read_sql_query(query14, conn)
print("===== 10 Food Items Closest to Expiry =====")
print(result14)
print()

# ===== QUESTION 15: City with highest claim cancellation rate =====

query15 = """
SELECT f.Location AS City,
       COUNT(*) AS Total_Claims,
       SUM(CASE WHEN c.Status = 'Cancelled' THEN 1 ELSE 0 END) AS Cancelled_Claims,
       ROUND(SUM(CASE WHEN c.Status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Cancellation_Rate_Percent
FROM claims c
JOIN food_listings f ON c.Food_ID = f.Food_ID
GROUP BY f.Location
HAVING COUNT(*) >= 3
ORDER BY Cancellation_Rate_Percent DESC
LIMIT 10;
"""

result15 = pd.read_sql_query(query15, conn)
print("===== Top 10 Cities by Claim Cancellation Rate (min 3 claims) =====")
print(result15)
print()
conn.close()
