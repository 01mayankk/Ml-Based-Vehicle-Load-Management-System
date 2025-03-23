from flask import Flask, render_template, request, jsonify, url_for
import pickle
import pandas as pd
import os
import logging
import random
import graph  # Import the graph module

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

model_filename = "vehicle_load_model.pkl"
scaler_filename = "vehicle_load_scaler.pkl"

try:
    with open(model_filename, "rb") as model_file, open(scaler_filename, "rb") as scaler_file:
        model = pickle.load(model_file)
        scaler = pickle.load(scaler_file)
    logging.info(f"Model '{model_filename}' and Scaler '{scaler_filename}' loaded successfully.")
except (FileNotFoundError, pickle.UnpicklingError) as e:
    logging.error(f"Error loading model or scaler: {e}")
    exit()

def preprocess_data(data):
    try:
        df = pd.DataFrame([data])
        logging.info(f"Dataframe before one-hot encoding: {df}")
        df = pd.get_dummies(df, columns=["vehicle_type"])
        logging.info(f"Dataframe after one-hot encoding: {df}")

        # Ensure all required training columns are present
        training_columns = ['vehicle_type_2-wheeler', 'vehicle_type_4-wheeler 5-seater',
                            'vehicle_type_4-wheeler 7-seater', 'vehicle_type_delivery vehicle',
                            'vehicle_type_heavy vehicle']
        for col in training_columns:
            if col not in df.columns:
                df[col] = 0
        logging.info(f"Dataframe after adding missing columns: {df}")

        numerical_features = ['weight', 'max_load_capacity', 'passenger_count', 'cargo_weight']
        numerical_data = df[numerical_features]
        logging.info(f"Numerical Data before scaling: {numerical_data}")
        try:
            scaled_data = scaler.transform(numerical_data)
            scaled_df = pd.DataFrame(scaled_data, columns=[f"{col}_scaled" for col in numerical_features])
            logging.info(f"Scaled Data: {scaled_df}")
        except Exception as e:
            logging.error(f"Error during scaling: {e}")
            return None
        df = pd.concat([df, scaled_df], axis=1)
        logging.info(f"Dataframe after concat scaled data: {df}")
        df.drop(numerical_features, axis=1, inplace=True)
        logging.info(f"Columns before reordering: {df.columns.tolist()}")

        # Reorder columns
        df = df[training_columns + [f"{col}_scaled" for col in numerical_features]]
        return df
    except KeyError as e:
        logging.error(f"Missing key in input data: {e}")
        return None
    except Exception as e:
        logging.error(f"Error in preprocessing: {e}")
        return None

@app.route("/")
def index():
    background_image = get_random_background()
    logging.info(f"Background image: {background_image}")
    return render_template("basic.html", background_image=background_image)

def generate_sample_data(num_samples=100):
    data = {
        'vehicle_type': random.choices(['2-wheeler', '4-wheeler 5-seater', '4-wheeler 7-seater', 'delivery vehicle', 'heavy vehicle'], k=num_samples),
        'weight': [random.randint(50, 20000) for _ in range(num_samples)],
        'max_load_capacity': [random.randint(100, 25000) for _ in range(num_samples)],
        'passenger_count': [random.randint(1, 7) for _ in range(num_samples)],
        'cargo_weight': [random.randint(0, 10000) for _ in range(num_samples)]
    }
    return pd.DataFrame(data)

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
        logging.info(f"Received data: {data}")
        if data is None:
            return jsonify({"error": "No data provided"}), 400
        processed_data = preprocess_data(data)
        logging.info(f"Processed data: {processed_data}")
        if processed_data is None:
            return jsonify({"error": "Preprocessing failed"}), 400
        prediction = model.predict(processed_data)[0]
        logging.info(f"Prediction (Model Output): {prediction}")

        # Calculate overload amount based on the provided data
        total_weight = int(data.get('weight', 0)) + int(data.get('passenger_count', 0)) * 75 + int(data.get('cargo_weight', 0))
        max_load_capacity = int(data.get('max_load_capacity', 0))
        overload_amount = max(0, total_weight - max_load_capacity)

        # Determine overload status based on overload amount
        if overload_amount > 0:
            overload_status = "Overloaded"
        else:
            overload_status = "Not Overloaded"

        result = {
            "overload_status": overload_status,
            "overload_amount": overload_amount,
        }

        vehicle_limits = {
            "2-wheeler": {"maxCargo": 50},
            "4-wheeler 5-seater": {"maxCargo": 500},
            "4-wheeler 7-seater": {"maxCargo": 750},
            "delivery vehicle": {"maxCargo": 1500},
            "heavy vehicle": {"maxCargo": 10000}
        }
        suggested_vehicles = []
        if data.get("vehicle_type") == "heavy vehicle":
            cargo_weight = int(data.get("cargo_weight", 0))  # Convert to integer
            if cargo_weight <= vehicle_limits["delivery vehicle"]["maxCargo"]:
                suggested_vehicles.append("delivery vehicle")
            if cargo_weight <= vehicle_limits["4-wheeler 7-seater"]["maxCargo"]:
                suggested_vehicles.append("4-wheeler 7-seater")
            if cargo_weight <= vehicle_limits["4-wheeler 5-seater"]["maxCargo"]:
                suggested_vehicles.append("4-wheeler 5-seater")
            if cargo_weight <= vehicle_limits["2-wheeler"]["maxCargo"]:
                suggested_vehicles.append("2-wheeler")
        result["suggested_vehicles"] = suggested_vehicles

        logging.info(f"Overload Status: {overload_status}")
        logging.info(f"Overload Amount: {overload_amount}")

        # Generate graphs based on vehicle type from sample data (not user input)
        df = generate_sample_data()

        graphs_dir = os.path.join(app.static_folder, 'graphs')
        if not os.path.exists(graphs_dir):
            os.makedirs(graphs_dir)

        # Generate all graphs
        histogram_path = os.path.join(graphs_dir, 'histogram_weight.png')
        graph.generate_histogram(df, 'weight', 'Histogram of Vehicle Weight', histogram_path)
        histogram_url = url_for('static', filename='graphs/histogram_weight.png')

        boxplot_path = os.path.join(graphs_dir, 'boxplot_weight.png')
        graph.generate_boxplot(df, 'weight', 'Boxplot of Vehicle Weight', boxplot_path)
        boxplot_url = url_for('static', filename='graphs/boxplot_weight.png')

        scatter_path = os.path.join(graphs_dir, 'scatter_plot.png')
        graph.generate_scatter_plot(df, 'weight', 'cargo_weight', 'Scatter Plot of Weight vs. Cargo Weight', scatter_path)
        scatter_url = url_for('static', filename='graphs/scatter_plot.png')

        heatmap_path = os.path.join(graphs_dir, 'heatmap.png')
        heatmap_df = df.drop("vehicle_type", axis=1)  # Exclude vehicle type for heatmap
        graph.generate_heatmap(heatmap_df, 'Heatmap of Vehicle Features', heatmap_path)
        heatmap_url = url_for('static', filename='graphs/heatmap.png')

        pair_plot_path = os.path.join(graphs_dir, 'pair_plot.png')
        graph.generate_pair_plot(df.drop("vehicle_type", axis=1), 'Pair Plot of Vehicle Features', pair_plot_path)  # Exclude vehicle type for pairplot
        pair_plot_url = url_for('static', filename='graphs/pair_plot.png')

        count_plot_path = os.path.join(graphs_dir, 'count_plot.png')
        graph.generate_count_plot(df, 'vehicle_type', 'Count Plot of Vehicle Types', count_plot_path)
        count_plot_url = url_for('static', filename='graphs/count_plot.png')

        # Add URLs to the response
        result['histogram_url'] = histogram_url
        result['boxplot_url'] = boxplot_url
        result['scatter_url'] = scatter_url
        result['heatmap_url'] = heatmap_url
        result['pair_plot_url'] = pair_plot_url
        result['count_plot_url'] = count_plot_url

        return jsonify(result)

    except Exception as e:
        logging.error(f"Prediction error: {e}")
        return jsonify({"error": "An error occurred during prediction."}), 500
    
def get_random_background():
    background_dir = os.path.join(app.static_folder, 'backgrounds')
    try:
        images = os.listdir(background_dir)
        if images:
            random_image = random.choice(images)
            return url_for('static', filename=f'backgrounds/{random_image}')
        logging.warning("No images found in backgrounds directory.")
        return None
    except FileNotFoundError:
        logging.error(f"Background directory not found at: {background_dir}")
        return None

if __name__ == "__main__":
    app.run(debug=True)