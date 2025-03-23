# Import necessary libraries for data manipulation, machine learning, and serialization
import pandas as pd  # Data manipulation and analysis library
import pickle  # Object serialization for saving models
from sklearn.model_selection import train_test_split  # Splitting data into training and testing sets
from sklearn.ensemble import RandomForestClassifier  # Random Forest machine learning algorithm
from sklearn.metrics import classification_report, confusion_matrix  # Model performance evaluation metrics
from sklearn.preprocessing import StandardScaler  # Feature scaling utility
import os  # Operating system interactions for file and path operations

# Define the filename for the dataset to be used for training
dataset_filename = "vehicle_data.csv"

# Check if the dataset file exists before proceeding
if not os.path.exists(dataset_filename):
    # Print error message if dataset is missing
    print(f"Error: Dataset file '{dataset_filename}' not found. Run generate_dataset.py first.")
    # Exit the script if dataset is not found
    exit()

try:
    # Attempt to load the dataset from CSV
    df = pd.read_csv(dataset_filename)
    # Print confirmation message upon successful loading
    print(f"Dataset '{dataset_filename}' loaded.")
except Exception as e:
    # Print error message if dataset loading fails
    print(f"Error loading dataset: {e}")
    # Exit the script if loading fails
    exit()

# Separate features (X) and target variable (y)
X = df.drop("overload_status", axis=1)  # All columns except target
y = df["overload_status"]  # Target variable

# Print columns before scaling for verification
print("Columns before scaling:", X.columns)

# Note: One-hot encoding is commented out, likely already done in previous preprocessing
# Uncomment if vehicle_type needs to be one-hot encoded
#X = pd.get_dummies(X, columns=["vehicle_type"])

# Define numerical features to be scaled
numerical_features = ['weight', 'max_load_capacity', 'passenger_count', 'cargo_weight']
# Initialize StandardScaler for feature normalization
scaler = StandardScaler()
# Apply scaling to numerical features
X[numerical_features] = scaler.fit_transform(X[numerical_features])

# Remove original numerical columns after scaling to prevent duplicate information
X.drop(numerical_features, axis=1, inplace=True)

# Create a list of columns to be used for training
X_train_cols = X.columns.tolist()

# Print training columns for verification
print("X_train_cols:", X_train_cols)

# Split data into training and testing sets
# 80% training, 20% testing, with a fixed random state for reproducibility
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize Random Forest Classifier
# Random state ensures reproducibility of results
model = RandomForestClassifier(random_state=42)
# Train the model on the training data
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Print detailed classification report
# Shows precision, recall, f1-score for each class
print(classification_report(y_test, y_pred))

# Print confusion matrix
# Shows correct and incorrect predictions for each class
print(confusion_matrix(y_test, y_pred))

# Define filenames for saving the model and scaler
model_filename = "vehicle_load_model.pkl"
scaler_filename = "vehicle_load_scaler.pkl"

# Save the trained model using pickle
with open(model_filename, "wb") as file:
    pickle.dump(model, file)

# Save the scaler used for feature scaling
with open(scaler_filename, "wb") as file:
    pickle.dump(scaler, file)

# Print confirmation messages for model and scaler saving
print(f"Model saved to '{model_filename}'.")
print(f"Scaler saved to '{scaler_filename}'.")

# Print final completion message
print("Training complete.")