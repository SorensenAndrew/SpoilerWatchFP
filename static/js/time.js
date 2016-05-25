var date = new Date();

            var t = date.toString();

            var res = t.split(" ",4);

            var dateTime = res.toString();

            var theDate = dateTime.replace(/,/g , " ");

            var formattedDate = document.getElementById("time").value = theDate;

            function getTime(){
                 return theDate;
            }
