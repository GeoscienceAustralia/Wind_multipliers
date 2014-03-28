% Lin 2004

function valley = findvalleys(y)

y = -y;

yud = flipud(y);

ind = findpeaks(yud);
valley = length(y) - ind + 1;
valley = flipud(valley);
