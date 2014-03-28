% Mh_Ms_Mz.m - to calculate Mh for the whole wind study DEM then times Ms and MZ to make M3
% It will call functions: ascii_read.m (to read ascii data file)
%                         multiplier_calc_new.m (to run a one directional Mh calculation, 
%                               it will call Mh_new.m, findpeaks_new.m and findvalleys.m)
%                         smoothing.m (to smooth the dataset)
%                         display_data.m (to plot the dataset as an image)
%                         plottopo_m_new.m (to plot the DEM and corresponding Mh)
%                         plot_6data.m (to plot DEM with corresponding Mh, roughness, Mz, Ms and M3)
%                         rot45.m  rot45back.m to rotate (or rotate back) 45 degrees
% Lin 2004

% 2009 modifications
%
% Calculates Mh = hill shape multiplier only. 
% Much more memory efficient. 
% Now coded to run on Octave but will still run on Matlab, perhaps with VERY slight modifications (see below).
% Modified from Lin's original code, now does not rotate matrices but rather pulls out 
% a line (ns, ew, or diagonal directions) from the array holding the dem and operates on that line to produce 
% the hill shape multipliers for that direction using slight modifications of the same subroutines as Lin uses
% (the algorithm is 2-d after all!). Code then writes the computed line of hillshape multipliers back to the 
% same array that holds the dem data. The smoothing (9 by 9 smoother) is done upon output, so that there is 
% only one large array ever defined, the one that holds the original dem data. It has been tested and 
% produces identical results to the original Lin code except for some points near the boundaries when computing 
% multipliers for diagonal (eg north_east etc) winds. This difference is due to the fact that Lin's original 
% code rotates the dem and fills the resulting matrix with zeros to make it rectangular.
% Can handle a MUCH larger dem, eg has been used on 13156 by 15018 dem (25m dem covering all of Tasmania). 
%
% Note: to run on Matlab may have to change things like 'endif' and 'endfor' to 'end', not sure. 
% 
% Chris Thomas - march 2009

% NOTE: Requires that the directories ../input and ../output exist.
%       and that the directory ../input hold a file called 'dem.asc'
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


clear all
close all
clc

direction = 'e';

% check direction specification

direction = tolower(strtrim(direction));
valid = {'n','s','e','w','ne','nw','se','sw'};
if !length(strmatch(direction,valid,'exact'))
  error('invalid direction given, must be one of n,s,e,w,ne,nw,se,sw')
endif

mh_data_dir = '../output/';


% read input data

printf('Reading data...\n');
fflush(stdout);

data = ascii_read('../input/dem.asc');

nr = data.nrows;
nc = data.ncols;
xll = data.xllcorner
yll = data.yllcorner
cellsize = data.cellsize

printf('nr %d\n', nr);
printf('nc %d\n', nc);
printf('xll %f\n', xll);
printf('yll %f\n', yll);
printf('cellsize %f\n\n', cellsize);


% adjust cellsize for diagonal lines

data_spacing = data.cellsize;
if length(direction) == 2
  data_spacing = data_spacing*sqrt(2);
endif
printf('data_spacing %f\n\n', data_spacing);
fflush(stdout);

% Compute the starting positions along the boundaries depending on dir 
% Together, the direction and the starting position determines a line.
% Note that the starting positions are defined
% in terms of the 1-d index of the array.

strt_idx = [];
if index(direction,'n') > 0 
  strt_idx = [strt_idx,1:nr:nr*nc];
endif
if index(direction,'s') > 0
  strt_idx = [strt_idx,nr:nr:nr*nc];
endif
if index(direction,'e') > 0
  strt_idx = [strt_idx,(nc-1)*nr+1:nr*nc];
endif
if index(direction,'w') > 0
  strt_idx = [strt_idx,1:nr];
endif

% for the diagonal directions the corner will have 
% been counted twice so get rid of the duplicate

strt_idx = unique(strt_idx);

% now loop over the possible lines (ie over the starting positions)

ctr = 1; % counter in order to report progress to stdout

for idx = strt_idx

  printf('processing path %d of %d, index %d\n', ctr,length(strt_idx),idx);
  fflush(stdout);

  % get a line of the data
  path = make_path(nr,nc,idx,direction); % path is a vector of 1-d indices
  line = data.data(path);

  % compute the multipliers
  M = multiplier_calc(line,data_spacing);

  % write the line back to the data
  data.data(path) = M;

  ctr++;

end


  % output unsmoothed data to file

  ofn = [mh_data_dir,'mh_',direction,'.asc'];
  printf('outputting unsmoothed data to %s\n', ofn);
  fflush(stdout);
  fid = fopen(ofn,'w');

  fprintf(fid,['ncols         ',num2str(nc),'\n']);
  fprintf(fid,['nrows         ',num2str(nr),'\n']);
  fprintf(fid,['xllcorner     ',sprintf('%.2f',xll),'\n']);
  fprintf(fid,['yllcorner     ',sprintf('%.2f',yll),'\n']);
  fprintf(fid,['cellsize      ',num2str(cellsize),'\n']);
  fprintf(fid,'NODATA_value  -9999\n');

  for i=1:nr
    fprintf(fid,'%4.2f ',round(data.data(i,:)*100)/100);
    fprintf(fid,['\n']);
  endfor
  fclose(fid);

  % output smoothed data to file

  ofn = [mh_data_dir,'mh_',direction,'_smooth','.asc'];
  printf('outputting smoothed data to %s\n', ofn);
  fflush(stdout);
  fid = fopen(ofn,'w');

  fprintf(fid,['ncols         ',num2str(nc),'\n']);
  fprintf(fid,['nrows         ',num2str(nr),'\n']);
  fprintf(fid,['xllcorner     ',sprintf('%.2f',xll),'\n']);
  fprintf(fid,['yllcorner     ',sprintf('%.2f',yll),'\n']);
  fprintf(fid,['cellsize      ',num2str(cellsize),'\n']);
  fprintf(fid,'NODATA_value  -9999\n');

  % top row

  fprintf(fid, '%4.2f ',(data.data(1,1)+data.data(1,2)+data.data(2,1))/3);
  for j = 2:(nc-1)
    fprintf(fid,'%4.2f ',(data.data(1,j-1)+data.data(1,j)+data.data(1,j+1))/3);
  endfor
  fprintf(fid,'%4.2f\n',(data.data(1,nc-1)+data.data(1,nc)+data.data(2,nc))/3);

  % general rows

  for i = 2:(nr-1)
    fprintf(fid,'%4.2f ',(data.data(i-1,1)+data.data(i,1)+data.data(i+1,1))/3);
    for j = 2:(nc-1)
      fprintf(fid,'%4.2f ',(data.data(i-1,j-1)+data.data(i-1,j)+data.data(i-1,j+1) + ...
			    data.data(i,j-1) + data.data(i,j) + data.data(i,j+1) + ...
			    data.data(i+1,j-1)+data.data(i+1,j)+data.data(i+1,j+1))/9);
    endfor
    fprintf(fid,'%4.2f\n',(data.data(i-1,nc)+data.data(i,nc)+data.data(i+1,nc))/3);
  endfor

  % bottom row

  fprintf(fid, '%4.2f ',(data.data(nr,1)+data.data(nr,2)+data.data(nr-1,1))/3);
  for j = 2:(nc-1)
    fprintf(fid,'%4.2f ',(data.data(nr,j-1)+data.data(nr,j)+data.data(nr,j+1))/3);
  endfor
  fprintf(fid,'%4.2f\n',(data.data(nr,nc-1)+data.data(nr,nc)+data.data(nr-1,nc))/3);

  fclose(fid);

  printf('Finished\n');
  fflush(stdout);


