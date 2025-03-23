# Import necessary libraries for data manipulation, numerical operations, randomization, and file operations
import pandas as pd  # Data manipulation and analysis library
import numpy as np  # Numerical computing library
import random  # Random number and selection generation
import os  # Operating system interactions for file and path operations

# Import specialized libraries for machine learning preprocessing
from imblearn.over_sampling import SMOTE  # Synthetic Minority Over-sampling Technique for balancing datasets
from sklearn.preprocessing import StandardScaler  # Feature scaling utility

# Define the filename for the generated dataset
dataset_filename = "vehicle_data.csv"

# Check if the dataset file already exists to avoid regenerating
if not os.path.exists(dataset_filename):
    # Set the number of entries to generate in the dataset
    num_entries = 10000
    # Initialize an empty list to store generated data
    data = []

    # Generate synthetic vehicle data entries
    for _ in range(num_entries):
        # Randomly select a vehicle type with equal probability
        vehicle_type = random.choice(["2-wheeler", "4-wheeler 5-seater", "4-wheeler 7-seater", "delivery vehicle", "heavy vehicle"])

        # Generate data specific to each vehicle type with realistic constraints
        if vehicle_type == "2-wheeler":
            max_capacity = random.randint(200, 350)  # Maximum load capacity range
            empty_weight = random.randint(80, 120)  # Vehicle's base weight
            passenger_count = random.randint(1, 2)  # Number of passengers
            passenger_weight = passenger_count * 75  # Assume 75kg per passenger
            cargo_weight = random.randint(0, 50)  # Cargo weight range
        elif vehicle_type == "4-wheeler 5-seater":
            max_capacity = random.randint(800, 1200)
            empty_weight = random.randint(600, 800)
            passenger_count = random.randint(1, 5)
            passenger_weight = passenger_count * 75
            cargo_weight = random.randint(0, 150)
        elif vehicle_type == "4-wheeler 7-seater":
            max_capacity = random.randint(1000, 1500)
            empty_weight = random.randint(800, 1000)
            passenger_count = random.randint(1, 7)
            passenger_weight = passenger_count * 75
            cargo_weight = random.randint(0, 200)
        elif vehicle_type == "delivery vehicle":
            max_capacity = random.randint(1500, 2500)
            empty_weight = random.randint(1000, 1500)
            passenger_count = random.randint(1, 2)
            passenger_weight = passenger_count * 75
            cargo_weight = random.randint(0, 500)
        elif vehicle_type == "heavy vehicle":
            max_capacity = random.randint(10000, 30000)
            empty_weight = random.randint(5000, 10000)
            passenger_count = random.randint(1, 3)
            passenger_weight = passenger_count * 75
            cargo_weight = random.randint(0, max_capacity)

        # Calculate total vehicle weight
        weight = empty_weight + passenger_weight + cargo_weight
        # Determine overload status based on weight exceeding max capacity
        overload_status = "Overloaded" if weight > max_capacity else "Not Overloaded"
        # Append generated data to the list
        data.append([vehicle_type, weight, max_capacity, passenger_count, cargo_weight, overload_status])

    # Convert generated data to a pandas DataFrame
    df = pd.DataFrame(data, columns=["vehicle_type", "weight", "max_load_capacity", "passenger_count", "cargo_weight", "overload_status"])

    # Perform initial data quality checks
    print("NaNs in df (original):", df.isnull().any().any())  # Check for any NaN values
    print("NaNs per column in df (original):\n", df.isnull().sum())  # Count NaNs per column
    print("Data types in df (original):\n", df.dtypes)  # Display column data types

    # Define numerical features for standardization
    numerical_features = ['weight', 'max_load_capacity', 'passenger_count', 'cargo_weight']
    # Initialize StandardScaler for feature normalization
    scaler = StandardScaler()

    # Separate features (X) and target variable (y)
    X = df.drop("overload_status", axis=1)
    y = df["overload_status"]

    # Perform one-hot encoding on categorical 'vehicle_type' column
    X = pd.get_dummies(X, columns=["vehicle_type"])

    # Apply SMOTE to balance the dataset and address class imbalance
    smote = SMOTE(random_state=42)  # Use fixed random state for reproducibility
    X_resampled, y_resampled = smote.fit_resample(X, y)

    # Scale numerical features after SMOTE resampling
    X_numerical_resampled = X_resampled[numerical_features]
    X_scaled_resampled = scaler.fit_transform(X_numerical_resampled)
    # Create a new DataFrame with scaled features
    X_scaled_resampled_df = pd.DataFrame(X_scaled_resampled, columns=[f"{col}_scaled" for col in numerical_features], index=X_resampled.index)

    # Concatenate original and scaled features
    X_resampled = pd.concat([X_resampled, X_scaled_resampled_df], axis=1)

    # Combine resampled features and target variable
    df_balanced = pd.concat([X_resampled, y_resampled], axis=1)

    # Randomly sample to ensure consistent dataset size
    df_balanced = df_balanced.sample(n=10000, random_state=42, replace=False)

    # Perform final data quality checks before saving
    print("NaNs in df_balanced before saving:", df_balanced.isnull().any().any())  # Check for any NaN values
    print("NaNs per column in df_balanced before saving:\n", df_balanced.isnull().sum())  # Count NaNs per column
    print("Data types in df_balanced before saving:\n", df_balanced.dtypes)  # Display column data types

    # Save the balanced and standardized dataset to a CSV file
    df_balanced.to_csv(dataset_filename, index=False)
    # Print confirmation message with dataset details
    print(f"Balanced and standardized dataset '{dataset_filename}' created with {len(df_balanced)} rows.")

else:
    # If dataset already exists, print a message and skip generation
    print(f"Dataset '{dataset_filename}' already exists. Skipping data generation.")