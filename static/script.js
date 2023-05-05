function updateChartSize(chart) {
  chart.width = chart.canvas.clientWidth;
  chart.height = chart.canvas.clientHeight;
  chart.resize();
  chart.render({duration: 0});
}

function makeChart(chart, datas) {
    if (chart) {
      chart.destroy();
    }
    
    var date_times = datas[0];
    var temperatures = datas[1];
    
    var buffer_date = [];
    for (var i = 0; i < date_times.length; i++) {
        var myDate = new Date(date_times[i]);
        myDate = myDate.getTime();
        buffer_date.push(myDate);
    }
    
    date_times = buffer_date;
    
    var data = {
        labels: date_times,
        datasets: [{
            label: "Temperature",
            data: temperatures,
            fill: false,
            borderColor: "rgb(75, 192, 192)",
            tension: 0.1              
        }]
    };
    
    var config = {
        type: 'line',
        data: data,
        options: {
            scales: {
                x: {
                    type:'time',
                    time: {
                        unit: 'day'
                    }
                }
            }
        }
    };
    
    var myChart = new Chart(document.getElementById('myChart'), config);
    updateChartSize(myChart);
}

window.addEventListener('resize', function() {
  var chart = Chart.getChart("myChart");
  updateChartSize(chart);
});

$(document).ready(function(){
        		
               $('.set-date-btn').click(function() {
                $.ajax({
                  url: '',
                  type: 'POST',
                  contentType: 'application/json',
                  data: JSON.stringify({ 
                    button_text: $(this).text(),
                    min_date: $('.min-date').val(),
                    max_date: $('.max-date').val(),
                    width: window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth
                  }), // use JSON.stringify to send data
                  success: function(response) {

                      
                      var minmax = response.minmax;
                      var temperatures = response.temperatures;
                      var datas = response.data;
                      
                      max_temp = document.getElementById("max-temp");
                      max_temp.textContent = "max " + minmax[1][1].toString() + "°C";
                      
                      min_temp = document.getElementById("min-temp");
                      min_temp.textContent = "min " + minmax[1][0].toString() + "°C";
                      
                      med_temp = document.getElementById("med-temp");
                      med_temp.textContent = "med " + minmax[1][2].toString() + "°C";
                      
                      //graph_data = document.getElementById("graph");
                      //graph_data.src = "data:image/png;base64," + data;
                      
                      $('#temp-table').empty();
                      console.log(temperatures.length);
                      for (var i = 0; i < temperatures.length; i++) {
                          var temperature = temperatures[i];
                          console.log(temperatures[i]);
                          var row = $('<tr>');
                          
                          row.append($('<td>').addClass('my-td').text(temperature[0]));
                          row.append($('<td>').addClass('my-td').text(temperature[1]));
                          
                          $('#temp-table').append(row);   
                      }
                      
                      
                    var chart = Chart.getChart("myChart");
                    makeChart(chart, datas);

                  }
                });
              })
              
              $('.reset-btn').click(function() {
                 location.reload();
              })
})

let minDateInput = document.getElementById('min-date');
let maxDateInput = document.getElementById('max-date');

// Listen for changes to the min-date input
minDateInput.addEventListener('change', function() {
    if (minDateInput.value > maxDateInput.value) {
        maxDateInput.value = minDateInput.value;
    }
});

// Listen for changes to the max-date input
maxDateInput.addEventListener('change', function() {
    if (maxDateInput.value < minDateInput.value) {
        minDateInput.value = maxDateInput.value;
    }
});

var chart = Chart.getChart("myChart");
// var datas = {{ data | tojson }}; now in the html becose of jinja
makeChart(chart, datas);