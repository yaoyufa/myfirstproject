$(function () {
        var url="/user/validatecode?num="
        var num=new Date().getTime()
        $('#validate_code').click(function () {
            url+=num
            $('#validate_code').attr("src",url)
         })
})