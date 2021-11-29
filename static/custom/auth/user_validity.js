document.addEventListener("DOMContentLoaded", function(){
    let token = JSON.parse(localStorage.getItem('UserToken')); 
    let access = token.access;
    // console.log(access);                   
    var payload = {token : access};
    $.ajax({
        url: " http://127.0.0.1:8000/auth/jwt/verify/",
        data: payload,
        type: "POST",
        dataType : "json",
        headers: {
            content_type: 'application/json',
        },
        success: function (data) {
            // console.log(data);
        },
        error: function (jqXHR,data,status, error) {
            // console.log(data);
            // document.getElementById("notify").style.display = "block";
            // $("#heading").html('Account Verified Failed!!');
            // $("#msg").html('Activation token expired');
            // $("#notify").removeClass("alert-info alert-success").addClass("alert-warning");
            // setTimeout(function() {
            //     window.location.href = "/";
            // }, 2500);
            console.log(jqXHR);
            let refresh = token.refresh;                  
            var payload = {refresh : refresh};
            // console.log(refresh);
            $.ajax({
                url: " http://127.0.0.1:8000/token/refresh/",
                data: payload,
                type: "POST",
                dataType : "json",
                headers: {
                    content_type: 'application/json',
                },
                success: function (data) {
                    localStorage.setItem('UserToken',JSON.stringify(data));
                },
                error: function (jqXHR,data,status, error) {
                    console.log("data: " + jqXHR);
                    // document.getElementById("notify").style.display = "block";
                    // $("#heading").html('Account Verified Failed!!');
                    // $("#msg").html('Activation token expired');
                    // $("#notify").removeClass("alert-info alert-success").addClass("alert-warning");
                    setTimeout(function() {
                        window.location.href = "/";
                    }, 2500);
                }
            });
        }
    });
});