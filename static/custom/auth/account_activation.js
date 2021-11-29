document.addEventListener("DOMContentLoaded", function(){
    setTimeout(function() {
        let uid = "{{ uid }}";
        let token = "{{ token }}";                       
        var payload = { uid : uid, token : token};
        $.ajax({
            url: "/user-management/users/activation/",
            data: payload,
            type: "POST",
            dataType : "json",
            headers: {
                content_type: 'application/json',
                'X-CSRFToken': "{{ csrf_token }}"
            },
            success: function (data) {
                document.getElementById("notify").style.display = "block";
                $("#heading").html('Account Verified!!');
                $("#msg").html('Redirecting, Please Wait...');
                $("#notify").removeClass("alert-info alert-warning").addClass("alert-success");
                setTimeout(function() {
                    window.location.href = "/";
                }, 2500);
            },
            error: function (data) {
                document.getElementById("notify").style.display = "block";
                $("#heading").html('Account Verified Failed!!');
                $("#msg").html('Activation token expired');
                $("#notify").removeClass("alert-info alert-success").addClass("alert-warning");
                setTimeout(function() {
                    window.location.href = "/";
                }, 2500);
            }
        });
    }, 1500);

});