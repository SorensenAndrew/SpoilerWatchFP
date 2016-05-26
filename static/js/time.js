// Javascript function for time

var date = new Date();

            var t = date.toString();

            var res = t.split(" ",4);

            var dateTime = res.toString();

            var theDate = dateTime.replace(/,/g , " ");

            function updateTime(){
                 return theDate;
            }
