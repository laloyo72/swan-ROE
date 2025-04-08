% P0_dades_puertos
% Descarreguem les dades del mareograf de PUERTOS DEL ESTADO a 2 Hz
%--------------------------------------------------------------------------

%--- Variables que volem descarregr
variables={'TIME','SLEV'};

%--- Escollim el periode de temps que volem estudiar
tini=datenum(2025,3,8);
tfi=datenum(2025,3,8);

%--- LOOP: importam les dades
date=tini;
ndays=tfi-tini+1;
for nv=1:length(variables)
    eval([variables{nv},'_cell=cell(ndays,1)']);
end

for n=1:ndays
    date=tini+n-1;
    datestr(date)
    folder=['http://opendap.puertos.es/thredds/dodsC/tidegauge_mall/',datestr(date,'yyyy'),'/',datestr(date,'mm'),'/MIR2Z_Mallorca_Mall_3851_',datestr(date,'yyyymmdd'),'.nc4'];
    try 
    for nv=1:length(variables)
        eval([variables{nv},'_cell{n}=ncread(folder,variables{nv});']);
    end
    catch
    end
end

%%
time=cat(1,TIME_cell{:});
time=datenum(1950,1,1)+time;
SL=cat(2,SLEV_cell{:})';

save('P0_puertos_2hz_v2_202402-202502.mat','time','SL');

%%
figure
plot(time,SL)
datetick('x')