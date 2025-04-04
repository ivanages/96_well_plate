import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import textwrap
from matplotlib.colors import is_color_like

# Define plate dimensions
rows = list("ABCDEFGH")  # A to H (8 rows)
cols = list(range(1, 13))  # 1 to 12 (12 columns)

# Create empty dataframe for well plate layout
plate_df = pd.DataFrame(index=rows, columns=cols)
colors_df = pd.DataFrame(index=rows, columns=cols)

# Initialize session state to store category information
if 'categories' not in st.session_state:
    st.session_state.categories = []

# Streamlit UI
st.title("96-Well Plate Planner")

# Sidebar for sample input
category_name = st.text_input("Enter Category Name:")
category_color = st.color_picker("Choose a Color:", "#FFFFFF")  # Default color is white

# Function to validate if a color is valid
def validate_color(color):
    if color and is_color_like(color):
        return color
    else:
        st.warning(f"Warning: Invalid color selected. Defaulting to white color.")
        return "#FFFFFF"

# Select wells for each category
selected_wells = st.multiselect("Select Wells for Category (e.g., A1, A2, A3)", [f"{r}{c}" for r in rows for c in cols])

# Add the selected wells to the category when the button is pressed
if st.button("Assign to Wells") and category_name and selected_wells:
    valid_color = validate_color(category_color)
    st.session_state.categories.append({"name": category_name, "color": valid_color, "wells": selected_wells})

# Option to reset category assignment for a well
reset_well = st.selectbox("Select a well to reset", [f"{r}{c}" for r in rows for c in cols])
if st.button("Reset Well"):
    for category in st.session_state.categories:
        if reset_well in category["wells"]:
            category["wells"].remove(reset_well)
            st.success(f"Well {reset_well} has been reset.")
            break
    st.session_state.categories = [category for category in st.session_state.categories if category["wells"]]

# Display all previous category assignments
for category in st.session_state.categories:
    if category["wells"]:  
        st.write(f"Category: {category['name']}, Color: {category['color']}, Wells: {', '.join(category['wells'])}")

# Adjust figure size and margins to ensure all wells are fully visible
fig, ax = plt.subplots(figsize=(10, 7))  

# Set grid ticks and labels
ax.set_xticks(range(1, len(cols) + 1))
ax.set_yticks(range(1, len(rows) + 1))

# Move column labels to the top
ax.set_xticklabels(cols, fontsize=12)  
ax.xaxis.set_label_position('top')  # Move labels to the top
ax.xaxis.tick_top()  

# Set row labels in the correct order (A to H) without reversing the order of wells
ax.set_yticklabels(rows[::-1], fontsize=12)

# Set the axis limits to prevent wells from going out of bounds
ax.set_xlim(0.5, len(cols) + 0.5)
ax.set_ylim(0.5, len(rows) + 0.5)
ax.set_aspect("equal")

# Well size
well_radius = 0.4  

# Iterate over each well and assign colors
for i, row in enumerate(rows):
    for j, col in enumerate(cols):
        color = "#FFFFFF"
        well_text = ""  # Default to no text

        # Check if well is assigned to a category
        for category in st.session_state.categories:
            if f"{row}{col}" in category["wells"]:
                color = category["color"]
                well_text = category["name"]  # Store category name for text label
                break  

        # Draw the well as a circle
        circle = plt.Circle((j + 1, len(rows) - i), well_radius, color=color, ec='black', lw=1)
        ax.add_patch(circle)

        # Add text label inside the well (Arial font, non-bold)
        ax.text(j + 1, len(rows) - i, 
                "\n".join(textwrap.wrap(well_text, width=5)),  # Wrap text for long names
                ha='center', va='center', fontsize=8, color='black', fontname="Arial")

# Show the plot
st.pyplot(fig)

# Download option (as CSV)
st.download_button("Download Layout as CSV", plate_df.to_csv().encode(), "plate_layout.csv", "text/csv")

# Save the plot as a JPEG image and provide a download button
def save_as_jpeg(fig):
    from io import BytesIO
    buf = BytesIO()
    fig.savefig(buf, format="jpeg", bbox_inches="tight", dpi=300)
    buf.seek(0)
    return buf

jpeg_buf = save_as_jpeg(fig)
st.download_button(
    label="Download Layout as JPEG",
    data=jpeg_buf,
    file_name="plate_layout.jpeg",
    mime="image/jpeg"
)
