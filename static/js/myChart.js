function englishLanguage(xValues, yValues) {
    // var xValues = {{ overall_language_name | safe }};
    //     var yValues = {{ overall_language_summary | safe }};
    var barColors = ["red", "green", "blue", "orange"];
    new Chart("myChart", {
        type: "bar",
        data: {
            labels: xValues,
            datasets: [{
                backgroundColor: barColors,
                data: yValues
            }]
        },
        options: {
            legend: {display: false},
            title: {
                display: true,
                text: "Business Sentiment Analysis"
            }
        }
    });
}