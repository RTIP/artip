var input = {}

function antenna_list(data){
    antennas= []
    data.forEach(function(row) {
        antennas.push(row["antenna"]);
    });
    return antennas
}

function generate_label(source_type,scan){
    return `Scan : ${scan}`
}

function generate_graph(graph_data, bind, scan){
    var antennas = graph_data["antennas"]
    var source_type = graph_data["source_type"]
    var chart = c3.generate({
        bindto: bind,
        data: {
            json: antennas,
            keys: {
                    value: ['quack', 'rang_closure', 'detailed_flagging']
                },
            names: {
                 detailed_flagging: 'Detail Flagging',
                rang_closure: 'Closure & Rang',
                quack: 'Quack',
                antenna: 'Antenna',
                flux_calibrator: 'Flux calibrator'
            },

            type: 'bar',
            groups: [
                ['detailed_flagging', 'rang_closure', 'quack']
            ],
            order: null
        },
        title: {
            text: generate_label(source_type,scan),
            y: 100,
            padding: {top:10, bottom:16, left: 70},
            position: 'bottom'
        },

        axis: {
            y: {
                label: {
                    text:'Percentage -->',
                    position: 'outer-middle'
                },
                max:100,
                min:0,
                padding: {top: 0, bottom: 0},
                tick: {
                    count: 5
                },
            },
            x: {
                type: 'category',
                categories: antenna_list(antennas),
                label: {
                    text: 'Antenna --> ',
                    position: 'outer-center'
                },
                order: 'asc'
            }
        },
        grid: {
          y: {
            show: true
          }
        },
         tooltip: {
        format: {
            value: function(value) {
                return d3.format(",.2f")(value)+'%'
            }
        }
    }

    });
}

function loadJson(sel_source_type) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      graph_data = JSON.parse(this.responseText);
      for (var scan in graph_data) {
        source_type = graph_data[scan]["source_type"]
        if(source_type === sel_source_type){
           var aDiv = document.createElement('div');
           aDiv.id = "chart"+ scan;
           document.getElementById("container").appendChild(aDiv);
           generate_graph(graph_data[scan], '#'+aDiv.id, scan)
       }
}

    }
  };
  xhttp.open("GET", "./graph.json", true);
  xhttp.send();
}

loadJson("flux_calibrator");

function selectStage(sel_source_type) {
    document.getElementById("container").innerHTML = '';
    loadJson(sel_source_type);
}