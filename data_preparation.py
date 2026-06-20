import pandas as pd

# Load all 4 datasets
providers = pd.read_csv("providers_data.csv")
receivers = pd.read_csv("receivers_data.csv")
food_listings = pd.read_csv("food_listings_data.csv")
claims = pd.read_csv("claims_data.csv")

# ---------- 1. Check for duplicate IDs ----------
print("===== DUPLICATE ID CHECK =====")
print("Duplicate Provider_IDs:", providers["Provider_ID"].duplicated().sum())
print("Duplicate Receiver_IDs:", receivers["Receiver_ID"].duplicated().sum())
print("Duplicate Food_IDs:", food_listings["Food_ID"].duplicated().sum())
print("Duplicate Claim_IDs:", claims["Claim_ID"].duplicated().sum())
print()

# ---------- 2. Check for broken relationships (IDs that don't exist) ----------
print("===== RELATIONSHIP CHECK =====")
invalid_provider_refs = ~food_listings["Provider_ID"].isin(providers["Provider_ID"])
print("Food listings with invalid Provider_ID:", invalid_provider_refs.sum())

invalid_food_refs = ~claims["Food_ID"].isin(food_listings["Food_ID"])
print("Claims with invalid Food_ID:", invalid_food_refs.sum())

invalid_receiver_refs = ~claims["Receiver_ID"].isin(receivers["Receiver_ID"])
print("Claims with invalid Receiver_ID:", invalid_receiver_refs.sum())
print()

# ---------- 3. Fix date columns ----------
print("===== FIXING DATES =====")
food_listings["Expiry_Date"] = pd.to_datetime(food_listings["Expiry_Date"], errors="coerce")
claims["Timestamp"] = pd.to_datetime(claims["Timestamp"], errors="coerce")

print("Expiry_Date dtype after fix:", food_listings["Expiry_Date"].dtype)
print("Timestamp dtype after fix:", claims["Timestamp"].dtype)

# Check if any dates failed to convert (became NaT = Not a Time)
print("Any failed Expiry_Date conversions:", food_listings["Expiry_Date"].isna().sum())
print("Any failed Timestamp conversions:", claims["Timestamp"].isna().sum())
print()

# ---------- 4. Save cleaned versions (optional but good practice) ----------
food_listings.to_csv("food_listings_cleaned.csv", index=False)
claims.to_csv("claims_cleaned.csv", index=False)
print("Cleaned files saved: food_listings_cleaned.csv, claims_cleaned.csv")