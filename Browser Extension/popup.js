$(document).ready(function() {

    baseUrl = "http://www.mashable.com";
    $.ajax({
        url: baseUrl,
        type: "get",
        dataType: "",
        success: function(data) {

            // load the response into jquery element
            // form tags are needed to get the entire html,head and body
            $foop = $('<form>' + data.responseText + '</form>');
            //console.log(data.responseText);

            // find meta tags
            $.each($foop.find("meta[content]"), function(idx, item) {
                lnk = $(item).attr("content");
                $('<option>' + lnk + '</option>').appendTo($('#meta'));
            });

            // find links
            $.each($foop.find('a[href]'), function(idx, item) {
                lnk = $(item).attr("href");
                $('<option>' + lnk + '</option>').appendTo($('#links'));
            });

            // find images bigger than 250x250
            $.each($foop.find('img[src]'), function(idx, item) {
                src = $(item).attr("src");
                if (src.indexOf('http://') == -1) {
                    src = baseUrl + src;
                }

                var img = new Image();
                img.src = src;
                img.onload = function() {
                    //alert(this.width + 'x' + this.height);
                    if (this.width > 250 && this.height > 250) {
                        $(this).appendTo($('#images'));
                    }
                }

            });

            // find contents of divs
            $.each($foop.find('div'), function(idx, item) {
                mytext = $(item).children().remove().text();
                //$('<div>'+mytext+'</div>').appendTo($('#divs'));
            });

        },
        error: function(status) {
            //console.log("request error:"+url);
        }
    });
});