function fileValue(value) {
    var path = value.value;
    var extenstion = path.split('.').pop();
    if(extenstion == "pdf" || extenstion == "txt"){
        document.getElementById('image-preview').src = window.URL.createObjectURL(value.files[0]);
        var filename = path.replace(/^.*[\\\/]/, '').split('.').slice(0, -1).join('.');
        document.getElementById("filename").innerHTML = filename;
    }else{
        alert("File not supported kindly upload pdf!")
    }
}

$("#button").click(function(e) {
    $("#thead").empty();
    $("#tbody").empty();
    $('#result').empty();
   
    e.preventDefault();
    var form_data = new FormData($('#upload-file')[0]);
    $.ajax({
        type: 'POST',
        url: 'http://285b-1-22-107-169.ngrok.io//upload_file/',
        beforeSend: function(){$('.loader').show();},
        complete: function(){ $('.loader').hide();},
        data: form_data,
        contentType: false,
        cache: false,
        processData: false,
        success: function(data) {
            
            $('html, body').animate({
                scrollTop: $("#thead").offset().top
            }, 2);
            $('#result').append(` <h1 id="result_out">Extracted Entities</h1>`)

            $('#thead').append(`
                  <tr>
                  <th scope="col">Entity</th>
                  <th scope="col">Values</th>
                   </tr>  `
            );
            $.each(data.data, function(key, value) {
              $("#tbody").append(`<tr>
              <th> ${key} </th>
              <td id="vals"> ${value} </td>
              </tr>` )
            });
        },


    });
});
