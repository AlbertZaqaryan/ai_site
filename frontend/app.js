// Relative path — nginx proxies /predict to the backend service
const API_URL = "/predict";

const form = document.getElementById("diabetesForm");
const resultBox = document.getElementById("resultBox");
const resultTitle = document.getElementById("resultTitle");
const resultText = document.getElementById("resultText");
const probaText = document.getElementById("probaText");
const presetBtn = document.getElementById("loadPresetBtn");

// Notebook preset: [1, 16, 0, 0, 0, 31.7, 3, 100]
presetBtn.addEventListener("click", () => {
  document.getElementById("gender").value = "1";
  document.getElementById("age").value = "16";
  document.getElementById("hypertension").value = "0";
  document.getElementById("heart_disease").value = "0";
  document.getElementById("smoking_history").value = "0";
  document.getElementById("bmi").value = "31.7";
  document.getElementById("HbA1c_level").value = "3.0";
  document.getElementById("blood_glucose_level").value = "100";
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const payload = {
    gender: Number(document.getElementById("gender").value),
    age: parseFloat(document.getElementById("age").value),
    hypertension: Number(document.getElementById("hypertension").value),
    heart_disease: Number(document.getElementById("heart_disease").value),
    smoking_history: Number(document.getElementById("smoking_history").value),
    bmi: parseFloat(document.getElementById("bmi").value),
    HbA1c_level: parseFloat(document.getElementById("HbA1c_level").value),
    blood_glucose_level: parseFloat(document.getElementById("blood_glucose_level").value),
  };

  resultBox.className = "result-box";
  resultTitle.textContent = "Processing...";
  resultText.textContent = "Calling model backend API...";
  probaText.textContent = "";

  try {
    const res = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      throw new Error(`Server returned status: ${res.status}`);
    }

    const data = await res.json();

    if (data.prediction === 1) {
      resultBox.className = "result-box result-positive";
      resultTitle.textContent = "Positive Result (Diabetic Risk Detected)";
      resultText.textContent = `Model predicted: array([1])`;
    } else {
      resultBox.className = "result-box result-negative";
      resultTitle.textContent = "Negative Result (Low Diabetic Risk)";
      resultText.textContent = `Model predicted: array([0])`;
    }

    if (data.probabilities) {
      probaText.textContent = `Probability: Non-Diabetic ${data.probabilities.negative}% | Diabetic ${data.probabilities.positive}%`;
    }
  } catch (err) {
    resultBox.className = "result-box result-positive";
    resultTitle.textContent = "Prediction Error";
    resultText.textContent = `Could not connect to Flask API (${err.message}). Make sure app.py is running on http://localhost:5000.`;
  }
});