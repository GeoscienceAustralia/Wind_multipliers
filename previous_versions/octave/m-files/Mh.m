function m = Mh(profile,ridge,valley,data_spacing)
% modified from Mh.m to include a new formula of Mh when slope > 0.45 and
% within a local separation zone defined in Wind Loading
%
% Lin 2004
%
% modified slightly by C Thomas, March 2009, without altering its functionality
% Modifications accommodate new code that doesn't operate on whole matrix.
% Results are identical to original version   

% parameters
max_escarp = 3;
min_escarp = 0.5;
H_threshold = 10; % a hight (bwt ridge & valley) threshold for Mh calculation
Lu_threshold = data_spacing;  % a half distance (bwt ridge & valley) threshold for Mh calculation

Z = 0; %building height
dec_1pts = 1;
dec_2pts = 2;
format_2dec = '%4.2f ';
format_1dec = '%3.1f ';

nrow = length(profile);
m = ones(nrow,1);
min_h = min(profile);
max_h = max(profile);

H  = profile(ridge) - profile(valley);
Lu = abs(ridge - valley) * data_spacing/2;
slope = H/(2*Lu);
                
L1 = max(0.36*Lu,0.4*H);
L2 = 4*L1; 
                
% fL2_ind - an absolute ind for the location of the front (face wind) L2
fL2_ind = max(1, ridge - floor(L2/data_spacing)); % if fL2_ind goes before the start of DEM, chose 1

% calculate the escarpment factor using the slope from -L2 position looks to the ridge
beta_ind = min(nrow,ridge+floor(2*Lu/data_spacing)); % absolute ind with max nrow
H_r2beta = profile(ridge) - profile(beta_ind); % H_r2beta can be > = < 0
D_r2beta = (beta_ind - ridge)*data_spacing; % D_r2beta is equal 2*Lu if nrow is reached
if D_r2beta > 0 % D_r2beta can be 0, 25, 50, ...
    slope_r2mL2 = H_r2beta/D_r2beta;
    escarp_factor = 2.5 - 1.5*slope_r2mL2/slope; % when a symatrical ridge slope_r2mL2=slope so escarp_factor=1; 
                                                 % If slope_r2mL2=0, escarp_factor=2.5
    if escarp_factor < min_escarp % let us limit the factor to be at min_escarp
        escarp_factor = min_escarp;
    elseif escarp_factor > max_escarp
        escarp_factor = max_escarp; % let us limit the factor to be at most max_escarp
    end
else % the ridge is on the end
    slope_r2mL2 = 999;
    escarp_factor = 1;
end

if slope < 0.05 | H < H_threshold | Lu < Lu_threshold
    return
end

%calculate the Mh from the front L2 to the back L2 with the escarpment factor considered
for k = fL2_ind:min(nrow,ridge+floor(escarp_factor*L2/data_spacing))
     x  = (ridge - k) * data_spacing;
     if x >= 0 & x < L2 % within the region of L2 up to the ridge
          m(k) = 1 + (H/(3.5*(Z+L1))) * (1 - abs(x)/L2);
          % for larger slopes, you still use the formula to calculate M, then re-value to 1.71 when it is
          % larger. If use 1.71 for any slope greater than 0.45, then all the points within the L2 zone will
          % have 1.71 rather than a gradual increaing, peaks and decreasing pattern.
          if m(k) > 1.71
              m(k) = 1.71;
          end
     elseif slope > 0.45 & x < 0 & x > -H/4 & abs(escarp_factor - 1) < 0.2 % more or less a symetrical hill
          m(k) = 1 + 0.71 * (1 - abs(x)/(escarp_factor*L2));
     elseif x < 0 & x > -escarp_factor*L2 % within the region from the ridge2 up to the back L2
          m(k) = 1 + (H/(3.5*(Z+L1))) * (1 - abs(x)/(escarp_factor*L2));   
          if m(k) > 1.71
             m(k) = 1.71;
          end
     end

end
