document.getElementById('scheduleForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const email = document.getElementById('email').value;
  const endDate = document.getElementById('endDate').value;
  const studyDays = Array.from(document.getElementById('studyDays').selectedOptions).map(opt => opt.value);
  const file = document.getElementById('jsonFile').files[0];

  if (!file) {
    alert("Please upload a JSON file.");
    return;
  }

  const fileText = await file.text();
  let courseData;
  try {
    courseData = JSON.parse(fileText);
  } catch {
    alert("Invalid JSON file.");
    return;
  }

  //Send to your API (replace with actual endpoint)
  const payload = {
    email,
    endDate,
    studyDays,
    courseData
  };

  try {
    const res = await fetch("https://bzab5xsmz3.execute-api.us-east-1.amazonaws.com/dev", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const result = await res.json();
    document.getElementById("result").textContent = JSON.stringify(result, null, 2);
  } catch (err) {
    console.error(err);
    alert("Error sending data to backend.");
  }
});
