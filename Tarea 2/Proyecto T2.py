# Acá van las librerías que vamos a ocupar :)
import csv                                   # Para leer archivo
import numpy as np                           # Útil para procesos matemáticos 
import math
from datetime import date as dt              # Para trabajar con fechas y diferencias de fechas 
from dateutil import relativedelta as rd
import matplotlib.pyplot as plt              # Plotting 
import pickle     

# Primero debemos cargar los archivos 
with open('TSLA.csv', 'r', encoding='utf-8') as file:
    data = csv.DictReader(file)
    data = [row for row in data] 

# data: Lista de entradas en el .csv en formato de diccionario, por ejemplo...
print('Ejemplo d in data: {}'.format(data[0]))

# Fecha a objeto date_time
def str_to_dt(date): 
    date = date.split('-')
    return dt(int(date[0]), int(date[1]), int(date[2]))

# Función que checkea si la fecha esta dentro del rango deseado:
def date_check(date, lim_date='2023-04-10'):
    date = date.split('-')
    date = dt(int(date[0]), int(date[1]), int(date[2]))
    lim_date = lim_date.split('-')
    lim_date = dt(int(lim_date[0]), int(lim_date[1]), int(lim_date[2]))
    t_delta = rd.relativedelta(lim_date, date)
    d_months = t_delta.months + t_delta.years*12
    d_days = (lim_date - date).days
    if d_months < 6: return (True, d_days)
    elif d_months == 6 and t_delta.days == 0: return (True, d_days)
    else: return (False, d_days)
    
# Filtramos los datos correspondientes a los 6 meses más recientes (desde la última entrada en el .csv).    
data = [d for d in data if date_check(d['Date'])[0]]

# Fecha desde la que trabajamos: 
print('Primera entrada considerada: {}'.format(data[0]))

Delta_t = 1/len(data)
def mu_hist(data):
    work_days = len(data)
    delta_t = Delta_t
    sum_result = 0
    for d in data: sum_result += (float(d['Close']) - float(d['Open']))/float(d['Open'])
    return sum_result/(work_days*delta_t)

def sigma_hist(data):
    mu_h = mu_hist(data)
    work_days = len(data)
    delta_t = Delta_t
    sum_result = 0
    for d in data: sum_result += ((float(d['Close']) - float(d['Open']))/float(d['Open']) - mu_h)**2
    return sum_result/((work_days-1)*delta_t)    

mu_h = mu_hist(data)
sigma_h = sigma_hist(data)
print('mu historico de TSLA últimos 6 meses: {}'.format(mu_hist(data)))   
print('sigma historico de TSLA últimos 6 meses: {}'.format(sigma_hist(data)))  

u = 1+sigma_h*np.sqrt(Delta_t)
v = 1-sigma_h*np.sqrt(Delta_t)
print('u: {}'.format(u))
print('v: {}'.format(v))

# Valor Inicial
s0 = float(data[-1]['Close'])

# Función encargada de generar todos los puntos para cada día 
# Solo contamos los días laborales 
def bin_tree_points(f_inicio='2023-04-10', f_termino='2023-10-10', s0=s0, u=u, v=v):
    f_inicio = str_to_dt(f_inicio)
    f_termino = str_to_dt(f_termino)
    days = np.busday_count(f_inicio, f_termino)
    ts = np.arange(1, days, 1)
    
    outcomes = [[(0,s0)]]
    for t in ts:
        new_outcomes = []
        for k in range(0, t+1): new_outcomes.append((t,s0*(u**k)*(v**(t-k))))
        outcomes.append(new_outcomes)
    return outcomes
    
points = bin_tree_points()

# Función de grapho útil para el siguiente ítem
###
def bin_tree_graph(f_inicio='2023-04-10', f_termino='2023-10-10', s0=s0, u=u, v=v):
    f_inicio = str_to_dt(f_inicio)
    f_termino = str_to_dt(f_termino)
    days = np.busday_count(f_inicio, f_termino)
    #days = 20
    ts = np.arange(1, days+1, 1)
    
    root = {0:{'id':0, 's':s0, 'time':0, 'father': None}}
    def recursive_builder(outcomes=root, recent_outcomes=root, time=0, last_id=0):
        # Paramos la función cuando hayamos generado todos los días 
        print('Progress: {}/{}'.format(time, days),end="\r")
        if time == days:
            return outcomes
        # Generamos los nodos nuevos en t=t+1
        new_outcomes={}
        for ro in recent_outcomes.values(): 
            new_outcomes[last_id+1]={'id':last_id+1, 's':ro['s']*u, 'time':time+1, 'father': ro['id']}
            new_outcomes[last_id+2]={'id':last_id+2, 's':ro['s']*v, 'time':time+1, 'father': ro['id']}
            last_id += 2
        outcomes.update(new_outcomes)
        # Volvemos a iterar
        return recursive_builder(outcomes=outcomes, recent_outcomes=new_outcomes, time=time+1, last_id=last_id)
    # Llamamos la función recursiva
    return recursive_builder()     
###

graph = bin_tree_graph()

# save dictionary to tree_data.pkl file
with open('tree_data.pkl', 'wb') as fp:
    pickle.dump(graph, fp)
    print('dictionary saved successfully to file')