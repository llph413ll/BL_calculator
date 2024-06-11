from flask import Flask, render_template, request
import datetime
import math

current = datetime.datetime.now().strftime('%m-%d-%Y')

# Density conversions to kg/m3
density_conversions = {
    'lbft3': 16.0185,  # pounds per cubic foot to kg/m³
    'kgm3': 1,         # kg/m³ to kg/m³ (no conversion needed)
    'gcm3': 1000,      # grams per cubic centimeter to kg/m³
    'gl': 1.0          # grams per liter to kg/m³
}

# Viscosity conversions to Pa·s
viscosity_conversions = {
    'cp': 0.001,    # centipoise to Pa·s
    'mpas': 0.001,  # milliPascal-second to Pa·s
    'pas': 1,       # Pascal-second to Pa·s
    'nsm2': 1
}

# Length conversions to meters
length_conversions = {
    'in': 0.0254,   # inches to meters
    'ft': 0.3048,   # feet to meters
    'mm': 0.001,    # millimeters to meters
    'cm': 0.01,      # centimeters to meters
    'm' : 1,
}

# Flowrate conversions to m3/s
flowrate_conversions = {
    'gpm': 0.0000630902,  # gallons per minute to m³/s
    'mgd': 0.043812636,   # million gallons per day to m³/s
    'bpd': 0.0001589873,  # barrels per day to m³/s
    'ft3m': 0.0004719474, # cubic feet per minute to m³/s
    'ft3s': 0.0283168466, # cubic feet per second to m³/s
    'm3s': 1,             # cubic meters per second to m³/s
    'm3min': 0.0166666667 # cubic meters per minute to m³/s
}

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html',time=current)

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    try:

        density = float(request.form['density'])
        density_unit = request.form['density_unit']
        viscosity = float(request.form['viscosity'])
        viscosity_unit = request.form['viscosity_unit']
        pipe_ID = float(request.form['pipe_ID'])
        pipe_ID_unit = request.form['pipe_ID_unit']
        flowrate = float(request.form['flowrate'])
        flowrate_unit = request.form['flowrate_unit']
        desired_yplus = float(request.form['target_yplus'])
        distance = float(request.form['distance'])
        distance_unit = request.form['distance_unit']
        growth_ratio = float(request.form['layer_ratio'])
        number_of_layer = float(request.form['NO_layer'])

        # Convert all inputs to standard units defined in your model
        density *= density_conversions[density_unit]
        viscosity *= viscosity_conversions[viscosity_unit]
        pipe_ID *= length_conversions[pipe_ID_unit]
        flowrate *= flowrate_conversions[flowrate_unit]
        distance *= length_conversions[distance_unit]
        velocity = 4 * flowrate/(math.pi*pipe_ID**2)
        re = velocity * density * pipe_ID/viscosity
        cf = 0.058 * (re**-0.2)
        tauw = 0.5*cf*density*(velocity**2)
        utau =(tauw/density)**0.5
        first_height = desired_yplus * viscosity/(density * utau)
        first_height_inch = first_height*1/0.0254
        turbulent_intensity = 0.2 * (re ** -0.125) * 100
        nth_height = first_height*growth_ratio**(number_of_layer-1)
        nth_height_in = nth_height*1/0.0254
        total_height = first_height*(1-growth_ratio**number_of_layer)/(1-growth_ratio)
        total_height_in = total_height*1/0.0254

        if re < 2300: #for laminar region
            entrance_length = 0.06 * pipe_ID * re  # per ANSYS fFully Developed Internal Turbulent Flows in Ducts and Pipes
            entrance_length_inch = entrance_length * 1 / 0.0254
            boundary_thk = 5 * distance * (re ** -0.5)
            boundary_thk_inch = boundary_thk * 1 / 0.0254
        else: #for turbulent region
            entrance_length = 4.4*pipe_ID * re**(1/6) #per ANSYS fFully Developed Internal Turbulent Flows in Ducts and Pipes
            entrance_length_inch = entrance_length * 1 / 0.0254
            boundary_thk= 0.382 * distance * (re ** -0.2)
            boundary_thk_inch = boundary_thk * 1 / 0.0254


        # result_text = f"Reynold's NO: {re:.2f} First cell height : {first_height} Desired y+ : {desired_yplus}"
        return render_template('index.html', re=f"{re:.3e}", first_height=f"{first_height_inch:.5f}", entrance_length =f"{entrance_length_inch:.1f}",
                boundary_thk=f"{boundary_thk_inch:.3f}", nth_height=f"{nth_height_in:.3f}", total_height=f"{total_height_in:.3f}",  turbulent_intensity=f"{turbulent_intensity:.1f}", time=current)
    except (ValueError, KeyError) as e:
        error_text = "Invalid input. Ensure all fields are numeric."
        return render_template('index.html', error_message=error_text, time=current)

if __name__ == '__main__':
    app.run(debug=True)
