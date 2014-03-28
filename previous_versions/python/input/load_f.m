load Ec_unstacked.mat

fid = fopen(Ec_unstacked.mat, 'r');
A = fscanf(fid,'%f')
fclose(fid);