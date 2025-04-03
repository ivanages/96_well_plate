import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import textwrap
from matplotlib.colors import is_color_like

# Define plate dimensions
rows = list("ABCDEFGH")
cols = list(range(1, 13))

# Create empty dataframe for well plate layout
plate_df = pd.DataFrame(index=rows, columns=cols)
colors_df = pd.DataFrame(index=rows, columns=cols)

# Initialize session state to store category information if it's not already present
if 'categories' not in st.session_state:
    st.session_state.categories = []

# Streamlit UI
st.title("96-Well Plate Planner")

# Sidebar for sample input
category_name = st.text_input("Enter Category Name:")
category_color = st.color_picker("Choose a Color:", "#FFFFFF")  # Default color is white

# Function to validate if a color is valid
def validate_color(color):
    if color and is_color_like(color):  # Only accept valid colors
        return color
    else:
        st.warning(f"Warning: Invalid color selected. Defaulting to white color.")
        return "#FFFFFF"  # Default to white if any error occurs

# Select wells for each category
selected_wells = st.multiselect("Select Wells for Category (e.g., A1, A2, A3)", [f"{r}{c}" for r in rows for c in cols])

# Add the selected wells to the category when the button is pressed
if st.button("Assign to Wells") and category_name and selected_wells:
    valid_color = validate_color(category_color)
    st.session_state.categories.append({"name": category_name, "color": valid_color, "wells": selected_wells})

# Option to reset category assignment for a well
reset_well = st.selectbox("Select a well to reset", [f"{r}{c}" for r in rows for c in cols])
if st.button("Reset Well"):
    # Reset the category for the selected well
    for category in st.session_state.categories:
        if reset_well in category["wells"]:
            category["wells"].remove(reset_well)
            st.success(f"Well {reset_well} has been reset.")
            break

    # Remove categories that no longer have any wells
    st.session_state.categories = [category for category in st.session_state.categories if category["wells"]]

# Display all previous category assignments only if there are still wells assigned
for category in st.session_state.categories:
    if category["wells"]:  # Only display categories with assigned wells
        st.write(f"Category: {category['name']}, Color: {category['color']}, Wells: {', '.join(category['wells'])}")

# Display plate layout
fig, ax = plt.subplots(figsize=(8, 6))

# Set grid ticks and labels
ax.set_xticks(range(len(cols)))
ax.set_xticklabels(cols)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels(rows)
ax.invert_yaxis()

# Parameters for circle size
well_radius = 0.4  # Radius of the circle

# Maximum characters for text to fit in one line
max_chars_per_line = 6

# Vertical offset to increase line spacing
line_spacing = 0.15  # Increase this value to create more space between lines

# Iterate over each well and assign the appropriate color and text based on the categories
for i, row in enumerate(rows):
    for j, col in enumerate(cols):
        well_text = plate_df.loc[row, col]
        color = colors_df.loc[row, col] if colors_df.loc[row, col] else "#FFFFFF"  # Default to white if no color assigned

        # Loop through all categories and check if the current well belongs to one of them
        for category in st.session_state.categories:
            if f"{row}{col}" in category["wells"]:
                color = category["color"]  # Use the valid color from the category
                well_text = category["name"]
                break  # Stop once a category is found for this well

        # Ensure that the color is valid (not NaN)
        if not is_color_like(color):
            color = "#FFFFFF"  # Set to white if the color is invalid

        # Draw the well as a circle
        circle = plt.Circle((j + 0.5, i + 0.5), well_radius, color=color, ec='black')
        ax.add_patch(circle)

        # Handle text wrapping by splitting into lines only if the well text is a valid string
        if isinstance(well_text, str) and well_text.strip():  # Check if well_text is a non-empty string
            # Wrap text properly using textwrap
            wrapped_text = textwrap.fill(well_text, width=max_chars_per_line)

            # Split the wrapped text into lines
            lines = wrapped_text.split('\n')

            # Adjust the font size based on the number of lines
            font_size = max(10 - len(lines), 6)  # Ensure text is not too small

            # Calculate total height of the text block
            total_text_height = len(lines) * line_spacing

            # Center text vertically in the well
            for line_num, line in enumerate(lines):
                ax.text(j + 0.5, i + 0.5 + (line_num * line_spacing) - total_text_height / 2, 
                        line, ha='center', va='center', fontsize=font_size, fontname='Arial')

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
