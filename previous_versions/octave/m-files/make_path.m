function result = make_path(nr,nc,n,dir)

% Returns a vector of array indices for a path
% starting at index n in a matrix of size nr by nc
% and proceeding in direction dir, where dir is one of 
% the 8 cardinal directions (n,s,e,w,ne,nw,se,sw). 
% Note that the array indices
% are all 1-d indices.
%
% thomas - mar 2009

  dir = tolower(dir);

  %first compute the i,j coordinates from the 1-d index n

  i = mod(n-1,nr) + 1;
  j = (n - i)/nr + 1;

  % find the i and j increments according to 
  % the directions in which we traverse

  if index(dir,'n')
    i_incr = 1;
  elseif index(dir,'s')
    i_incr = -1;
  else
    i_incr = 0;
  endif

  if index(dir,'w')
    j_incr = 1;
  elseif index(dir,'e')
    j_incr = -1;
  else
    j_incr = 0;
  endif

  % traverse, putting the positions in 1-index form

  result = [];
  while (i <= nr && i >= 1 && j <= nc && j >= 1)
    result = [result;i+(j-1)*nr];
    i +=  i_incr;
    j += j_incr;
  endwhile

endfunction
