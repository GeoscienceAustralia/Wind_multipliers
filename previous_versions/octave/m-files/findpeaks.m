function ind = findpeaks(y)
%modified from Paul Taylor's findpeaks_new3 to handle the general case of a pure flat topo
%
% Lin 2004

dy = diff(y);
%not_plateau_ind = find(dy~=0);

if length(y) == 0
    ind = [];
    return
end

if length(y) == 1
    ind = 1;
    return
end

if length(dy) == length(find(dy==0))
    ind = [];
    return
end

% ind = find( ([dy(not_plateau_ind) ; 0]<0) & ([0 ; dy(not_plateau_ind)]>0) );
ind = find( ([dy ; 0] <= 0) & ([1 ; dy] > 0) );

if ind(1) == 1
    if dy(1) == 0
        % There is a plateau at the start
        non_zero_ind = find(dy ~= 0);
        if dy(non_zero_ind(1)) > 0 
            % The plateau at the start is a valley, so remove it from the list
            ind = ind(2:end);
        end
    end
end

if ind(end) == length(y)
    if dy(end) == 0
        % There is a plateau at the end
        non_zero_ind = find(dy ~= 0);
        if dy(non_zero_ind(end)) < 0 
            % The plateau at the end is a valley, so remove it from the list
            ind = ind(1:(end-1));
        end
    end
end

% Get the values that are at the start of plateaus, or are peaks
ind = ind([0 ; diff(ind)] ~= 1);


