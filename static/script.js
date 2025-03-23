// static/script.js

const vehicleLimits = {
    "2-wheeler": { minWeight: 50, maxWeight: 350, minPassengers: 1, maxPassengers: 2, maxCargo: 50, suggestedVehicles: [] },
    "4-wheeler 5-seater": { minWeight: 800, maxWeight: 2500, minPassengers: 1, maxPassengers: 5, maxCargo: 500, suggestedVehicles: ["2-wheeler"] },
    "4-wheeler 7-seater": { minWeight: 1000, maxWeight: 3500, minPassengers: 1, maxPassengers: 7, maxCargo: 750, suggestedVehicles: ["2-wheeler", "4-wheeler 5-seater"] },
    "delivery vehicle": { minWeight: 1500, maxWeight: 5000, minPassengers: 1, maxPassengers: 2, maxCargo: 1500, suggestedVehVehicles: ["2-wheeler", "4-wheeler 5-seater", "4-wheeler 7-seater"] },
    "heavy vehicle": { minWeight: 5000, maxWeight: 20000, minPassengers: 1, maxPassengers: 3, maxCargo: 10000, suggestedVehicles: ["2-wheeler", "4-wheeler 5-seater", "4-wheeler 7-seater", "delivery vehicle"] }
};

const vehicleTypeSelect = document.getElementById("vehicle_type");
const weightInput = document.getElementById("weight");
const maxLoadInput = document.getElementById("max_load_capacity");
const passengerInput = document.getElementById("passenger_count");
const cargoInput = document.getElementById("cargo_weight");

const errorMessages = {
    weight: document.getElementById("weight_error"),
    maxLoad: document.getElementById("max_load_error"),
    passengers: document.getElementById("passenger_error"),
    cargo: document.getElementById("cargo_error")
};

// Style error messages
for (const key in errorMessages) {
    if (errorMessages[key]) {
        errorMessages[key].style.color = "red";
    }
}

function validateInputs() {
    setTimeout(() => {
        const vehicleType = vehicleTypeSelect.value;
        const limits = vehicleLimits[vehicleType];

        if (!limits) return;

        // Set Max Load Capacity on Vehicle Type Change
        if (document.activeElement === vehicleTypeSelect) {
            maxLoadInput.value = limits.maxWeight;
        }

        const weight = parseFloat(weightInput.value);
        const maxLoad = parseFloat(maxLoadInput.value);
        const passengers = parseInt(passengerInput.value);
        const cargo = parseFloat(cargoInput.value);

        // Weight Validation
        if (weight < limits.minWeight || weight > limits.maxWeight) {
            errorMessages.weight.textContent = `Weight must be between ${limits.minWeight} and ${limits.maxWeight} kg. Current weight: ${weight} kg.`;
        } else {
            errorMessages.weight.textContent = "";
        }

        // Max Load Validation
        if (maxLoad > limits.maxWeight) {
            errorMessages.maxLoad.textContent = `Max load cannot exceed ${limits.maxWeight} kg for ${vehicleType}. Current max load: ${maxLoad} kg.`;
        } else {
            errorMessages.maxLoad.textContent = "";
        }

        // Passenger Validation
        if (passengers < limits.minPassengers || passengers > limits.maxPassengers) {
            errorMessages.passengers.textContent = `Passengers must be between ${limits.minPassengers} and ${limits.maxPassengers}. Current passenger count: ${passengers}.`;
        } else {
            errorMessages.passengers.textContent = "";
        }

        // Cargo Validation
        if (cargo > limits.maxCargo) {
            errorMessages.cargo.textContent = `Cargo weight cannot exceed ${limits.maxCargo} kg. Current cargo weight: ${cargo} kg.`;
        } else {
            errorMessages.cargo.textContent = "";
        }
    }, 0);
}

// Add event listeners
vehicleTypeSelect.addEventListener("change", validateInputs);
weightInput.addEventListener("input", validateInputs);
maxLoadInput.addEventListener("input", validateInputs);
passengerInput.addEventListener("input", validateInputs);
cargoInput.addEventListener("input", validateInputs);

// Prediction Function
function predict() {
    const form = document.getElementById("predictionForm");
    const data = {
        vehicle_type: form.vehicle_type.value,
        weight: parseFloat(form.weight.value),
        max_load_capacity: parseFloat(form.max_load_capacity.value),
        passenger_count: parseInt(form.passenger_count.value),
        cargo_weight: parseFloat(form.cargo_weight.value)
    };

    fetch('/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(result => {
        const resultDiv = document.getElementById("result");
        resultDiv.innerHTML = "";

        if (result.error) {
            resultDiv.innerHTML = `<p style="color: red;">${result.error}</p>`;
        } else {
            let resultText = `Overload Status: <span class="${result.overload_status.toLowerCase()}">${result.overload_status}</span><br>`;
            resultText += `Overload Amount: ${result.overload_amount} kg`;

            // Vehicle Suggestions
            const currentVehicle = data.vehicle_type;
            const limits = vehicleLimits[currentVehicle];
            const suggestedVehicles = limits.suggestedVehicles;

            if (suggestedVehicles && suggestedVehicles.length > 0) {
                let suitableVehicles = [];
                for (const vehicle of suggestedVehicles) {
                    const vehicleLimit = vehicleLimits[vehicle];
                    if (vehicleLimit && data.cargo_weight <= vehicleLimit.maxCargo) {
                        suitableVehicles.push(vehicle);
                    }
                }

                if (suitableVehicles.length > 0) {
                    resultText += `<br><br>Suggestion: With this cargo weight, you could use a ${suitableVehicles.join(", ")}.`;
                }
            }

            resultDiv.innerHTML = resultText;

            // Show Graph Section
            const graphSection = document.getElementById('dataVisualizationSection');
            if (graphSection) {
                graphSection.style.display = 'block'; // Corrected to 'block'
                console.log("Graph section display:", graphSection.style.display);
            }

            // Modal Logic (Assuming you have openModal defined)
            const graphs = document.querySelectorAll('.graphs img');
            graphs.forEach(graph => {
                graph.onclick = function() {
                    openModal(this.src);
                };
            });
        }
    })
    .catch(error => console.error('Error:', error));
}