; Инициализация массива [5, -7, 0, 42] по адресам 1000..1003.
LOAD 0, 1000
LOAD 1, 1100
LOAD 2, 5
STORE 2, 0, 0
LOAD 2, -7
STORE 2, 1, 0
LOAD 2, 0
STORE 2, 2, 0
LOAD 2, 42
STORE 2, 3, 0
; Копирование через косвенное чтение и запись со смещением.
READ 0, 2
STORE 2, 0, 1
LOAD 0, 1001
READ 0, 2
STORE 2, 1, 1
LOAD 0, 1002
READ 0, 2
STORE 2, 2, 1
LOAD 0, 1003
READ 0, 2
STORE 2, 3, 1
