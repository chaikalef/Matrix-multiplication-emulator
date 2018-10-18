
# coding: utf-8

# In[ ]:


import numpy as np
from math import ceil

old_settings = np.seterr(all = 'warn')  # Меняем настройки numpy

res_file = open('result.txt', 'w')   # Файл для записи результата
res_file.close()

log_file = open('log.txt', 'w')

m_size = (100000, 100000)       # Размер матриц
p_size = 1024                   # Количество чисел в странице
p_size_2 = p_size // 2
M_speed = 10                    # Отношение скорости загрузки к 
                                # скорости вычислений


# RAM
r_arr = [ [],                   # Матрица А
          [],                   # Матрица В
          [] ]                  # Матрица А х В

# CACHE
c_arr = [ [ [], [] ],           # [Закачиваемая подстрочка матрицы А],
                                # [Закачиваемый подстолбец матрицы В]
                                # ИЛИ НАОБОРОТ, ТАК КАК ОНИ ЧЕРЕДУЮТСЯ
          [ [], [] ],           # [Подстрочка-операнд матрицы А],
                                # [Подстолбец-операнд матрицы В]
               0     ]          # Результат произведения 
                                # подстрочки-операнда матрицы А на 
                                # подстолбец-операнд матрицы В

# MAC ARRAY
M_arr = []                      # Промежуточные произведения подстрочки
                                # и подстолбца


max_int32 = np.iinfo(np.int32).max

# Массив нулей для увеличения матрицы до размера, кратного p_size/2
zeros = np.zeros(p_size_2 * ceil(m_size[0] / p_size_2) - m_size[0],
                 dtype = np.int32)

m_real_size = (zeros.shape[0] + m_size[0], zeros.shape[0] + m_size[1])

# Количество подстрок и подстолбцов
subarr_num = ceil(m_size[0] / p_size_2)

# Порция данных передачи RAM -> CACHE
dwnld_step = ceil(p_size_2 / M_speed) 

# Чередование расположений нового и используемого массивов в CACHE
new_idx, cur_idx = (0, 1)


# Вычислитель
def MAC(a, b):
    return np.sum([a[i] * b[i] for i in range(4)])


print('-- Начало работы программы --')
print('Размер матриц: {0}'.format(m_size))
print('Размер перемножаемых матриц: {0}'.format(m_real_size))
print('Количество пустых строчек: ' + str(zeros.shape[0]))
print('Количество пустых столбцов: ' + str(zeros.shape[0]) + '\n')

print('-- Начало работы алгоритма --')
print('Размер подстрочек и подстолбцов: ' + str(p_size_2))
print('Количество подстрочек и подстолбцов: ' + str(subarr_num))
print('Размер RAM (в числах): ' + str(m_real_size[0] * m_real_size[1]))
print('Размер CACHE (в числах): ' + str(p_size) + ' + ' + str(p_size) +
      ' + 1')
print('Количество вычислителей: 16')
print('Передача RAM -> CACHE осуществляется за ' + str(M_speed) + 
      ' такта(-ов) алгоритма\n')

log_file.write('-- Начало работы программы --\n')
log_file.write('Размер матриц: {0}\n'.format(m_size))
log_file.write('Количество пустых строчек: ' + str(zeros.shape[0]) +
               '\n')
log_file.write('Количество пустых столбцов: ' + str(zeros.shape[0]) +
               '\n\n')

log_file.write('-- Начало работы алгоритма --\n')
log_file.write('Размер подстрочек и подстолбцов: ' + str(p_size_2) +
               '\n')
log_file.write('Количество подстрочек и подстолбцов: ' +
               str(subarr_num) + '\n')
log_file.write('Размер RAM (в числах): ' +
               str(m_real_size[0] * m_real_size[1]) + '\n')
log_file.write('Размер CACHE (в числах): ' + str(p_size) + ' + ' +
               str(p_size) + ' + 1\n')
log_file.write('Количество вычислителей: 16\n')
log_file.write('Передача RAM -> CACHE осуществляется за ' +
               str(M_speed) + ' такта(-ов) алгоритма\n\n')


# Цикл по строчкам матрицы А
for A_row in range(m_size[0]):
    # Создание строчки матрицы А
    r_arr_part1 = np.random.randint(max_int32, size = m_size[1])
    r_arr[0] = np.concatenate((r_arr_part1, zeros))
    
    # Цикл по столбцам матрицы В
    for B_col in range(m_size[1]):
        # Создание столбца матрицы В
        r_arr_part1 = np.random.randint(max_int32, size = m_size[0])
        r_arr[1] = np.concatenate((r_arr_part1, zeros))
        
        
        ###############################
        ### Начало работы алгоритма ###
        
        print('  Произведение строки номер ' + str(A_row + 1) + 
              ' на столбец номер ' + str(B_col + 1))
        log_file.write('  Произведение строки номер ' +
                       str(A_row + 1) + ' на столбец номер ' +
                       str(B_col + 1) + '\n')
        
        # Цикл передачи новой подстрочки матрицы А и нового подстолбца
        # матрицы В
        # dwnld_idx - индекс закачиваемой подстроки и подстолбца
        for dwnld_idx in range(subarr_num):
            
            print('    Передача RAM -> CACHE подстроки и подстолбца ' +
                  'номер ' + str(dwnld_idx + 1))
            log_file.write('    Передача RAM -> CACHE подстроки и ' +
                           'подстолбца номер ' + str(dwnld_idx + 1) +
                           '\n')
            
            # Создание массива для передачи RAM -> CACHE
            array_1024 = [r_arr[0][dwnld_idx * p_size_2:
                                   (dwnld_idx + 1) * p_size_2],
                          r_arr[1][dwnld_idx * p_size_2:
                                   (dwnld_idx + 1) * p_size_2]]
            
            # Цикл передачи пакетов RAM -> CACHE
            # M_idx - индекс итерации передачи пакетов RAM -> CACHE
            for M_idx in range(M_speed):
                
                print('      Такт алгоритма номер ' + str(M_idx + 1))
                log_file.write('      Такт алгоритма номер ' +
                               str(M_idx + 1) + '\n')
                
                # Если это первая передача RAM -> CACHE подстроки и
                # подстолбца за произведение строки на столбец
                if (dwnld_idx == 0):
                    # Первый пакет от RAM в CACHE
                    if (M_idx == 0):
                        c_arr[0][0] = array_1024[0][:dwnld_step]
                        c_arr[0][1] = array_1024[1][:dwnld_step]
                        
                        log_file.write('        В CACHE было ' +
                                       'передано ' +
                                       str(2 * c_arr[0][0].shape[0]) +
                                       ' символа(-ов)\n')
                    
                    # Последний пакет от RAM в CACHE
                    elif (M_idx == M_speed - 1):
                        c_arr[0][0] = np.concatenate(
                            (c_arr[0][0], 
                             array_1024[0][M_idx * dwnld_step:]))
                        c_arr[0][1] = np.concatenate(
                            (c_arr[0][1],
                             array_1024[1][M_idx * dwnld_step:]))
                                                     
                        print('        В CACHE были переданы все ' +
                              str(2 * c_arr[0][0].shape[0]) +
                              ' символа(-ов)\n')
                        log_file.write('        В CACHE были переданы' +
                                       ' все ' +
                                       str(2 * c_arr[0][0].shape[0]) +
                                       ' символа(-ов)\n\n')
                        print('-- Начало вычислений в MAC ARRAY --\n')
                        log_file.write('-- Начало вычислений в MAC ' +
                                       'ARRAY --\n\n')
                
                    else:
                        c_arr[0][0] = np.concatenate(
                            (c_arr[0][0],
                             array_1024[0][M_idx * dwnld_step:
                                           (M_idx + 1) * dwnld_step]))
                        c_arr[0][1] = np.concatenate(
                            (c_arr[0][1],
                             array_1024[1][M_idx * dwnld_step:
                                           (M_idx + 1) * dwnld_step]))
                                                     
                        log_file.write('        В CACHE было передано ' +
                                       str(2 * c_arr[0][0].shape[0]) +
                                       ' символа(-ов)\n')
                                                     
                  
                
                # Если это не первая передача RAM -> CACHE подстроки и
                # подстолбца за произведение строки на столбец
                else:
                    # Первый пакет от RAM в CACHE
                    if (M_idx == 0):
                        c_arr[new_idx][0] = array_1024[0][:dwnld_step]
                        c_arr[new_idx][1] = array_1024[1][:dwnld_step]
                                                     
                        log_file.write('        В CACHE было передано ' +
                                       str(2 * (M_idx + 1) * dwnld_step) +
                                       ' символа(-ов)\n')
                                                     
                        print('        Передача CACHE -> MAC ARRAY ' +
                              'номер ' + str(M_idx + 1))
                        log_file.write('        Передача CACHE -> MAC ' +
                                       'ARRAY номер ' + str(M_idx + 1) +
                                       '\n')
                        
                        # Выполнение вычислений над 128 числами
                        # idx - итератор по вычислителям
                        m_arr = [MAC(c_arr[cur_idx][0][idx * 4:
                                                       (idx + 1) * 4], 
                                     c_arr[cur_idx][1][idx * 4:
                                                       (idx + 1) * 4]) 
                                 for idx in range(0, 64, 4)]
                                                     
                        log_file.write('        Накопленная сумма в ' +
                                       'CACHE = ' + str(c_arr[2]) + '\n')
                        log_file.write('        Промежуточная сумма 128 ' +
                                       'чисел в MAC ARRAY = ' +
                                       str(np.sum(m_arr)) + '\n')
                        
                        print('        Передача MAC ARRAY -> CACHE ' +
                              'номер ' + str(M_idx + 1))
                        log_file.write('        Передача MAC ARRAY -> ' +
                                       'CACHE номер ' + str(M_idx + 1) +
                                       '\n')
                                                     
                        c_arr[2] += np.sum(m_arr)
                    
                    # Последний пакет от RAM в CACHE
                    elif (M_idx == M_speed - 1):
                        c_arr[new_idx][0] = np.concatenate(
                            (c_arr[new_idx][0],
                             array_1024[0][M_idx * dwnld_step:]))
                        c_arr[new_idx][1] = np.concatenate(
                            (c_arr[new_idx][1],
                             array_1024[1][M_idx * dwnld_step:]))
                                                           
                        print('        В CACHE были переданы все ' +
                              str(2 * c_arr[0][0].shape[0]) +
                              ' символа(-ов)\n')
                        log_file.write('        В CACHE были переданы ' +
                                       'все ' +
                                       str(2 * c_arr[0][0].shape[0]) +
                                       ' символа(-ов)\n\n')
                
                    elif (M_idx in range(1, 8)):
                        c_arr[new_idx][0] = np.concatenate(
                            (c_arr[new_idx][0],
                             array_1024[0][M_idx * dwnld_step:
                                           (M_idx + 1) * dwnld_step]))
                        c_arr[new_idx][1] = np.concatenate(
                            (c_arr[new_idx][1],
                             array_1024[1][M_idx * dwnld_step:
                                           (M_idx + 1) * dwnld_step]))
                                                           
                        log_file.write('        В CACHE было передано ' +
                                       str(2 * (M_idx + 1) * dwnld_step) +
                                       ' символа(-ов)\n')
                                                           
                        print('        Передача CACHE -> MAC ARRAY ' +
                              'номер ' + str(M_idx + 1))
                        log_file.write('        Передача CACHE -> MAC ' +
                                       'ARRAY номер ' + str(M_idx + 1) +
                                       '\n')
                                                           
                        # Выполнение вычислений над 128 числами
                        # idx - итератор по вычислителям
                        m_arr = [MAC(c_arr[cur_idx][0][idx * 4:
                                                       (idx + 1) * 4], 
                                     c_arr[cur_idx][1][idx * 4:
                                                       (idx + 1) * 4]) 
                                 for idx in range(0, 64, 4)]
                        
                        log_file.write('        Накопленная сумма в ' +
                                       'CACHE = ' + str(c_arr[2]) + '\n')
                        log_file.write('        Промежуточная сумма 128 ' +
                                       'чисел в MAC ARRAY = ' +
                                       str(np.sum(m_arr)) + '\n')
                        
                        print('        Передача MAC ARRAY -> CACHE ' +
                              'номер ' + str(M_idx + 1))
                        log_file.write('        Передача MAC ARRAY -> ' +
                                       'CACHE номер ' + str(M_idx + 1) +
                                       '\n')
                                                     
                        c_arr[2] += np.sum(m_arr)
                                                           
                    else:
                        c_arr[new_idx][0] = np.concatenate(
                            (c_arr[new_idx][0],
                             array_1024[0][M_idx * dwnld_step:
                                           (M_idx + 1) * dwnld_step]))
                        c_arr[new_idx][1] = np.concatenate(
                            (c_arr[new_idx][1],
                             array_1024[1][M_idx * dwnld_step:
                                           (M_idx + 1) * dwnld_step]))
                        
                        log_file.write('        В CACHE было передано ' +
                                       str(2 * (M_idx + 1) * dwnld_step) +
                                       ' символа(-ов)\n')
                                                           

            # Чередование расположений нового и используемого
            # массивов в CACHE
            new_idx, cur_idx = cur_idx, new_idx
          
        
        print('    Подсчёт произведения последней подстроки и ' +
              'подстолбца номер ' + str(subarr_num))
        log_file.write('    Подсчёт произведения последней подстроки ' +
                       'и подстолбца номер ' + str(subarr_num) + '\n')
        
        # Подсчёт последнего переданного блока RAM -> CACHE
        # M_idx - индекс итерации передачи пакетов CACHE -> MAC ARRAY
        for M_idx in range(8):
                
            print('      Такт алгоритма номер ' + str(M_idx + 1))
            log_file.write('      Такт алгоритма номер ' + str(M_idx + 1) +
                           '\n')
                                                            
            print('        Передача CACHE -> MAC ARRAY номер ' +
                  str(M_idx + 1))
            log_file.write('        Передача CACHE -> MAC ARRAY номер ' +
                           str(M_idx + 1) + '\n')
                                                           
            # Выполнение вычислений над 128 числами
            # idx - итератор по вычислителям
            m_arr = [MAC(c_arr[cur_idx][0][idx * 4:(idx + 1) * 4],
                         c_arr[cur_idx][1][idx * 4:(idx + 1) * 4])
                     for idx in range(0, 64, 4)]
                        
            log_file.write('        Накопленная сумма в CACHE = ' +
                           str(c_arr[2]) + '\n')
            log_file.write('        Промежуточная сумма 128 чисел в ' +
                           'MAC ARRAY = ' + str(np.sum(m_arr)) + '\n')
                        
            print('        Передача MAC ARRAY -> CACHE номер ' +
                  str(M_idx + 1))
            log_file.write('        Передача MAC ARRAY -> CACHE номер ' +
                           str(M_idx + 1) + '\n')
                                                     
            c_arr[2] += np.sum(m_arr)
                                                            
        
        print('\n  Подсчёт произведения строчки на столбец окончен')
        log_file.write('\n  Подсчёт произведения строчки на столбец ' +
                       'окончен\n')
        print('  Передача элемента {0} в матрицу A x B'.format(
            (A_row + 1, B_col + 1)))
        log_file.write('  Передача элемента {0} в матрицу A x B'.format(
            (A_row + 1, B_col + 1)) + '\n')
                                                            
        # Подсчёт произведения строчки на столбец
        # окончен - пора передать CACHE -> RAM
        r_arr[2].append(c_arr[2])
        
        row_like_str = ' '.join(str(idx) for idx in r_arr[2])
        print('  Строчка номер ' + str(A_row + 1) + ' матрицы A x B: ' +
              row_like_str)
        log_file.write('  Строчка номер ' + str(A_row + 1) +
                       ' матрицы A x B: ' + row_like_str + '\n')
                                                            
        # Сброс CACHE
        c_arr = [ [ [], [] ],
                  [ [], [] ],
                       0     ]
        new_idx, cur_idx = (0, 1)
                                                            
        print('  Выполнен сброс CACHE\n\n')
        log_file.write('  Выполнен сброс CACHE\n\n' + '\n')
     
    # Запись каждой строчки результата в файл
    res_file = open('result.txt', 'a')
    res_file.write(' '.join(str(idx) for idx in r_arr[2]) + '\n')
    res_file.close()
                                                            
    # Сброс строчки результата
    r_arr[2] = []
                                                           

print('-- Окончание работы программы --')
log_file.write('-- Окончание работы программы --\n')
print('Результат умножения в файле result.txt')
log_file.write('Результат умножения в файле result.txt\n')
print('Подробный процесс работы программы описан в log.txt')

log_file.close()
np.seterr(**old_settings)     # Устанавливаем найстройки по-умолчанию

