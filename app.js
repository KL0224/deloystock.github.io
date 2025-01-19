async function makePrediction() {
    const datetime = document.getElementById("datetime").value;
    const resultDiv = document.getElementById("result");

    // Xóa kết quả cũ
    resultDiv.textContent = "";

    if (!datetime) {
        resultDiv.textContent = "Vui lòng nhập ngày giờ.";
        resultDiv.className = "error";
        return;
    }

    try {
        // Gửi yêu cầu đến API
        const response = await fetch("http://127.0.0.1:5000/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ input_date: datetime }),
        });

        // Xử lý phản hồi từ API
        const data = await response.json();
        if (response.ok) {
            resultDiv.textContent = `Giá dự đoán: ${data.prediction}`;
            resultDiv.className = "result";
        } else {
            resultDiv.textContent = `Lỗi: ${data.error}`;
            resultDiv.className = "error";
        }
    } catch (error) {
        resultDiv.textContent = `Lỗi kết nối: ${error.message}`;
        resultDiv.className = "error";
    }
}
