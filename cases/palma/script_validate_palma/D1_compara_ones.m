% Calculam alçades d'ona de puertos i comparam amb les de onadeta
%
% Joan Villalonga 29/09/2022
% gracis Joan!! last modifed: @laloyo 28/02/2025
%--------------------------------------------------------------------------

%% INPUT

%--- Carpeta amb les dades
load('P0_puertos_2hz_v2.mat')
whos;

% Supongamos que la variable que contiene la matriz es 'data' (reemplaza por el nombre correcto)
% Verifica cuántos NaNs hay en la matriz
num_nans = sum(isnan(SL(:)));

% Cargar el archivo .mat (ya lo tienes cargado)
% load('P0_puertos_2hz_v2.mat');

% Convertir 'time' a formato datetime
time_dt = datetime(time, 'ConvertFrom', 'datenum');

% Identificar los NaNs en la variable SL
nan_indices = isnan(SL);

% Filtrar los tiempos correspondientes a los NaNs
times_with_nans = time_dt(nan_indices);

% Contar los NaNs por intervalo de tiempo
% Usamos un histograma para contar el número de NaNs por cada intervalo de tiempo
% Asegúrate de definir el intervalo que desees (por ejemplo, cada hora, cada minuto, etc.)
% En este caso, se agrupa por cada hora:

figure;
histogram(times_with_nans, 'BinMethod', 'hour');
title('Número de NaNs en función del tiempo');
xlabel('Tiempo');
ylabel('Número de NaNs');
%%
opts = detectImportOptions('table_socibPoint_ca01_202501.txt', 'FileType', 'text');
opts.DataLines = 8;  % Skip header lines
opts.VariableNames = {'Time', 'Xp', 'Yp', 'Depth', 'Hsig', 'Tm02', 'RTpeak', 'Dir'};
opts.VariableTypes = {'string', 'double', 'double', 'double', 'double', 'double', 'double', 'double'}; % Read Time as string

% Read table
vars = readtable('table_socibPoint_ca01_202501.txt', opts);

%load('Malla_ext_ca01_202501.mat')
%ona=load(['P0_onadeta',num2str(aparell),'_arduino'],'time','Hm0','Tp','Tm01','Tm02','TS','spts','period');
% comparamos con Swan

timeStr = erase(vars.Time, '.'); % Remove decimal point
timeVec = datetime(timeStr, 'InputFormat', 'yyyyMMddHHmmss');


%% Triam els paràmetres
n_fft=1024/2; %fourier cosas mejor potencias de dos

Tmin=1;
Tmax=20;

% definim alguns paràmetres nous
% interval de mstreix 
dt=0.5; % segons
n_fmax=n_fft*dt/Tmin; n_fmin=floor(n_fft*dt/Tmax);

%% Obrim la serie temporal

%--- Index que volem obrir
%t=vars.Time
%(length(t))
Hm=zeros(length(vars.Time),1);
Tm1=zeros(length(vars.Time),1);
Tm2=zeros(length(vars.Time),1);
tp=zeros(length(vars.Time),1);
spts=cell(length(vars.Time),1);
spt_news=cell(length(vars.Time),1);
spt_filt=cell(length(vars.Time),1);
TS=cell(length(vars.Time),1);
%%
ratio=TS;
rat=NaN+zeros(length(vars.Time),n_fft/2);

% h1=figure('units','centimeters','Position',[2 2 12 20]);
% h2=figure('units','centimeters','Position',[2 2 12 20]);
for n=1:length(vars.Time)
%datestr(time(n))
%--- Importem les dades
% seleccionamos trozo de serie donde vamos a realizar Transf Fourier
time_dt = datetime(time, 'ConvertFrom', 'datenum');
[mm,ind]=min(abs(time_dt-timeVec(n)));
if ind<length(time)-n_fft+1
aux=SL(ind:ind+n_fft-1);
TS{n}=aux;
%%
%% Càlcul de la nostra FFT
new_fft=fft(aux-mean(aux),n_fft);
new_spt=new_fft.*conj(new_fft);
new_spt=2*new_spt/(n_fft^2);

%quito alta y baja freq
new_spt(1:n_fmin-1)=0;
new_spt(n_fmax+1:end)=[];

new_freq=[0:length(new_spt)-1]'./(n_fft*dt);
new_freq(n_fmax+1:end)=[];
spt_news{n}=new_spt;

spt_filt{n}=new_spt.*(1-(1./(1+((((new_freq)/(2/Tmax))).^2).^2)));

new_period=1./new_freq;

%--- Càlcul de moments
m0=sum(spt_filt{n});
m1=sum(spt_filt{n}.*new_freq);
m2=sum(spt_filt{n}.*(new_freq.^2));


[m,ind2]=max(spt_filt{n});
%--- Calculam els parametres
Hm(n)=sqrt(m0)*4;
Tm1(n)=m0/m1;
Tm2(n)=sqrt(m0/m2);
tp(n)=new_period(ind2);

% ratio{n}=ona.spts{n}./(spt_news{n}*10000);
% rat(n,:)=ona.spts{n}./(spt_news{n}*10000);
end
end
%%
Hm_real=real(Hm)
%plot(timeVec,vars.Hsig, timeVec,Hm_real)
% Compute the real part of Hm
Hm_real = real(Hm);

% Create the plot
figure;
plot(timeVec, vars.Hsig, 'b', 'LineWidth', 1.5);  % Blue line for Hsig
hold on;
plot(timeVec, Hm_real, 'r', 'LineWidth', 1.5);  % Red line for Hm_real
hold off;

% Add legend
legend({'Hsig (swan)', 'Hm_{real} (calculated from puertos data)'}, 'Location', 'Best');

% Add axis labels
xlabel('Time');
ylabel('Wave Height [m]');

% Add title
title('Comparison of SWAN and Calculated Puertos Wave Heights');

% Format the x-axis to show readable time labels
datetick('x', 'dd-mmm-yyyy HH:MM', 'keeplimits', 'keepticks');

% Improve readability
grid on;
ax = gca;
ax.FontSize = 12;
ax.XTickLabelRotation = 30;
%%
%now Hsig an Tpeak on the same figure
% Create the figure
figure;

% --- Top Subplot: Tpeak comparison ---
subplot(2,1,1); % 2 rows, 1 column, first plot
plot(timeVec, vars.RTpeak, 'b', 'LineWidth', 1.5); hold on;
plot(timeVec, tp, 'r', 'LineWidth', 1.5); hold off;

% Customize subplot
legend({'RTpeak (Simulated)', 'Tp (Calculated)'}, 'Location', 'Best');
xlabel('Time');
ylabel('Peak Period [s]');
title('Comparison of Simulated and Calculated Tpeak');
datetick('x', 'dd-mmm-yyyy HH:MM', 'keeplimits', 'keepticks');
grid on;
ax = gca;
ax.FontSize = 12;
ax.XTickLabelRotation = 30;

% --- Bottom Subplot: Hsig comparison ---
subplot(2,1,2); % 2 rows, 1 column, second plot
plot(timeVec, vars.Hsig, 'b', 'LineWidth', 1.5); hold on;
plot(timeVec, Hm_real, 'r', 'LineWidth', 1.5); hold off;

% Customize subplot
legend({'Hsig (Simulated)', 'Hm_{real} (Calculated)'}, 'Location', 'Best');
xlabel('Time');
ylabel('Wave Height [m]');
title('Comparison of Simulated and Calculated Hsig');
datetick('x', 'dd-mmm-yyyy HH:MM', 'keeplimits', 'keepticks');
grid on;
ax = gca;
ax.FontSize = 12;
ax.XTickLabelRotation = 30;

% Adjust figure size and save
%set(gcf, 'Position', [100, 100, 1000, 600]); % Adjust figure size
set(gcf, 'Position', get(0, 'Screensize')); % Fullscreen figure
saveas(gcf, '/home/laloyo/swan/cases/palma/figures/Tpeak_Hsig_Comparison.png'); % Save as PNG
%%
Hm(Hm==0)=NaN;
tp(tp==0)=NaN;
tp(tp==inf)=NaN;
