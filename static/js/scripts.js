// Wait until page content is loaded
document.addEventListener("DOMContentLoaded", function() {

    // --- Handle all forms ---
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function(e) {
            e.preventDefault(); // prevent immediate submission
            let action = form.getAttribute("action") || "";
            
            // Determine form type
            if (action.includes("create_loan")) {
                alert("Loan created successfully!");
            } else if (action.includes("approve_loan")) {
                alert("Loan approved successfully!");
            } else if (action.includes("collect_loan")) {
                alert("Loan collected successfully!");
            } else if (action.includes("ussd_request")) {
                alert("USSD loan request submitted successfully!");
            } else if (action.includes("export_csv")) {
                alert("CSV exported successfully!");
            } else {
                alert("Form submitted!");
            }

            // Submit form after alert
            form.submit();
        });
