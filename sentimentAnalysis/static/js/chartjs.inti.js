function barChart(dataValues, labelvalues)
{
    new Chart(document.getElementById("bar"), {
        type: 'bar',
        data: {
            labels: labelvalues,
            datasets: [{
                label: "Sentiment Analysis",
                backgroundColor: "#29b57d",
                borderColor: "#29b57d",
                borderWidth: 1,
                hoverBackgroundColor: "#29b57d",
                hoverBorderColor:"#29b57d",
                data: dataValues,
            }]
        },
        options: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Sentiment Analysis'
          }
        }
    });

}
function pieChart(dataValue)
{
    new Chart(document.getElementById("pie"), {
        type: 'pie',
        data:{
            labels: ["Negative", "Positive", "Neutral"],
            datasets: [{
                data: dataValue,
                 backgroundColor: ["#2ab57d", "#ebeff2","#00aba9"],
                  hoverBorderColor: "#fff"

            }]
        },
        options: {
            title: {
              display: true,
              text: 'Sentiment Analysis'
            }
          }
    });

}
function donutChart(dataValues, labelValues)
{
    new Chart(document.getElementById("doughnut"), {
        type: 'doughnut',
        data:{
            labels: labelValues,
                datasets: [{
                    data: dataValues,
                    backgroundColor: ["#5156be", "#ebeff2", "#23ae78", "#ee2390"] ,
                    hoverBorderColor: "#fff"
                }]
        },
        options: {
            title: {
              display: true,
              text: 'Sentiment Analysis'
            }
          }
    });
}