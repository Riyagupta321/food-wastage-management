import streamlit as st
import sqlite3
import pandas as pd

# Page setup
st.set_page_config(page_title="Local Food Wastage Management", layout="wide")

st.title("🍱 Local Food Wastage Management System")
st.write("Connecting surplus food providers with people who need it.")

# Connect to our database
conn = sqlite3.connect("food_wastage.db", check_same_thread=False)

# Create 4 tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Filter Listings",
    "📊 SQL Insights",
    "📞 Contact Providers",
    "✏️ Manage Records"
])

# ---------- TAB 1: Filter Listings ----------
with tab1:
    st.subheader("Browse Available Food Listings")

    # Get unique values for filter dropdowns
    cities = pd.read_sql_query("SELECT DISTINCT Location FROM food_listings ORDER BY Location", conn)
    providers_list = pd.read_sql_query("SELECT DISTINCT Provider_Type FROM food_listings ORDER BY Provider_Type", conn)
    food_types = pd.read_sql_query("SELECT DISTINCT Food_Type FROM food_listings ORDER BY Food_Type", conn)
    meal_types = pd.read_sql_query("SELECT DISTINCT Meal_Type FROM food_listings ORDER BY Meal_Type", conn)

    # Create 4 filter dropdowns side by side
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_city = st.selectbox("City", ["All"] + cities["Location"].tolist())
    with col2:
        selected_provider_type = st.selectbox("Provider Type", ["All"] + providers_list["Provider_Type"].tolist())
    with col3:
        selected_food_type = st.selectbox("Food Type", ["All"] + food_types["Food_Type"].tolist())
    with col4:
        selected_meal_type = st.selectbox("Meal Type", ["All"] + meal_types["Meal_Type"].tolist())

    # Build the SQL query based on selected filters
    query = "SELECT * FROM food_listings WHERE 1=1"
    params = []

    if selected_city != "All":
        query += " AND Location = ?"
        params.append(selected_city)
    if selected_provider_type != "All":
        query += " AND Provider_Type = ?"
        params.append(selected_provider_type)
    if selected_food_type != "All":
        query += " AND Food_Type = ?"
        params.append(selected_food_type)
    if selected_meal_type != "All":
        query += " AND Meal_Type = ?"
        params.append(selected_meal_type)

    filtered_df = pd.read_sql_query(query, conn, params=params)

    st.write(f"**{len(filtered_df)} results found**")
    st.dataframe(filtered_df, use_container_width=True)

    # ---------- TAB 2: SQL Insights ----------
with tab2:
 st.subheader("Data Analysis & Insights (15 SQL Queries)")

 query_options = {
        "1a. Providers per City": """
            SELECT City, COUNT(*) AS Total_Providers FROM providers
            GROUP BY City ORDER BY Total_Providers DESC;
        """,
        "1b. Receivers per City": """
            SELECT City, COUNT(*) AS Total_Receivers FROM receivers
            GROUP BY City ORDER BY Total_Receivers DESC;
        """,
        "2. Food Contribution by Provider Type": """
            SELECT Provider_Type, SUM(Quantity) AS Total_Quantity FROM food_listings
            GROUP BY Provider_Type ORDER BY Total_Quantity DESC;
        """,
        "4. Top Receivers by Total Claims": """
            SELECT r.Name, r.Type, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            GROUP BY r.Receiver_ID ORDER BY Total_Claims DESC LIMIT 10;
        """,
        "5. Total Food Available": """
            SELECT SUM(Quantity) AS Total_Food_Available FROM food_listings;
        """,
        "6. Top Cities by Food Listings": """
            SELECT Location AS City, COUNT(*) AS Total_Listings FROM food_listings
            GROUP BY Location ORDER BY Total_Listings DESC LIMIT 10;
        """,
        "7. Most Common Food Types": """
            SELECT Food_Type, COUNT(*) AS Total_Items FROM food_listings
            GROUP BY Food_Type ORDER BY Total_Items DESC;
        """,
        "8. Claims per Food Item": """
            SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY f.Food_Name ORDER BY Total_Claims DESC;
        """,
        "9. Top Providers by Successful Claims": """
            SELECT p.Name AS Provider_Name, COUNT(c.Claim_ID) AS Successful_Claims
            FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            JOIN providers p ON f.Provider_ID = p.Provider_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID ORDER BY Successful_Claims DESC LIMIT 10;
        """,
        "10. Claims Status Breakdown (%)": """
            SELECT Status, COUNT(*) AS Total,
                   ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims), 2) AS Percentage
            FROM claims GROUP BY Status;
        """,
        "11. Avg Quantity Claimed per Receiver": """
            SELECT r.Name AS Receiver_Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
            FROM claims c
            JOIN food_listings f ON c.Food_ID = f.Food_ID
            JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
            GROUP BY r.Receiver_ID ORDER BY Avg_Quantity_Claimed DESC LIMIT 10;
        """,
        "12. Claims by Meal Type": """
            SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
            FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY f.Meal_Type ORDER BY Total_Claims DESC;
        """,
        "13. Total Quantity Donated per Provider": """
            SELECT p.Name AS Provider_Name, SUM(f.Quantity) AS Total_Quantity_Donated
            FROM food_listings f JOIN providers p ON f.Provider_ID = p.Provider_ID
            GROUP BY p.Provider_ID ORDER BY Total_Quantity_Donated DESC LIMIT 10;
        """,
        "14. Food Items Closest to Expiry": """
            SELECT f.Food_Name, f.Quantity, f.Expiry_Date, p.Name AS Provider_Name
            FROM food_listings f JOIN providers p ON f.Provider_ID = p.Provider_ID
            ORDER BY f.Expiry_Date ASC LIMIT 10;
        """,
        "15. Cities by Claim Cancellation Rate": """
            SELECT f.Location AS City, COUNT(*) AS Total_Claims,
                   SUM(CASE WHEN c.Status = 'Cancelled' THEN 1 ELSE 0 END) AS Cancelled_Claims,
                   ROUND(SUM(CASE WHEN c.Status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS Cancellation_Rate_Percent
            FROM claims c JOIN food_listings f ON c.Food_ID = f.Food_ID
            GROUP BY f.Location HAVING COUNT(*) >= 3
            ORDER BY Cancellation_Rate_Percent DESC LIMIT 10;
        """,
    }

 selected_query = st.selectbox("Choose a query to view:", list(query_options.keys()))

 result_df = pd.read_sql_query(query_options[selected_query], conn)
 st.dataframe(result_df, use_container_width=True)   
 with tab3:

    st.subheader("Provider Contact Directory")
    st.write("Find providers in your city and get their contact details directly.")

    cities_for_contact = pd.read_sql_query(
        "SELECT DISTINCT City FROM providers ORDER BY City", conn
    )

    selected_contact_city = st.selectbox(
        "Select a city to find providers:",
        cities_for_contact["City"].tolist(),
        key="contact_city_select"
    )

    contact_query = """
        SELECT Name, Type, Address, Contact
        FROM providers
        WHERE City = ?;
    """
    contact_df = pd.read_sql_query(contact_query, conn, params=(selected_contact_city,))

    st.write(f"**{len(contact_df)} provider(s) found in {selected_contact_city}**")
    st.dataframe(contact_df, use_container_width=True)

# ---------- TAB 4: Manage Records ----------
with tab4:
    st.subheader("Add / Edit / Delete Food Listings")

    crud_action = st.radio(
        "Choose an action:",
        ["Add New Listing", "View All Listings", "Update Listing", "Delete Listing"],
        horizontal=True
    )

    # ----- ADD -----
    if crud_action == "Add New Listing":
        st.write("### Add a New Food Listing")

        with st.form("add_form"):
            food_name = st.text_input("Food Name")
            quantity = st.number_input("Quantity", min_value=1, step=1)
            expiry_date = st.date_input("Expiry Date")
            provider_id = st.number_input("Provider ID", min_value=1, step=1)
            provider_type = st.text_input("Provider Type")
            location = st.text_input("Location (City)")
            food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"])

            submitted = st.form_submit_button("Add Listing")

            if submitted:
                cursor = conn.cursor()
                cursor.execute("SELECT MAX(Food_ID) FROM food_listings")
                max_id = cursor.fetchone()[0]
                new_id = (max_id or 0) + 1

                cursor.execute("""
                    INSERT INTO food_listings
                    (Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (new_id, food_name, quantity, str(expiry_date), provider_id, provider_type, location, food_type, meal_type))
                conn.commit()
                st.success(f"✅ Listing added successfully with Food_ID = {new_id}")

    # ----- VIEW -----
    elif crud_action == "View All Listings":
        st.write("### All Food Listings")
        all_df = pd.read_sql_query("SELECT * FROM food_listings", conn)
        st.dataframe(all_df, use_container_width=True)

    # ----- UPDATE -----
    elif crud_action == "Update Listing":
        st.write("### Update an Existing Listing")

        food_id_to_update = st.number_input("Enter Food_ID to update", min_value=1, step=1, key="update_id")

        existing = pd.read_sql_query(
            "SELECT * FROM food_listings WHERE Food_ID = ?", conn, params=(food_id_to_update,)
        )

        if existing.empty:
            st.warning("No listing found with this Food_ID.")
        else:
            st.write("Current details:")
            st.dataframe(existing, use_container_width=True)

            with st.form("update_form"):
                new_quantity = st.number_input("New Quantity", min_value=1, step=1, value=int(existing["Quantity"].iloc[0]))
                new_food_type = st.selectbox("New Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])

                update_submitted = st.form_submit_button("Update Listing")

                if update_submitted:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE food_listings
                        SET Quantity = ?, Food_Type = ?
                        WHERE Food_ID = ?
                    """, (new_quantity, new_food_type, food_id_to_update))
                    conn.commit()
                    st.success(f"✅ Food_ID {food_id_to_update} updated successfully.")

    # ----- DELETE -----
    elif crud_action == "Delete Listing":
        st.write("### Delete a Listing")

        food_id_to_delete = st.number_input("Enter Food_ID to delete", min_value=1, step=1, key="delete_id")

        existing_del = pd.read_sql_query(
            "SELECT * FROM food_listings WHERE Food_ID = ?", conn, params=(food_id_to_delete,)
        )

        if existing_del.empty:
            st.warning("No listing found with this Food_ID.")
        else:
            st.write("This listing will be deleted:")
            st.dataframe(existing_del, use_container_width=True)

            if st.button("🗑️ Confirm Delete"):
                cursor = conn.cursor()
                cursor.execute("DELETE FROM food_listings WHERE Food_ID = ?", (food_id_to_delete,))
                conn.commit()
                st.success(f"✅ Food_ID {food_id_to_delete} deleted successfully.")