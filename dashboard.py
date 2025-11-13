from shiny import App, render, ui

# -------------------------------
# 1. Define the User Interface
# -------------------------------
app_ui = ui.page_fluid(
    ui.h2("My First Shiny Dashboard"),
    # Add inputs and outputs here, for example:
    # ui.input_slider("n", "Choose a number:", 1, 100, 50),
    # ui.output_text("result")
)

# -------------------------------
# 2. Define the Server Logic
# -------------------------------
def server(input, output, session):
    # Example reactive output (can be deleted or modified)
    @output
    @render.text
    def result():
        return "Hello, Shiny!"


# -------------------------------
# 3. Create the App Object
# -------------------------------
app = App(app_ui, server)
app.run()