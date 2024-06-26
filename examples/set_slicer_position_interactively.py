"""
This is an example that shows how the slicer position can be both read from and written to
by listening to the "drag_value" of the default slider with an auxiliary slider
"""

import dash
from dash import html
from dash_slicer import VolumeSlicer
from dash import dcc
from dash.dependencies import Input, Output
import imageio


app = dash.Dash(__name__, update_title=None)

vol = imageio.volread("imageio:stent.npz")
slicer0 = VolumeSlicer(app, vol, axis=0, scene_id="brain")
slicer1 = VolumeSlicer(app, vol, axis=1, scene_id="brain")
slicer2 = VolumeSlicer(app, vol, axis=2, scene_id="brain")

setpos_store = dcc.Store(
    id={"context": "app", "scene": slicer0.scene_id, "name": "setpos"}
)

# Here we create an auxiliary slider for each slicer and encapsulate it inside a Div
# to be added to the app layout
slicer_list = [setpos_store]
for sidx, slicer in enumerate([slicer0, slicer1, slicer2]):
    slider = dcc.Slider(id=f"slider-{sidx}", max=slicer.nslices)
    slicer_list.append(
        html.Div(
            [
                html.Pre("slicer graph"),
                slicer.graph,
                html.Pre("builtin slider"),
                slicer.slider,
                html.Pre("auxiliary slider"),
                slider,
                *slicer.stores,
            ]
        )
    )

# Create a small CSS grid with Input fields and text labels to both display
# the slicer axis positions and allow the user to interactively change them
nav_table = html.Div(
    [
        html.Div(""),
        html.Div("Voxel position"),
        html.Div("X axis"),
        dcc.Input(id="x-nav", type="number", placeholder="X value"),
        html.Div("Y axis"),
        dcc.Input(id="y-nav", type="number", placeholder="Y value"),
        html.Div("Z axis"),
        dcc.Input(id="z-nav", type="number", placeholder="Z value"),
    ],
    style={"display": "grid", "gridTemplateColumns": "10% 10%"},
)
slicer_list.append(nav_table)

app.layout = html.Div(
    style={
        "display": "grid",
        "gridTemplateColumns": "33% 33% 33%",
    },
    children=slicer_list,
)


# Take the current value from the main slider and copy it to the
# auxiliary slider
@app.callback(
    [
        Output("slider-0", "value"),
        Output("slider-1", "value"),
        Output("slider-2", "value"),
    ],
    [
        Input(slicer0.slider.id, "drag_value"),
        Input(slicer1.slider.id, "drag_value"),
        Input(slicer2.slider.id, "drag_value"),
    ],
)
def write_to_auxiliary_slider(x_slider, y_slider, z_slider):
    return x_slider, y_slider, z_slider


# Write the values of the axiliary slider to the input fields in the navigation table
@app.callback(
    [Output("x-nav", "value"), Output("y-nav", "value"), Output("z-nav", "value")],
    [
        Input("slider-0", "value"),
        Input("slider-1", "value"),
        Input("slider-2", "value"),
    ],
)
def write_to_position_table(x_val, y_val, z_val):
    return x_val, y_val, z_val


# Listen for a user-triggered change to the value of the Input fields in the navigation table
# and set the position of the slicer accordingly
@app.callback(
    Output(setpos_store.id, "data"),
    [
        Input("x-nav", "value"),
        Input("y-nav", "value"),
        Input("z-nav", "value"),
    ],
)
def write_table_values_to_slicer(x_pos, y_pos, z_pos):
    return z_pos, y_pos, x_pos


if __name__ == "__main__":
    # Note: dev_tools_props_check negatively affects the performance of VolumeSlicer
    app.run_server(debug=True, dev_tools_props_check=False)
