function M = multiplier_calc(line, data_spacing)

% modified from multiplier_calc_new_v1.m to use the simpler formula of Mh
% when slope > 0.45 and in the local separation zone. But the results are
% same as multiplier_calc_new.m since when Mh was calculated > 1.71 it will
% reset to 1.71 anyway.
%
% Lin 2004

% Modified slightly by Chris Thomas 2009, so that it operates only on the line of data
% passed to it rather than a whole array. Did not alter functionality

  %n = length(line);
  %[nr nc] = size(line);
  %printf('line has size %d %d\n',nr,nc);

%initialise M to 1
  M = ones(size(line));

  fwd_line = floor(line);
  % Get the index of the ridges & valleys
  ridge_ind  = findpeaks(fwd_line); % relative ind
  valley_ind = findvalleys(fwd_line); % relative ind

  if isempty(ridge_ind) % the DEM is completely flat
    %printf('Flat line\n');
    %fflush(stdout);
  elseif length(ridge_ind) == 1 & ridge_ind(1) == 1 % the DEM is downward slope all the time
    %printf('Downward slope\n');
    %fflush(stdout);
  else % 2 general cases
    if ridge_ind(1) == 1 % (1) down up down up ....
      for i=2:length(ridge_ind)
        M = max(M, Mh(fwd_line,ridge_ind(i),valley_ind(i-1),data_spacing));
      endfor
    else % (2) up dowm up dowm ....
      for i=1:length(ridge_ind)
        M = max(M, Mh(fwd_line,ridge_ind(i),valley_ind(i),data_spacing));
      endfor
    endif
  endif

endfunction
