from pprint import pprint
import csv
from datetime import datetime, timedelta, date, time
import re 

def is_this_correct_time(now, before):

    '''
    funkcja sprawdza poprawnosc wprowadzonych godzin
    w pliku wejsciowym, jesli rozpatrywana godzina
    bedzie "mniejsza" niz poprzednia tego samego dnia
    ustawi flage 'inconclusive'
    '''

    # konwersja na typ timedela aby moc porownac aktualnie 
    # rozpatrywana godzine z ostantio rozpatrywana godzine
    # aby wykryc ewentualne bledy z godzinami

    # czy sa to te same dni
    if now.date() == before.date():
        formated_time = now.time()
        ls = before.time()

        # formated_time_timedelta
        fr_td = timedelta(hours=formated_time.hour, minutes=formated_time.minute, seconds= formated_time.second)
        # last_timedelta
        ls_td = timedelta(hours=ls.hour, minutes=ls.minute, seconds= ls.second)

        # jesli nie to ustaw flage "inconclusive"
        if fr_td < ls_td:
            self.dict_of_all_days[formated_date].flags['inconclusive'] = "i "
            raise ValueError(f"Time of day {now} - {fr_td} is earlier than the previous one : {ls_td}")


class BatchOfWork:

    """
        klasa dla obiektu kontrolujacego ilosc "parti"
        czasu spedzonego w biurze
    """

    def __init__(self, value=1):
        self.value = value

    def increment(self):
        self.value += 1
    
    def decrement(self):
        self.value -= 1

    def set_value(self, value=1):
        self.value = value

    def get_value(self):
        return self.value

class OneDay:

    def __init__(self, date):
        self.date = date
        self.batches_of_time_in = {}
        self.sum_of_work = timedelta(seconds=0)
        self.flags = {
                'weekend':"",
                'overtime':"", 
                'undertime':"", 
                'inconclusive':"",
        }
        self.out_of_office = 1
        self.batch_obj = BatchOfWork()


    def get_date(self):
        print(self.date)

    def print_data(self):
        print("Data: ", self.date)
        print("Batches: ", self.batches_of_time_in)
        print("Sum of work: ", self.sum_of_work)
        print("Flags: ", self.flags)
        print("Out of office: ", self.out_of_office)
        print("Batch value: ", self.batch_obj.get_value())


class CollectionOfDays():
    
    def __init__(self):
        self.dict_of_all_days = dict()


    def add_day(self, day):
        date = day.date
        self.dict_of_all_days[date] = day
    
    def is_date_in_collection(self, date):
        self.date = date
        if self.date in self.dict_of_all_days.keys():
            return True
        else:
            return False

    def add_entry_hour(self, formated_day):
        '''
        funkcja dodaje do konkretnego dnia
        godzine wejsca do biura
        '''
        
        # ograniczenie daty tylko do YYYY-MM-DD
        formated_date = formated_day.date()
        
        # ograniczenie daty tylko do hh:mm:ss
        formated_time = formated_day.time()

        # indywidualny numer "partii" kazdego dnia
        batch_obj = self.dict_of_all_days[formated_date].batch_obj
        batch_value = batch_obj.get_value()


        #jesli nie ma jeszcze daty na liscie
        if self.dict_of_all_days[formated_date].batches_of_time_in == {}:
            # obiekt ktorego wartosc oznacza "partie" czasu spedzonego 
            # w biurze zaczynamy od 1 partii, jesli wyjdzie z biura, 
            # zwiekszamy ja o jeden
            batch_obj.set_value(1)
            self.dict_of_all_days[formated_date].batches_of_time_in[batch_value] = list()
        
        if batch_value in list(self.dict_of_all_days[formated_date].batches_of_time_in.keys()):
            
            # dodaj ja jako pierwsza
            if self.dict_of_all_days[formated_date].batches_of_time_in[batch_value] == list():
                

                self.dict_of_all_days[formated_date].batches_of_time_in[batch_value].append(formated_time)
                self.dict_of_all_days[formated_date].batches_of_time_in[batch_value].append(formated_time)

                # flaga na 0 - czyli jest w biurze
                self.dict_of_all_days[formated_date].out_of_office = 0


            # na miejsce czasu WYJŚCIA tymczasowo zapisywany jest 
            # ostatni czas WEJŚCIA, gdyby nie znaleziono zadnego 
            # innego czasu wyjscia to ten zostanie za niego uznany
            else: 
                # ustatawiamy flage 'inconclusive'
                self.dict_of_all_days[formated_date].flags['inconclusive'] = "i "
                self.dict_of_all_days[formated_date].batches_of_time_in[batch_value][EXIT] = formated_time
       
        # utworzenie nowej parti godzin spedzonych w biurze
        else:

            self.dict_of_all_days[formated_date].batches_of_time_in[batch_value] = list()
            
            self.dict_of_all_days[formated_date].batches_of_time_in[batch_value].append(formated_time)
            self.dict_of_all_days[formated_date].batches_of_time_in[batch_value].append(formated_time)

            # flaga na 0 - czyli jest w biurze
            self.dict_of_all_days[formated_date].out_of_office = 0

    def add_exit_hour(self, formated_day, floor_number):
        '''
        funkcja dodaje do konkretnego dnia
        godzine wyjscia z biura
        '''        
        
        # ograniczenie daty tylko do YYYY-MM-DD
        formated_date = formated_day.date()
            
        # ograniczenie daty tylko do hh:mm:ss
        formated_time = formated_day.time()

        # indywidualny numer "partii" kazdego dnia
        batch_obj = self.dict_of_all_days[formated_date].batch_obj
        batch_value = batch_obj.get_value()


        # jesli ta partia czasu znajduje sie w wartosciach
        if batch_value in list(self.dict_of_all_days[formated_date].batches_of_time_in.keys()):
            # jesli lista godzin tej partii nie jest pusta, czyli juz wszedl
            if len(self.dict_of_all_days[formated_date].batches_of_time_in[batch_value]) != 0:
                # jesli na miejscu godziny wejscia jest odpowiedni typ <datatime.time>
                if type(self.dict_of_all_days[formated_date].batches_of_time_in[batch_value][ENTRY]) == type(formated_time):

                    
                    # jesli przechodzi przez bramke na parterze
                    if floor_number == str(0):
                        # jesli znajduje sie w biurze
                        if self.dict_of_all_days[formated_date].out_of_office == 0:
                            
                            # dodaj pierwsza godzine WYJSCIA 
                            self.dict_of_all_days[formated_date].batches_of_time_in[batch_value][1] = formated_time

                            # po tym wyjsciu z biura, jesli do niego wroci
                            # utworzymy kolejna partie czasu
                            batch_obj.increment()

                            # wyszedl z biura wiec ustawiamy flage na 1
                            self.dict_of_all_days[formated_date].out_of_office = 1

                            # znaleziono czasy wyjscia wiec mozemy usunac flage
                            # jest to konieczne poniewaz w warunku wyzej profilaktycznie
                            # ja ustawiamy na wypadek gdyby nie byl podany zaden z 
                            # czasow WYJSCIA
                            self.dict_of_all_days[formated_date].flags['inconclusive'] = ""

                
        
            else:
                self.dict_of_all_days[formated_date].flags['inconclusive'] = "i "
                #raise ValueError("Nie mozesz wyjsc jak jeszcze nie weszles")
            
        # jesli nie byloby godziny WEJSCIA tego dnia, ale byly WYJSCIA
        else:
            # ustaw flage 'inconclusive'
            self.dict_of_all_days[formated_date].flags['inconclusive'] = "i "

            batch_obj.set_value(1)

            #stworz nowa liste ktora bedzie przechowywala [czas_rozpoczacia, czas_zakonczenia]
            self.dict_of_all_days[formated_date].batches_of_time_in[batch_value] = list()
            
            # wypelnij liste najpierw godzina WEJSCIA rowna 00:00:00
            self.dict_of_all_days[formated_date].batches_of_time_in[batch_value].append(time(second=0))
            # i index 1 faktyczna godzina WYJSCIA 
            self.dict_of_all_days[formated_date].batches_of_time_in[batch_value].append(formated_time)

            # flaga na 1 - czyli jest poza biurem
            self.dict_of_all_days[formated_date].out_of_office = 1


    def fill_days_with_worktime(self, input_list):

        for row in input_list:

            # konwersja daty z str na datetime.datetime
            
            formated_day = get_formated_date(row[DATE])

            # test czy nastepna godzina tego samego dnia nie jest "wczesniejsza"
            # od poprzednich
            try:
                is_this_correct_time(formated_day, last_day)
            except NameError:
                pass
            
            last_day = formated_day
            

            #jesli jest to godzina WEJSCIA
            if "entry" in row[EVENT]:
                self.add_entry_hour(formated_day)


            # jesli jest to godzina WYJSCIA
            elif "exit" in row[EVENT]:

                # numer pietra na ktorym znajduje sie bramka 
                floor_number = row[GATE][2] 
                self.add_exit_hour(formated_day, floor_number)


    def print_collection(self):
        for obj in self.dict_of_all_days.values():
            obj.print_data()
            print("-"*20)

def read_rows_from_input():

    '''
    funkcja probuje otworzyc plik input.csv,
    sprawdza czy istnieje, czy nie jest pusty
    i zwraca wiersze w postaci listy bez naglowka 
    '''

    with open('input.csv', 'r') as input_file:
        
        try:
            input_read = csv.reader(input_file, delimiter=';')
        except ValueError:
            raise ValueError("""Incorrect data format, should be:
                                '%Y-%m-%d %H:%M:%S ;Reader [event]; E/[]/KD1/[]-[]
                                """)
        except FileNotFoundError:
            raise FileNotFoundError(" Could not open file 'input.csv' ")

        input_list = list(input_read)

        # jesli plik nie jest pusty
        if (len(input_list) == 0):
            raise ValueError("Input file is empty!")
        
        return input_list[1:]

def validation_of_rows(input_list):

    i_date = 0
    i_event = 1
    i_gate  = 2

    for row in input_list:

        if row == []:       # jesli mamy pusty wiersz to go usun
            input_list.remove(row)
        
        else:

            # format daty
            #pattern_date = re.compile(r'[0-2][0-9]{3}-[0-1][0-9]-[0-3][')
            try:
                datetime.strptime(row[i_date], '%Y-%m-%d %H:%M:%S ')
            except ValueError as err:
                print(err)


            # format eventu
            pattern_event = re.compile(r'Reader (exit|entry)')

            matched_event = re.match(pattern_event, row[i_event])
            is_matched_event = bool(matched_event)

            if is_matched_event is False:
                raise ValueError(f'Event data does not match format: Reader (exit|entry)')

            #format bramki
            pattern_gate = re.compile(r'^E/[0-3]/KD1/[0-9]-[0-9]$')

            matched_gate = re.match( pattern_gate, row[i_gate])
            is_matched_gate = bool(matched_gate)

            if is_matched_gate is False:
                raise ValueError(f'Data Gate does not match format: E/[0-3]/KD1/[0-9]-[0-9]')

def get_formated_date(str_date):

    ''' 
    funkcja przyjmuje date jako string w 
    formacie YYYY-MM-DD hh:mm:ss i zwraca
    ja jako obiekt datetime.datetime
    '''

    return datetime.strptime(str_date, "%Y-%m-%d %H:%M:%S ")

def create_all_days(input_list, colleciton_of_days):

    '''
    funkcja tworzy slownik w ktorych kluczami
    sa daty zczytane z pliku
    '''


    for index in range(len(input_list)):

        batch_obj = BatchOfWork()


        formated_day = get_formated_date(input_list[index][DATE])

        formated_date = formated_day.date()
        
        one_day = OneDay(formated_date)

        if colleciton_of_days.is_date_in_collection(formated_date) is False:
            colleciton_of_days.add_day(one_day)



# -------------------- Koniec funkcji -------------------------

# stale odpowiadajace wartosciom w liscie zebranej z pliku "input.csv"
DATE  = 0   
EVENT = 1    
GATE  = 2 

# stale odpowiadajace indeksom w liscie skladajacej sie z [czasu_wejscia, czasu_wyjscia] (z biura)
ENTRY = 0
EXIT = 1


# utworzenie listy elementow z pominieciem naglowka
input_list = read_rows_from_input()  

# sprawdzenie poprawnosci wpisanych danych
validation_of_rows(input_list)  

colleciton_of_days = CollectionOfDays()

create_all_days(input_list, colleciton_of_days)


colleciton_of_days.fill_days_with_worktime(input_list)
    
colleciton_of_days.print_collection()


    