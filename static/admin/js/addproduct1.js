$(document).ready(function () {

    var cookieop = new cookieOperate();
    var csrf = cookieop.getCookie('csrftoken');
    $('.standard-tag .close-icon').unbind().click(function () {
        $(this).parent().remove();
        $('.standard').val('');
    });
    $('.image-list-wrp .close-icon').unbind().click(function () {
        $(this).parent().remove();
        $('input[name="imglink"]').val('');
    });
    // 添加图片
    $('.new-imgurl').click(function () {
        var imgurl = $('input[name="imglink"]').val();
        if ($('.image-list-wrp .new-img-preview').length > 3) {
            alert('不允许添加超过4张产品图片');
        } else if (imgurl == "") {
            alert('图片链接不允许为空');
        } else {
            $('input[name="imglink"]').val('');
            $('.image-list-wrp').append('<span class="new-img-preview"><img src="' + imgurl + '"/><i class="close-icon">×</i></span>');
            $('.image-list-wrp .close-icon').unbind().click(function () {
                $(this).parent().remove();
                $('input[name="imglink"]').val('');
            });
        }
    });
    // 添加产品
    $('.new-pro').click(function () {
        swal({
            title: '是否添加产品?',
            text: "是否添加产品",
            type: "info",
            showCancelButton: true,
            confirmButtonColor: "#1ab394",
            confirmButtonText: "是的",
            cancelButtonText: '取消',
            closeOnConfirm: true
        }, function () {
            var standard = [];
            var imglink = [];
            $('.standard-tag .btn-primary').each(function (i, e) {
                standard.push($(e).text().replace('×', ''));
            });
            standard = standard.join('|');
            for (var i = 0; i < $('.new-img-preview img').length; i++) {
                imglink.push($('.new-img-preview img').eq(i).attr('src').replace(/#/g, ''));
            }
            $.ajax({
                cache: false,
                type: "post",
                data: {
                    first: $('.f-sec-type').val(),
                    // second: $('.s-sec-type').val(),
                    proname: $('input[name="proname"]').val(),
                    proname2: $('input[name="proname2"]').val(),

                   productjie: $('input[name="productjie"]').val(),

                    proprice: $('input[name="proprice"]').val(),
                    discount: $('input[name="discount"]').val(),
                    imglink: imglink,

                    //introinfo: $('input[name="introinfo"]').val(),
                },
                dataType: 'json',
                url: " /admin/productm/newproduct/",
                beforeSend: function (request) {
                    request.setRequestHeader("X-CSRFToken", csrf);
                },
                success: function (res) {
                    if (res.recode) {
                        window.location = window.location;
                    } else {
                        alert(res.remsg)
                    }
                }
            });
        });
    });

});