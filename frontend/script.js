let npkChart = null;

// ==========================================
// 1. IMAGE PREVIEW
// ==========================================
function previewImage() {
    const file = document.getElementById("imageInput").files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            document.getElementById("preview").src = e.target.result;
            document.getElementById("imagePreviewContainer").style.display = "block";
        }
        reader.readAsDataURL(file);
    }
}

// ==========================================
// 2. HTML5 GEOLOCATION (LAT/LON)
// ==========================================
function getGPSLocation() {
    const locInput = document.getElementById("locationInput");
    const gpsBtn = document.getElementById("gpsBtn");

    if (navigator.geolocation) {
        gpsBtn.innerText = "⏳"; // Loading indicator
        
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const lat = position.coords.latitude.toFixed(4);
                const lon = position.coords.longitude.toFixed(4);
                locInput.value = `${lat}, ${lon}`;
                gpsBtn.innerText = "📍";
            },
            (error) => {
                console.error("GPS Error:", error);
                alert("⚠️ Could not detect GPS. Please allow location permissions in your browser.");
                gpsBtn.innerText = "📍";
            },
            { enableHighAccuracy: false, timeout: 10000, maximumAge: 0 }
        );
    } else {
        alert("Geolocation is not supported by your browser.");
    }
}

// ==========================================
// 3. MAIN AI & API FETCH LOGIC
// ==========================================
async function submitData() {
    const imageFile = document.getElementById("imageInput").files[0];
    const location = document.getElementById("locationInput").value;
    const btn = document.getElementById("analyzeBtn");

    const healthCard = document.getElementById("healthCard");
    const soilCard = document.getElementById("soilCard");
    const pestCard = document.getElementById("pestCard");
    const actionContent = document.getElementById("actionContent");

    if (!imageFile || !location) {
        alert("⚠️ Please upload a leaf image and enter a location or GPS coordinates first!");
        return;
    }

    btn.innerText = "Processing AI & APIs...";
    btn.disabled = true;
    btn.style.opacity = "0.7";

    const formData = new FormData();
    formData.append("image", imageFile);
    formData.append("location", location);

    try {
        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Backend connection failed");

        const data = await response.json();

        // ==========================================
        // 4. HEALTH CARD LOGIC
        // ==========================================
        let healthClass = "card status-danger"; 
        let healthIcon = "⚠️";
        let isHealthy = data.crop_health.toLowerCase().includes("healthy");
        
        if (isHealthy) {
            healthClass = "card status-healthy";
            healthIcon = "✅";
        }

        healthCard.className = healthClass;
        healthCard.innerHTML = `
            <div class="card-header">🌿 Health Status</div>
            <div class="card-body">${healthIcon} ${data.crop_health}</div>
        `;

        // ==========================================
        // 5. SOIL CARD LOGIC
        // ==========================================
        soilCard.className = "card"; 
        soilCard.innerHTML = `
            <div class="card-header">
                🌱 Soil Score <span class="pulse-dot"></span>
            </div>
            <div class="card-body" style="color: #2563eb;">${data.soil_score} / 100</div>
            <div style="font-size: 0.75em; margin-top: 10px; font-weight: normal; color: #64748b;">
                🌡️ Temp: ${data.soil_temp}°C | 💧 Moist: ${data.soil_moisture}%
            </div>
        `;

        // ==========================================
        // 6. PEST RISK CARD LOGIC
        // ==========================================
        let pestClass = "card status-warning";
        const riskLevel = data.pest_risk.toLowerCase();
        
        if (riskLevel === "low") pestClass = "card status-healthy";
        if (riskLevel === "high") pestClass = "card status-danger";

        pestCard.className = pestClass;
        pestCard.innerHTML = `
            <div class="card-header">🐛 Pest Risk</div>
            <div class="card-body">${data.pest_risk}</div>
            <div style="font-size: 0.75em; margin-top: 10px; font-weight: normal; color: #64748b;">
                🌡️ Air: ${data.temperature}°C | 💧 Hum: ${data.humidity}%
            </div>
        `;

        // ==========================================
        // 7. ACTION PLAN LOGIC
        // ==========================================
        if (riskLevel === "high" || !isHealthy) {
            actionContent.innerHTML = `
                <div style="color: #991b1b; background: #fef2f2; padding: 15px; border-radius: 10px; border-left: 5px solid #ef4444;">
                    <strong>🚨 URGENT ACTION REQUIRED:</strong> ${!isHealthy ? `Crop shows signs of ${data.crop_health}. ` : ''} 
                    Current humidity (${data.humidity}%) accelerates spread. Isolate affected areas and apply targeted organic treatments immediately.
                </div>`;
        } else if (riskLevel === "medium") {
            actionContent.innerHTML = `
                <div style="color: #92400e; background: #fffbeb; padding: 15px; border-radius: 10px; border-left: 5px solid #f59e0b;">
                    <strong>⚠️ PREVENTATIVE CARE:</strong> Moderate environmental stress detected. Monitor leaf undersides closely. 
                    Ensure proper field drainage and avoid evening irrigation to keep foliage dry.
                </div>`;
        } else {
            actionContent.innerHTML = `
                <div style="color: #065f46; background: #ecfdf5; padding: 15px; border-radius: 10px; border-left: 5px solid #10b981;">
                    <strong>✅ STABLE CONDITIONS:</strong> No immediate threat detected. Environmental metrics are optimal. 
                    Continue standard scouting and routine irrigation.
                </div>`;
        }

        // ==========================================
        // 8. NPK CHART GENERATION
        // ==========================================
        document.getElementById("chartPlaceholder").style.display = "none";
        updateChart(data.npk_values);

    } catch (error) {
        console.error("Fetch Error:", error);
        alert("Failed to connect to backend. Make sure your Python Flask server is running!");
    } finally {
        btn.innerText = "Analyze Crop";
        btn.disabled = false;
        btn.style.opacity = "1";
    }
}

function updateChart(npkData) {
    const ctx = document.getElementById('npkChart').getContext('2d');
    if (npkChart) npkChart.destroy();
    
    npkChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Nitrogen (N)', 'Phosphorus (P)', 'Potassium (K)'],
            datasets: [{
                label: 'Soil Nutrients',
                data: npkData,
                backgroundColor: ['#10b981', '#3b82f6', '#f59e0b'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: { y: { beginAtZero: true, max: 100 } }
        }
    });
}