function data_struct = ascii_read(fname)


% Open file for reading
  fid = fopen(fname,'r');

 if fid == -1 
     error(['Cannot find file']);
     return
 end

% Read header information and store in structure
for i = 1:6
    tline    = fgetl(fid);
    data_str = str2num(tline(index(tline,' '):end)); 
    if i == 1
        data_struct.ncols         = data_str;
    elseif i == 2
        data_struct.nrows         = data_str;
    elseif i == 3
        data_struct.xllcorner     = data_str;
    elseif i == 4    
        data_struct.yllcorner     = data_str;
    elseif i == 5
        data_struct.cellsize      = data_str;
    elseif i == 6
        data_struct.NODATA_value  = data_str;
    end
end

% Read data
A = fscanf(fid,'%f',[data_struct.ncols,data_struct.nrows]);

% Close file
fclose(fid);

A = A';

 A(A == data_struct.NODATA_value) = NaN;

 max_data = max(max(A));
 nan_ind = isnan(A);

 A(nan_ind) = (max_data);
 data_struct.NODATA_value = (max_data);

% data_struct.data        = flipud(A);
 data_struct.data        = A;

endfunction





