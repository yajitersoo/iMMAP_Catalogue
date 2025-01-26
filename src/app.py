import dash
import os
import pandas as pd
import openpyxl
from dash import Dash, html, dcc, Input, Output, State, no_update, callback_context

import os
import pandas as pd


def load_product_data():
    # Determine the correct file path dynamically
    script_dir = os.path.dirname(os.path.abspath(__file__))  # Get the script's directory
    file_path = os.path.join(script_dir, 'assets', 'products.xlsx')

    print(f"Looking for file at: {file_path}")  # Debugging

    try:
        # Load the Excel file with openpyxl engine
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"Excel file loaded successfully from {file_path}")

        # Fill missing values and ensure category is string
        df['Category'] = df['Category'].fillna('Unknown').astype(str)
        return df.to_dict('records')

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return []  # Return empty list if file is missing

    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return []  # Handle any other errors gracefully


# Create Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=['/assets/style.css'],  # Dash automatically serves files from 'assets' folder
    suppress_callback_exceptions=True
)

# Expose the Flask server instance for deployment
server = app.server
app.title = "iMMAP Product Catalogue"

# Load products from Excel
products = load_product_data()

# Get unique categories from the data
categories = list(set([product["Category"].lower().replace(" ", "-") for product in products]))

# # Get unique sector values for the first dropdown
# unique_sectors = df['Sector'].unique()


# Prepare homepage product catalog (keeps all products complete)
product_catalog = [
    {
        "title": cat.replace("-", " ").title(),
        "image_url": next((p["Image_URL"] for p in products if p["Category"].lower().replace(" ", "-") == cat), ""),
        "link": f"/{cat}"
    }
    for cat in categories
]

# Carousel images
carousel_images = [
    "/assets/image1.jpg",
    "/assets/image2.jpg",
    "/assets/image3.jpg",
    "/assets/image4.jpg"
]

# Layout for the app
app.layout = html.Div(
    [
        dcc.Location(id='url', refresh=False),

        # Store components to track carousel index and fade trigger
        dcc.Store(id='carousel-index', data=0),
        # html.Link(rel='stylesheet', href='/assets/style.css'),
        # Top Bar
        html.Div(
            [
                html.Div(
                    [

                        html.Div(
                            "iMMAP Inc Product Catalogue",
                            className="top-bar-title",
                            style={"textAlign": "center", "fontSize": "24px", "fontWeight": "bold", "flexGrow": "1"}
                        ),
                        html.Div(
                            [
                                html.A("Email us: nigeria@immap.org", href="mailto:nigeria@immap.org", className="top-bar-link",
                                       style={"fontSize": "8px", "fontWeight": "normal"}),
                                html.Div("Call us: (258) 84 564 5353", className="top-bar-text",
                                         style={"marginTop": "5px", "fontSize": "8px", "fontWeight": "normal"})
                            ],
                            className="top-bar-contact",
                            style={"display": "flex", "flexDirection": "column", "alignItems": "center"}
                        ),
                    ],
                    className="top-bar-content",
                    style={"display": "flex", "alignItems": "center", "justifyContent": "space-between",
                           "width": "100%"}
                ),
            ],
            className="top-bar",
        ),

        # Logo and Navigation with active tab handling via Dash callback
        html.Div(
            [
                html.Div(
                    html.Img(
                        src="/assets/immap_usaid_logo.png",
                        alt="iMMAP and USAID Logo",
                        className="logo"
                    ),
                    className="logo-container",
                ),
                html.Div(
                    id="nav-menu",
                    children=[
                        html.A("Home", href="/", className="nav-link", id="nav-home"),
                        *[
                            html.A(
                                product["title"],
                                href=product["link"],
                                className="nav-link",
                                id=f"nav-{product['link'].strip('/')}"
                            )
                            for product in product_catalog
                        ],
                    ],
                    className="nav-links",
                ),
            ],
            className="logo-nav-bar",
        ),

        # Dynamic content container
        html.Div(id='page-content', className="content"),

        # Footer (Unchanged)
        html.Footer(
            [
                html.Div(
                    [
                        html.P("Copyright © 2025. Developed by iMMAP Inc."),
                        html.Div(
                            [
                                html.A(
                                    html.Img(
                                        src="/assets/twitter-icon.png",
                                        alt="Twitter",
                                        className="social-icon"
                                    ),
                                    href="https://twitter.com/iMMAP_Inc",
                                    target="_blank",
                                    className="social-link"
                                ),
                                html.A(
                                    html.Img(
                                        src="/assets/youtube-icon.png",
                                        alt="YouTube",
                                        className="social-icon"
                                    ),
                                    href="https://www.youtube.com/channel/UCA2uVXRWcJOkNcOD0svYxOg",
                                    target="_blank",
                                    className="social-link"
                                ),
                                html.A(
                                    html.Img(
                                        src="/assets/linkedin-icon.png",
                                        alt="LinkedIn",
                                        className="social-icon"
                                    ),
                                    href="https://www.linkedin.com/company/immap",
                                    target="_blank",
                                    className="social-link"
                                ),
                                html.A(
                                    html.Img(
                                        src="/assets/facebook-icon.png",
                                        alt="Facebook",
                                        className="social-icon"
                                    ),
                                    href="https://www.facebook.com/immap.org/",
                                    target="_blank",
                                    className="social-link"
                                ),
                            ],
                            className="social-links",
                        ),
                    ],
                    className="footer-content",
                ),
            ],
            className="footer",
        )

    ],
    className="container",
)


# Homepage layout (keeping all products)
def homepage():
    return html.Div([
        # Store components (Ensuring presence for callback reference)
        dcc.Store(id='carousel-index', data=0),
        dcc.Store(id='fade-trigger', data=False),

        # Carousel Section
        html.Div(
            [
                html.Button("❮", id="prev-btn", className="carousel-btn prev-btn", n_clicks=0),
                html.Div(
                    id="carousel-wrapper",
                    children=[
                        html.Img(
                            id="carousel-image",
                            src=carousel_images[0],
                            className="carousel-image fade"
                        )
                    ],
                ),

                # html.Img(src=item["image"], className="carousel-image"),
                html.Div(
                    [
                        html.Div(  # Wrapper with black tint background
                            [
                                html.H2("Better Data | Better Decisions | Better Outcomes", className="carousel-heading"),
                                html.P("We support humanitarian actors to solve operational and strategic challenges. "
                                       "Our pioneering approach facilitates informed and effective emergency preparedness, "
                                       "humanitarian response, and development aid activities by enabling evidence-based decision-making for UN agencies, "
                                       "humanitarian cluster/sector leads, NGOs, and government operations."),
                                html.A("Know More", href="https://immap.org/who-we-are/",target="_blank", className="carousel-button"),
                            ],
                            className="carousel-overlay"
                        ),
                    ],
                    className="carousel-content",
                ),

                html.Button("❯", id="next-btn", className="carousel-btn next-btn", n_clicks=0),
                dcc.Interval(id="carousel-timer", interval=5000, n_intervals=0),
            ],
            className="carousel",
        ),

        # Product Catalogue Section
        html.Div(
            [
                html.H2("Product Catalogue", className="section-heading"),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Img(src=product["image_url"], className="course-image"),
                                html.H4(product["title"], className="course-title"),
                                html.A("View Products", href=product["link"], className="course-link"),
                            ],
                            className="course-card",
                        )
                        for product in product_catalog
                    ],
                    className="course-row",
                ),
            ],
            className="promoted-courses-section",
        ),
    ], className="homepage-content")


# Product pages with dropdown selection
def product_page(category):
    formatted_category = category.lower().replace(" ", "-")
    # products_for_category = [
    #     p for p in products if p["Category"].lower().replace(" ", "-") == formatted_category
    # ]
    products_for_category = list({p["Sector"]: p for p in products
                                  if p["Category"].lower().replace(" ", "-") == formatted_category}.values())

    if products_for_category:
        # Get options for the dropdowns
        titles = sorted(set([p["Title"] for p in products_for_category]))
        sectors = sorted(set([p["Sector"] for p in products_for_category]))
        years = sorted(set([p["Year"] for p in products_for_category]))
        return html.Div([
            # Store section-head (category) in a hidden store within the function
            dcc.Store(id='stored-section-head', data=products_for_category[0]["Category"]),

            html.H2(products_for_category[0]["Category"], className="section-heading"),

        # Product selection dropdown
        html.Div([
            html.Div([
                html.Label("Sector:", className="dropdown-label"),
                dcc.Dropdown(
                    id="sector-dropdown",
                    options=[{"label": p["Sector"], "value": p["Sector"]} for p in products_for_category],
                    value=sectors[0],
                    placeholder="Select Sector",
                    style={'width': '250px'}
                ),
            ], className="dropdown-container"),

            html.Div([
                html.Label("Year:", className="dropdown-label"),
                dcc.Dropdown(
                    id="year-dropdown",
                    placeholder="Select Year",
                    disabled=True,  # Initially disabled
                    style={'width': '250px'},
                    value=years[0],
                ),
            ], className="dropdown-container"),

            html.Div([
                html.Label("Product Title:", className="dropdown-label"),
                dcc.Dropdown(
                    id="product-dropdown",
                    placeholder="Select Product Title",
                    disabled=True,  # Initially disabled
                    value=titles[0],
                    style={'width': '250px'}
                ),
            ], className="dropdown-container"),
        ], className="dropdown-row", style={'display': 'flex', 'gap': '20px', 'alignItems': 'center'}),

            html.Iframe(id="product-iframe", style={'width': '100%', 'height': '80vh', 'border': 'none'}),

            # Return link
            html.Div(html.A("← Return to Homepage", href="/", className="back-link"),
                     style={'textAlign': 'center', 'marginTop': '20px'}),

            # Floating "About Product" section
            html.Div(id="floating-about", className="floating-about")
        ])

    return homepage()


# Callback to update page content when clicking "View Products"
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def update_page_content(pathname):
    print(f"Current URL Pathname: {pathname}")
    category = pathname.strip("/")
    if category in [p["link"].strip("/") for p in product_catalog]:
        return product_page(category)

    return homepage()

@app.callback(
    Output('product-iframe', 'src'),
    [
        Input('sector-dropdown', 'value'),
        Input('year-dropdown', 'value'),
        Input('product-dropdown', 'value')
    ],
    [State('stored-section-head', 'data')]  # Retrieve section-head from store
)
def update_product_page(selected_sector, selected_year, selected_product, selected_section_head):
    # If any dropdown (sector, year, product) or section-head is not selected, return default URL
    if not selected_product or not selected_sector or not selected_year or not selected_section_head:
        return "/assets/loading.html"  # Default URL when no valid selection is made

    # Proceed to filter and set iframe URL if all selections are made
    filtered_data = [
        p for p in products
        if p['Title'] == selected_product and
           p['Sector'] == selected_sector and
           p['Year'] == selected_year and
           p['Category'] == selected_section_head
    ]

    # If a matching entry is found, return the URL for the iframe
    if filtered_data:
        return filtered_data[0]['URL']

    # If no valid selection or no match is found, return a default URL with no data
    return "/assets/loading.html"  # Default URL when no valid data is available



# Callback to update the year and title dropdowns based on selected sector
@app.callback(
    [Output('year-dropdown', 'options'),
     Output('year-dropdown', 'disabled')],
    [Input('sector-dropdown', 'value')],
    [State('stored-section-head', 'data')]  # Retrieve section-head from store
)
def update_year_dropdown(selected_sector, selected_section_head):
    if selected_sector and selected_section_head:
        filtered_years = sorted(set(
            p['Year'] for p in products
            if p['Sector'] == selected_sector and p['Category'] == selected_section_head
        ))
        return [{'label': year, 'value': year} for year in filtered_years], False

    return [], True  # Disable the dropdown if no sector or section-head is selected



# Callback to update the title dropdown based on selected year
@app.callback(
    [Output('product-dropdown', 'options'),
     Output('product-dropdown', 'disabled')],
    [Input('sector-dropdown', 'value'),
     Input('year-dropdown', 'value')],
    [State('stored-section-head', 'data')]  # Retrieve section-head from store
)
def update_product_dropdown(selected_sector, selected_year, selected_section_head):
    if selected_sector and selected_year and selected_section_head:
        filtered_titles = sorted(set(
            p['Title'] for p in products
            if p['Sector'] == selected_sector and p['Year'] == selected_year and p['Category'] == selected_section_head
        ))
        return [{'label': title, 'value': title} for title in filtered_titles], False

    return [], True  # Disable the dropdown if no sector, year, or section-head is selected



# Callback to update the image and re-trigger fade effect
@app.callback(
    [Output('carousel-image', 'src'),
     Output('carousel-image', 'className'),
     Output('carousel-index', 'data'),
     Output('fade-trigger', 'data')],
    [Input('prev-btn', 'n_clicks'),
     Input('next-btn', 'n_clicks'),
     Input('carousel-timer', 'n_intervals')],
    [State('carousel-index', 'data'),
     State('fade-trigger', 'data')]
)
def update_carousel(prev_clicks, next_clicks, n_intervals, index, fade_trigger):
    prev_clicks = prev_clicks or 0
    next_clicks = next_clicks or 0
    n_intervals = n_intervals or 0

    triggered = callback_context.triggered

    if not triggered:
        return carousel_images[index], "carousel-image fade", index, not fade_trigger  # Initial load

    button_id = triggered[0]['prop_id'].split('.')[0]

    if button_id == "next-btn" or button_id == "carousel-timer":
        index = (index + 1) % len(carousel_images)
    elif button_id == "prev-btn":
        index = (index - 1) % len(carousel_images)

    return carousel_images[
               index], "carousel-image fade" if not fade_trigger else "carousel-image fade-alt", index, not fade_trigger


@app.callback(
    Output('nav-menu', 'children'),
    Input('url', 'pathname')
)
def update_active_nav(pathname):
    nav_links = [
        html.A("Home", href="/", className="nav-link active" if pathname == "/" else "nav-link", id="nav-home"),
        *[
            html.A(
                product["title"],
                href=product["link"],
                className="nav-link active" if pathname == product["link"] else "nav-link",
                id=f"nav-{product['link'].strip('/')}"
            )
            for product in product_catalog
        ]
    ]
    return nav_links



@app.callback(
    Output('floating-about', 'children'),
    [Input('product-dropdown', 'value'),
     Input('sector-dropdown', 'value'),
     Input('year-dropdown', 'value')],
    [State('stored-section-head', 'data')]  # Retrieve section-head from store
)
def update_product_page(selected_product, selected_sector, selected_year, selected_section_head):
    # Ensure all required values are selected
    if not selected_product or not selected_sector or not selected_year or not selected_section_head:
        return html.P("Select all filters to see product information.", className="floating-text")

    # Filter the product data based on selected values from all dropdowns
    filtered_data = [
        p for p in products
        if p['Title'] == selected_product and
           p['Sector'] == selected_sector and
           p['Year'] == selected_year and
           p['Category'] == selected_section_head
    ]

    # Get the selected product details
    selected_product_details = next((p for p in products if p["Title"] == selected_product), None)

    # If a matching entry is found, return product details
    if filtered_data and selected_product_details:
        return html.Div([
            html.H3("About This Product", className="floating-title"),
            html.P(selected_product_details.get('Description', 'No description available.'), className="floating-text")
        ])

    # If no match is found, display a message
    return html.P("Select all filters to see product information.", className="floating-text")



# if __name__ == "__main__":
#     app.run_server(debug=True, port = 8080)
if __name__ == "__main__":
    app.run_server(
        debug=True,
        # host='0.0.0.0',
        port=8080)
