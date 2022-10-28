$.validator.addMethod("email_valid", function(value) {
    return /^\w+([-+.'][^\s]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(value);
});
$.validator.addMethod("checklower", function(value) {
    return /[a-z]/.test(value);
});
$.validator.addMethod("checkupper", function(value) {
    return /[A-Z]/.test(value);
});
$.validator.addMethod("checkdigit", function(value) {
    return /[0-9]/.test(value);
});

$(document).ready(function(){
    $('#register-user').validate({
        errorClass:"text-danger reg-warning",
        rules: {
            first_name: {
                required: true,
            },
            last_name: {
                required: true,
            },
            email: {
                email : true,
                required: true,
                email_valid: true,
            },
            password1: {
                required : true,
                minlength : 8,
                checklower: true,
                checkupper: true,
                checkdigit: true
            },
            password2: {
                required : true,
                minlength : 8,
                equalTo:"#password1"
            }
        },
        submitHandler:function(form) {
            $("#server-errors").html("")
            $("#submit-details").css("opacity", "0.5");
            $("#submit-details").css("cursor", "progress");
            $("#submit-details").prop("disabled", true);
            $.ajax({
                type: "POST",
                url : "/signup/",
                headers: {'X-CSRFToken': $("#csrf_token").val()},
                data: $(form).serialize(),
                success: function(response){
                    if(response.error){
                        $("#submit-details").css("opacity", "1");
                        $("#submit-details").css("cursor", "");
                        $("#submit-details").prop("disabled", false);
                        $("#server-errors").html(response.error)
                    }
                    else{
                        $("#server-errors").html("")
                        $("#server-success").html("Successfully registered")
                        setTimeout(function(){window.location.href = "/login/"}, 19)
                    }
                }
            })
            return false
        },
        messages :{
            first_name: {
                required: "This field is required.",
            },
            last_name: {
                required: "This field is required.",
            },
            email: {
                required : "Please provide an email.",
                email : "The email should be in this format: abc@domain.tld",
                email_valid : "Please enter a valid email."
            },
            password1: {
                required : "Please provide a password.",
                minlength : "Your password should consist of at least 8 characters.",
                checklower: "Your password should have at least 1 lowercase letter.",
                checkupper: "Your password should have at least 1 uppercase letter.",
                checkdigit: "Your password should contain at least 1 digit."
            },
            password2: {
                required : "Please re-enter your password.",
                equalTo: "Password and confirm password should be equal."
            }
        }
    });
});



function username_validation(){
  username = $('#username').val()
  check_email = /^\w+([-+.'][^\s]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*$/.test(username)
  if (username == ''){
    $('#username_error').html("Please enter your email.")
    $('#username_error').show()
    return false
  }
  else if(check_email == false){
    $('#username_error').html("Please enter valid email.")
    $('#username_error').show()
    return false
  }
  else{
    $('#username_error').hide()
    return true
  }
}

function password_validation(){
  password = $('#password').val()
  if (password == ''){
    $('#password_error').html("Please enter your password.")
    $('#password_error').show()
    return false
  }
  else{
    $('#password_error').hide()
    return true
  }
}



$('#login-btn').click(function(){
    $('#password_error').hide()
    $('#username_error').hide()
    username_validation()
    password_validation()
    if(username_validation() && password_validation()){
        username = $('#username').val()
        password = $("#password").val();
        $("#username_error").hide()
        $("#password_error").hide()
        $.ajax({
            type: "POST",
            headers: {'X-CSRFToken': $("#csrf_token").val()},
            url: "/login/",
            data: {
                "email":username,
                "password":password
            },
            success: function(response){
                console.log(response)
                if (response == 1){
                    window.location.href = "/"
                }
                else{
                    $('#password_error').html("Invalid username or password.")
                    $('#password_error').show()
                }
            }
        })
    }
})

$(document).on('keypress','#username',function (e) {
  var key = e.which;
  if(key == 13)  // the enter key code
  {
    $('#login-btn').click();
    return false;
  }
});

$(document).on('keypress','#password',function (e) {
  var key = e.which;
  if(key == 13)  // the enter key code
  {
    $('#login-btn').click();
    return false;
  }
});