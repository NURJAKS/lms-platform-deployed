"""
Seed script: run from backend dir: python seed_data.py
Requires: DATABASE_URL in .env, tables created (run app once or alembic).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal, engine, Base
from app.models import (
    User, CourseCategory, Course, CourseModule, CourseTopic,
    Test, TestQuestion, StudentProgress, CourseEnrollment, Certificate,
    AIChallenge, UserActivityLog, StudySchedule, StudentGoal, TeacherGroup,
    GroupStudent, TeacherAssignment, AssignmentSubmission, Notification,
    AIChatHistory,
)
from app.core.security import get_password_hash
from datetime import datetime, date, timezone
from decimal import Decimal

try:
    from topic_theory_content import DESCRIPTIONS_COURSE_1 as THEORY_PYTHON, DESCRIPTIONS_COURSE_2 as THEORY_WEB
except ImportError:
    THEORY_PYTHON = None
    THEORY_WEB = None

# Format: (question_text, correct_answer "a"|"b"|"c"|"d", option_a, option_b, option_c, option_d)
# Python topic 1: Python дегеніміз не?
QUESTIONS_PYTHON_TOPIC_1 = [
    ("Python - бұл не?", "a", "Программалау тілі", "Жылан", "Операциялық жүйе", "Деректер базасы"),
    ("Python қай жылы жасалған?", "b", "1985", "1991", "2000", "2010"),
    ("Python интерпретацияланатын тіл ме?", "a", "Иә", "Жоқ", "Кейде", "Білмеймін"),
    ("Python қай салада кең қолданылады?", "a", "Веб, деректер, AI", "Тек ойындар", "Тек мобильді", "Тек ОС"),
    ("Python синтаксисі қандай?", "b", "Күрделі", "Қарапайым, оқуға оңай", "Тек ағылшын", "Жоқ синтаксис"),
    ("Гвидо ван Россум кім?", "a", "Python жасаған адам", "JavaScript әзірлеуші", "Microsoft қызметкері", "Жауап жоқ"),
    ("Python бағдарламасы қалай іске қосылады?", "b", "Тек компиляция", "Интерпретатор арқылы", "Тек браузерде", "Жұмыс істемейді"),
    ("Python негізгі артықшылығы?", "a", "Оқуға оңайлық", "Ең жылдам тіл", "Тек Windows", "Тек 1 қолдану"),
    ("Python қай платформада істейді?", "c", "Тек Windows", "Тек Linux", "Windows, Linux, macOS", "Тек веб"),
    ("Python-да print() не істейді?", "a", "Мәтінді экранға шығарады", "Файл жазады", "Есептейді", "Тек оқиды"),
]
# Python topic 2: Айнымалылар және деректер түрлері
QUESTIONS_PYTHON_TOPIC_2 = [
    ("Айнымалы қалай жасалады?", "a", "x = 5", "var x", "int x", "variable x"),
    ("Тізім қандай жақшада?", "b", "()", "[]", "{}", "<>"),
    ("type() функциясы не істейді?", "a", "Деректер түрін қайтарады", "Мәтінді түрлендіреді", "Жасайды", "Жоқ"),
    ("int деген не?", "b", "Мәтін", "Бүтін сан", "Қалған сан", "Тізім"),
    ("str деген не?", "a", "Мәтін (string)", "Сан", "Логикалық", "Сөздік"),
    ("bool түрінде қандай мәндер бар?", "c", "0 және 1", "yes және no", "True және False", "а және б"),
    ("float не?", "b", "Бүтін сан", "Нақты сан (үтірлі)", "Мәтін", "Тізім"),
    ("list деген не?", "a", "Реттелген элементтер тізімі", "Жұптар жиыны", "Бір элемент", "Функция"),
    ("dict не үшін қолданылады?", "c", "Тізім сақтау", "Тек сандар", "Кілт-мән жұптары", "Мәтін"),
    ("None не?", "b", "0", "Жоқ мән (null)", "Бос тізім", "Қате"),
]
# Python topic 3: Операторлар
QUESTIONS_PYTHON_TOPIC_3 = [
    ("** операторы не істейді?", "a", "Дәрежелеу (степень)", "Көбейту", "Бөлу", "Қосу"),
    ("// операторы не?", "b", "Қалдықсыз бөлу (целочисленное)", "Қалдықпен бөлу", "Көбейту", "Дәреже"),
    ("== салыстыру не тексереді?", "a", "Теңдік", "Тең емес", "Кіші", "Үлкен"),
    ("and логикалық операторы не?", "c", "Бірінші мәні", "Екінші мәні", "Екеуі де True болса True", "Әрқашан False"),
    ("or операторы қашан True?", "a", "Кем дегенде бір операнд True", "Екеуі True", "Екеуі False", "Ешқашан"),
    ("not операторы не істейді?", "b", "Қосу", "Инверсия (терістеу)", "Көбейту", "Салыстыру"),
    ("+= не істейді?", "a", "Мәнді қосып тағайындайды", "Тек қосады", "Азайтады", "Көбейтеді"),
    ("% операторы не?", "c", "Пайыз есептейді", "Бөледі", "Бөлу қалдығын қайтарады", "Көбейтеді"),
    ("<, >, <=, >= не?", "b", "Логикалық", "Салыстыру операторлары", "Тағайындау", "Арифметикалық"),
    ("= не?", "a", "Тағайындау (мән беру)", "Теңдік тексеру", "Салыстыру", "Логикалық"),
]
# Python topic 4: Шартты операторлар
QUESTIONS_PYTHON_TOPIC_4 = [
    ("if операторы не үшін?", "a", "Шартты тексеру", "Цикл", "Функция", "Тізім"),
    ("elif не?", "b", "Бірінші шарт", "Басқа шарт (else if)", "Соңғы нұсқа", "Цикл"),
    ("else қашан орындалады?", "a", "Ешқандай шарт орындалмаса", "Бірінші шарт False болса", "Әрқашан", "Ешқашан"),
    ("Python-да блок қалай белгіленеді?", "c", "Жақшамен {}", "Жақшамен ()", "Кеңістік (indentation)", "; арқылы"),
    ("if x > 0: кейін не келуі керек?", "a", "Кеңістікпен ішке жазылған код", "Жаңа if", "Тек :", "Ештеңе"),
    ("Қанша elif қолдануға болады?", "b", "Тек 1", "Қалағанша", "0", "Тек 2"),
    ("Шартты өрнек мысалы?", "a", "x > 5", "x = 5", "x + 5", "print(x)"),
    ("and шарттарда не істейді?", "c", "Біріншісін тексереді", "Екіншісін тексереді", "Екеуін де тексереді", "Ешқайсысын"),
    ("if-elif-else тізбегінің мақсаты?", "b", "Цикл жасау", "Бірнеше нұсқадан бірін таңдау", "Функция", "Тізім"),
    ("if без else қолдануға болады ма?", "a", "Иә", "Жоқ", "Тек elif бар болса", "Тек бір рет"),
]
# Python topic 5: Циклдар
QUESTIONS_PYTHON_TOPIC_5 = [
    ("for циклы қандай көздерді қолданады?", "a", "range(), тізімдер", "loop()", "cycle()", "repeat()"),
    ("while циклы қашан тоқтайды?", "b", "Әр итерацияда", "Шарт False болғанда", "10 реттен кейін", "Ешқашан"),
    ("range(5) не береді?", "a", "0, 1, 2, 3, 4", "1, 2, 3, 4, 5", "5 сан", "0-ден 5-ке"),
    ("break не істейді?", "c", "Циклды жалғастырады", "Келесі итерацияға өтеді", "Циклдан шығарады", "Қате шығарады"),
    ("continue не істейді?", "a", "Келесі итерацияға өтеді", "Циклды тоқтатады", "Функцияны шақырады", "Ештеңе"),
    ("for элемент in [1,2,3]: — элемент не?", "b", "Индекс", "Тізімнің әр мәні", "Ұзындығы", "Функция"),
    ("Функция def арқылы жасалады ма?", "a", "Иә", "Жоқ", "Кейде", "function()"),
    ("Python-дағы None не?", "b", "0", "Жоқ мән", "Бос тізім", "Қате"),
    ("print() не істейді?", "a", "Экранға шығарады", "Оқиды", "Жазады", "Есептейді"),
    ("range(2, 6) не береді?", "c", "0, 1, 2, 3, 4, 5", "2, 6", "2, 3, 4, 5", "6 сан"),
]
TOPIC_QUESTIONS_PYTHON = [
    QUESTIONS_PYTHON_TOPIC_1,
    QUESTIONS_PYTHON_TOPIC_2,
    QUESTIONS_PYTHON_TOPIC_3,
    QUESTIONS_PYTHON_TOPIC_4,
    QUESTIONS_PYTHON_TOPIC_5,
]
PYTHON_FINAL_QUESTIONS = (
    QUESTIONS_PYTHON_TOPIC_1[:4] + QUESTIONS_PYTHON_TOPIC_2[:4] + QUESTIONS_PYTHON_TOPIC_3[:4]
    + QUESTIONS_PYTHON_TOPIC_4[:4] + QUESTIONS_PYTHON_TOPIC_5[:4]
)[:20]  # 20 questions for final

# Web topic 1: HTML тегтері
QUESTIONS_WEB_TOPIC_1 = [
    ("HTML дегеніміз не?", "a", "HyperText Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyper Transfer Markup Language"),
    ("HTML тегтері қандай жақшада жазылады?", "b", "()", "<>", "[]", "{}"),
    ("<p> тегі не үшін қолданылады?", "a", "Параграф", "Кесте", "Сілтеме", "Сурет"),
    ("<a> тегі не үшін қолданылады?", "c", "Параграф", "Тақырып", "Сілтеме (link)", "Тізім"),
    ("<img> тегі қандай атрибутпен міндетті?", "a", "src", "href", "alt", "class"),
    ("<h1> — <h6> тегтері не үшін?", "b", "Параграф", "Тақырыптар (headings)", "Тізім", "Кесте"),
    ("<ul> тегі не үшін?", "a", "Нұсқалар тізімі", "Нөмірленген тізім", "Кесте", "Параграф"),
    ("<ol> тегі не үшін?", "b", "Нұсқалар тізімі", "Нөмірленген тізім", "Кесте", "Параграф"),
    ("<div> тегі не үшін қолданылады?", "a", "Блоктық контейнер", "Мәтін", "Сілтеме", "Сурет"),
    ("HTML құжаты қай тегпен басталады?", "a", "<!DOCTYPE html>", "<html>", "<head>", "<body>"),
]
# Web topic 2: Формалар
QUESTIONS_WEB_TOPIC_2 = [
    ("<form> тегі не үшін?", "a", "Пайдаланушыдан деректер жинау", "Стиль беру", "Скрипт", "Сурет"),
    ("form action атрибуты не?", "b", "Стиль", "Деректер жіберілетін URL", "Тег атауы", "ID"),
    ("method='GET' не істейді?", "a", "Параметрлерді URL-ге қосады", "Жашырады", "Жібермейді", "Файл жібереді"),
    ("method='POST' қашан қолданылады?", "c", "Сілтеме үшін", "Көрсету үшін", "Құпия деректер жіберу", "Сурет үшін"),
    ("<input type='text'> не?", "a", "Мәтін енгізу өрісі", "Түйме", "Сұраныс", "Сілтеме"),
    ("<input type='password'> не үшін?", "b", "Электрондық пошта", "Құпия сөз енгізу", "Мәтін", "Сан"),
    ("<textarea> не үшін?", "a", "Ұзын мәтін енгізу", "Бір жол", "Түйме", "Тізім"),
    ("<select> және <option> не үшін?", "c", "Мәтін", "Құпия сөз", "Тізімнен таңдау (dropdown)", "Сурет"),
    ("name атрибуты формада не үшін?", "a", "Сервер деректерді осы атаумен алады", "Стиль", "ID", "Класс"),
    ("<button type='submit'> не істейді?", "b", "Жабады", "Форманы жібереді", "Тек көрсетеді", "Жоқ"),
]
# Web topic 3: Семантикалық HTML
QUESTIONS_WEB_TOPIC_3 = [
    ("Семантикалық HTML не?", "a", "Мағыналы тегтер (header, main, footer)", "Тек <div>", "Стиль тілі", "Скрипт"),
    ("<header> не үшін?", "b", "Төменгі бөлім", "Беттің немесе бөлімнің басы", "Негізгі мазмұн", "Қосымша"),
    ("<main> қанша рет қолданылады?", "a", "Бір рет бетке", "Қалағанша", "Ешқашан", "Тек 2"),
    ("<nav> не үшін?", "c", "Мазмұн", "Сурет", "Навигациялық сілтемелер", "Төменгі"),
    ("<article> не?", "a", "Өзіндік мазмұн (мақала, пост)", "Бүкіл бет", "Сілтеме", "Тізім"),
    ("<section> не?", "b", "Төменгі бөлім", "Тақырыптық топтасқан бөлім", "Басты мазмұн", "Навигация"),
    ("<aside> не?", "a", "Қосымша ақпарат", "Негізгі мазмұн", "Басты тақырып", "Төменгі"),
    ("<footer> не үшін?", "c", "Басы", "Навигация", "Төменгі бөлім (сілтемелер, авторлық)", "Мазмұн"),
    ("Семантикалық тегтердің артықшылығы?", "a", "Экран оқу құралдары, іздеу жүйелері", "Тек әдемі", "Жоқ", "Тек жылдам"),
    ("<div> орнына семантикалық тегтер не береді?", "b", "Тек стиль", "Мағына және қолдау", "Жылдамдық", "Ештеңе"),
]
# Web topic 4: CSS селекторлары
QUESTIONS_WEB_TOPIC_4 = [
    ("CSS селектор не?", "a", "Қандай элементтерге стиль қолданылатынын анықтайды", "Цикл", "Функция", "Айнымалы"),
    (".class селекторы не?", "b", "ID бойынша", "Класс бойынша", "Тег бойынша", "Атрибут"),
    ("#id селекторы не?", "a", "Бір элементке (id бойынша)", "Барлық класстарға", "Барлық тегтерге", "Екеуіне"),
    ("div p селекторы не таңдайды?", "c", "Тек div", "Тек p", "div ішіндегі барлық p", "Тек бірінші p"),
    ("div > p не?", "a", "Тікелей бала p (div ішінде)", "Барлық ұрпақ p", "Барлық p", "Тек div"),
    (":hover псевдоклассы не?", "b", "Тінтуір түрмекте", "Тінтуір үстінде", "Фокус алғанда", "Бірінші бала"),
    (":focus не үшін?", "a", "Элемент фокус алғанда", "Тінтуір үстінде", "Тек кнопка", "Ешқашан"),
    ("::before псевдоэлемент не істейді?", "c", "Артына мазмұн", "Жоқ", "Элемент алдына мазмұн қосады", "Стиль өшіреді"),
    ("Элемент аты бойынша селектор мысалы?", "a", "p, div, h1", ".class", "#id", "[attr]"),
    ("Комбинатор div + p не таңдайды?", "b", "div ішіндегі p", "div-тен кейінгі бірінші қатардағы p", "Барлық p", "Тек div"),
]
# Web topic 5: Flexbox
QUESTIONS_WEB_TOPIC_5 = [
    ("Flexbox не?", "a", "Элементтерді икемді орналастыру құралы", "Мәтін стилі", "Сұраныс", "Анимация"),
    ("display: flex не істейді?", "b", "Жасырады", "Контейнерді flex жасайды", "Түс береді", "Шрифт"),
    ("flex-direction не?", "a", "Негізгі ось бағыты (row/column)", "Түс", "Өлшем", "Арақашықтық"),
    ("justify-content не үшін?", "c", "Көлденең ось", "Жабу", "Негізгі ось бойынша орналасу", "Түс"),
    ("align-items не?", "a", "Көлденең ось бойынша туралау", "Негізгі ось", "Жабу", "Өлшем"),
    ("flex-wrap не?", "b", "Түс", "Жолдарға ауысу (wrap)", "Жоқ", "Тек row"),
    ("flex-grow не істейді?", "a", "Бос орынды бөледі (ұлғайтады)", "Кішірейтеді", "Жабады", "Жоқ"),
    ("flex-shrink қашан әсер етеді?", "c", "Әрқашан", "Ешқашан", "Орын жетпей қалғанда", "Тек column"),
    ("flex-direction: column не істейді?", "a", "Элементтерді тік орналастырады", "Көлденең", "Жасырады", "Айналдырады"),
    ("align-items: center не?", "b", "Солға туралайды", "Ортаға туралайды (көлденең)", "Оңға", "Жабады"),
]
# Web topic 6: Responsive дизайн
QUESTIONS_WEB_TOPIC_6 = [
    ("Responsive дизайн не?", "a", "Барлық құрылғыларға (экранға) бейімделу", "Тек мобильді", "Тек компьютер", "Тек планшет"),
    ("@media (max-width: 768px) не?", "b", "Тек түс", "Экран ені 768px-ден кіші болса стиль", "Әрқашан", "Жоқ"),
    ("viewport meta тегі не үшін?", "a", "Браузерге экран енін дұрыс көрсету", "Стиль", "Скрипт", "Сурет"),
    ("mobile-first тәсілі не?", "c", "Тек компьютерді ойлау", "Тек планшет", "Алдымен кіші экран, кейін үлкен", "Тек мобильді"),
    ("vw, vh бірліктері не?", "a", "Viewport ені/биіктігінің пайызы", "Пиксель", "Сантиметр", "Жоқ"),
    ("rem не?", "b", "Пиксель", "Түбір элементтің font-size-ы", "Тек экран", "Миллиметр"),
    ("min-width не істейді?", "a", "Ең кіші енін белгілейді", "Ең үлкен", "Тек түс", "Жоқ"),
    ("Breakpoint не?", "c", "Қате", "Түс", "Экран өлшемі (медиа сұраныста)", "Шрифт"),
    ("% бірлігі неге қолданылады?", "a", "Өрнектелген элементке қатысты", "Тек түс", "Тек шрифт", "Жоқ"),
    ("max-width медиада не тексеріледі?", "b", "Биіктік", "Экран ені шектен аспауы", "Түс", "Шрифт"),
]
# Web topic 7: JavaScript айнымалылары
QUESTIONS_WEB_TOPIC_7 = [
    ("JavaScript айнымалысы қалай жасалады?", "b", "int x", "let x немесе const x", "var x = 5", "variable x"),
    ("let және const айырмасы?", "a", "const қайта тағайындалмайды", "Жоқ айырма", "let блокта жоқ", "const жоқ"),
    ("var қайда көрінеді?", "c", "Тек блокта", "Тек функцияда", "Функция көлемінде (ескі)", "Еш жерде"),
    ("Примитивтер мысалы?", "a", "number, string, boolean", "object, array", "function", "Тек object"),
    ("undefined не?", "b", "Қате", "Мән берілмеген", "0", "null"),
    ("null не?", "a", "Жоқ мән (әдейі)", "Автоматты", "Қате", "0"),
    ("const объектінің қасиетін өзгертуге болады ма?", "c", "Жоқ", "Тек жаңа объект", "Иә (объект өзі өзгереді)", "Ешқашан"),
    ("JavaScript деректер түрлері?", "a", "Примитивтер және объектілер", "Тек сандар", "Тек мәтін", "Жоқ"),
    ("typeof операторы не қайтарады?", "b", "Мән", "Деректер түрінің атауы", "Ұзындық", "Жоқ"),
    ("block scope не?", "a", "Жақша ішіндегі көрініс аймағы", "Глобалды", "Тек функция", "Жоқ"),
]
# Web topic 8: DOM манипуляциясы
QUESTIONS_WEB_TOPIC_8 = [
    ("DOM дегеніміз не?", "a", "Document Object Model — бет құрылымы", "Data Object Model", "Design Object Model", "Жоқ"),
    ("document.getElementById() не қайтарады?", "b", "Барлық элементтер", "Бір элемент (id бойынша)", "Тізім", "Ештеңе"),
    ("querySelector() не?", "a", "Бірінші сәйкес элемент", "Барлық элементтер", "Тек id", "Жоқ"),
    ("textContent не істейді?", "c", "HTML қосады", "Стиль береді", "Мәтінді орнатады/алады", "Жоқ"),
    ("innerHTML қауіпі не?", "a", "XSS — жағымсыз скрипт енгізу мүмкін", "Жоқ", "Тек баяу", "Тек көп"),
    ("addEventListener() не үшін?", "b", "Стиль", "Оқиғаны тыңдау (click, keydown)", "Мәтін", "Сурет"),
    ("createElement() не істейді?", "a", "Жаңа DOM элементін жасайды", "Жояды", "Өзгертеді", "Жоқ"),
    ("appendChild() не істейді?", "c", "Алады", "Өшіреді", "Элементті басқа элементке қосады", "Жоқ"),
    ("classList.add() не?", "a", "Элементке класс қосады", "Жояды", "Тек оқиды", "Жоқ"),
    ("querySelectorAll() не қайтарады?", "b", "Бір элемент", "Элементтер тізімі (NodeList)", "Массив емес", "Жоқ"),
]
TOPIC_QUESTIONS_WEB = [
    QUESTIONS_WEB_TOPIC_1,
    QUESTIONS_WEB_TOPIC_2,
    QUESTIONS_WEB_TOPIC_3,
    QUESTIONS_WEB_TOPIC_4,
    QUESTIONS_WEB_TOPIC_5,
    QUESTIONS_WEB_TOPIC_6,
    QUESTIONS_WEB_TOPIC_7,
    QUESTIONS_WEB_TOPIC_8,
]
WEB_FINAL_QUESTIONS = [
    ("HTML дегеніміз не?", "a", "HyperText Markup Language", "High Tech Modern Language", "Home Tool Markup Language", "Hyper Transfer Markup Language"),
    ("HTML тегтері қандай жақшада жазылады?", "b", "()", "<>", "[]", "{}"),
    ("<p> тегі не үшін қолданылады?", "a", "Параграф", "Кесте", "Сілтеме", "Сурет"),
    ("<a> тегі не үшін қолданылады?", "c", "Параграф", "Тақырып", "Сілтеме (link)", "Тізім"),
    ("<img> тегі қандай атрибутпен міндетті?", "a", "src", "href", "alt", "class"),
    ("<h1> — <h6> тегтері не үшін?", "b", "Параграф", "Тақырыптар (headings)", "Тізім", "Кесте"),
    ("<ul> тегі не үшін?", "a", "Нұсқалар тізімі", "Нөмірленген тізім", "Кесте", "Параграф"),
    ("<ol> тегі не үшін?", "b", "Нұсқалар тізімі", "Нөмірленген тізім", "Кесте", "Параграф"),
    ("<div> тегі не үшін қолданылады?", "a", "Блоктық контейнер", "Мәтін", "Сілтеме", "Сурет"),
    ("HTML құжаты қай тегпен басталады?", "a", "<!DOCTYPE html>", "<html>", "<head>", "<body>"),
    ("CSS дегеніміз не?", "b", "Программалау тілі", "Стиль кестелер тілі", "Деректер базасы", "Фреймворк"),
    ("CSS селектор не?", "a", "Элементті таңдау құралы", "Цикл", "Функция", "Айнымалы"),
    ("Flexbox не үшін қолданылады?", "b", "Мәтінді стильдеу", "Элементтерді орналастыру", "Сұраныс жасау", "Анимация"),
    ("Responsive дизайн не?", "a", "Барлық құрылғыларға бейімделу", "Тек мобильді", "Тек компьютер", "Тек планшет"),
    ("CSS-та түс қалай көрсетіледі?", "c", "color: red", "color = red", "color: red;", "color(red)"),
    ("JavaScript дегеніміз не?", "a", "Скрипт тілі", "Стиль тілі", "Разметка тілі", "Деректер базасы"),
    ("JavaScript айнымалысы қалай жасалады?", "b", "int x", "let x", "var x = 5", "variable x"),
    ("DOM дегеніміз не?", "a", "Document Object Model", "Data Object Model", "Design Object Model", "Dynamic Object Model"),
    ("addEventListener не үшін?", "c", "Стиль қосу", "Мәтінді өзгерту", "Оқиғаны тыңдау", "Сурет қосу"),
    ("console.log() не істейді?", "a", "Консольға шығарады", "Экранға жазады", "Файлға жазады", "Ештеңе істемейді"),
]


def _add_questions_to_test(db, test_id, questions_list):
    """Add question tuples (question_text, correct, a, b, c, d) to test."""
    for i, q in enumerate(questions_list):
        db.add(TestQuestion(test_id=test_id, question_text=q[0], correct_answer=q[1], option_a=q[2], option_b=q[3], option_c=q[4], option_d=q[5], order_number=i + 1))


def seed():
    db = SessionLocal()
    try:
        # Users
        if db.query(User).filter(User.email == "admin@edu.kz").first():
            # Add director/curator if missing (for existing DBs)
            if not db.query(User).filter(User.email == "director@edu.kz").first():
                db.add(User(email="director@edu.kz", password_hash=get_password_hash("director123"), full_name="Директор", role="director"))
            if not db.query(User).filter(User.email == "curator@edu.kz").first():
                db.add(User(email="curator@edu.kz", password_hash=get_password_hash("curator123"), full_name="Куратор", role="curator"))
            db.commit()
            print("Director/curator added if missing. Skip full seed.")
            return
        admin_user = User(
            email="admin@edu.kz",
            password_hash=get_password_hash("admin123"),
            full_name="Әкімші (Администратор)",
            role="admin",
        )
        db.add(admin_user)
        db.flush()
        director_user = User(email="director@edu.kz", password_hash=get_password_hash("director123"), full_name="Директор", role="director")
        curator_user = User(email="curator@edu.kz", password_hash=get_password_hash("curator123"), full_name="Куратор", role="curator")
        db.add(director_user)
        db.add(curator_user)
        db.flush()
        teacher1 = User(
            email="teacher1@edu.kz",
            password_hash=get_password_hash("teacher123"),
            full_name="Айгүл Нұрсұлтан",
            role="teacher",
        )
        teacher2 = User(
            email="teacher2@edu.kz",
            password_hash=get_password_hash("teacher123"),
            full_name="Ерлан Қайрат",
            role="teacher",
        )
        db.add(teacher1)
        db.add(teacher2)
        db.flush()
        parent_user = User(
            email="parent@edu.kz",
            password_hash=get_password_hash("parent123"),
            full_name="Ата-ана (Родитель)",
            role="parent",
        )
        db.add(parent_user)
        db.flush()
        for i, name in enumerate(["Айдар Асқар", "Асель Дәулет", "Нұрбол Ерлан", "Гүлнар Серік", "Бекзат Мұрат"], 1):
            u = User(
                email=f"student{i}@edu.kz",
                password_hash=get_password_hash("student123"),
                full_name=name,
                role="student",
                parent_id=parent_user.id if i == 1 else None,
            )
            db.add(u)
        db.commit()
        db.refresh(admin_user)
        db.refresh(teacher1)
        db.refresh(teacher2)
        admin_id = admin_user.id
        t1_id = teacher1.id
        t2_id = teacher2.id
        student_ids = [db.query(User).filter(User.email == f"student{i}@edu.kz").first().id for i in range(1, 6)]

        # Categories
        cats = [
            ("Программалау", "Программирование", "💻"),
            ("Web-әзірлеу", "Веб-разработка", "🌐"),
            ("Деректер ғылымы", "Наука о данных", "📊"),
            ("Мобильді әзірлеу", "Мобильная разработка", "📱"),
            ("Дизайн", "Дизайн", "🎨"),
        ]
        cat_ids = []
        for name, desc, icon in cats:
            c = CourseCategory(name=name, description=desc, icon=icon)
            db.add(c)
            db.flush()
            cat_ids.append(c.id)
        db.commit()

        # Course 1: Python (active)
        c1 = Course(
            title="Python программалау негіздері",
            description="Бұл курс Python программалау тілінің негіздерімен таныстырады. Сіз айнымалылар, деректер түрлері, циклдар және функцияларды үйренесіз.",
            category_id=cat_ids[0],
            is_active=True,
            price=Decimal("30000.00"),
            language="kz",
            created_by=admin_id,
            published_at=datetime.now(timezone.utc),
            image_url="https://codedamn-blog.s3.amazonaws.com/wp-content/uploads/2022/12/10131134/Python-image-with-logo-940x530-1.webp",
        )
        db.add(c1)
        db.flush()
        course1_id = c1.id
        m1_1 = CourseModule(course_id=course1_id, title="Кіріспе", order_number=1, description="Python-ға кіріспе")
        m1_2 = CourseModule(course_id=course1_id, title="Басқару құрылымдары", order_number=2, description="Шартты операторлар және циклдар")
        db.add(m1_1)
        db.add(m1_2)
        db.flush()
        _d1 = THEORY_PYTHON if THEORY_PYTHON else [""] * 5
        topics1 = [
            (m1_1.id, "Python дегеніміз не?", 1, "/uploads/videos/course1/intro.mp4", 143, _d1[0]),
            (m1_1.id, "Айнымалылар және деректер түрлері", 2, None, None, _d1[1]),
            (m1_1.id, "Операторлар", 3, None, None, _d1[2]),
            (m1_2.id, "Шартты операторлар", 4, None, None, _d1[3]),
            (m1_2.id, "Циклдар", 5, None, None, _d1[4]),
        ]
        topic1_ids = []
        for mod_id, title, order, video, dur, desc in topics1:
            t = CourseTopic(course_id=course1_id, module_id=mod_id, title=title, order_number=order, video_url=video, video_duration=dur, description=desc)
            db.add(t)
            db.flush()
            topic1_ids.append(t.id)
        db.commit()

        # Tests for course 1 (per topic + final) — each topic gets its own question set
        for idx, tid in enumerate(topic1_ids):
            qs = TOPIC_QUESTIONS_PYTHON[idx]
            test = Test(topic_id=tid, course_id=course1_id, title=f"Тест {idx+1}", passing_score=70, question_count=len(qs), is_final=0, time_limit_seconds=600)
            db.add(test)
            db.flush()
            _add_questions_to_test(db, test.id, qs)
        final1 = Test(topic_id=None, course_id=course1_id, title="Python негіздері - Қорытынды тест", passing_score=70, question_count=len(PYTHON_FINAL_QUESTIONS), is_final=1, time_limit_seconds=1200)
        db.add(final1)
        db.flush()
        _add_questions_to_test(db, final1.id, PYTHON_FINAL_QUESTIONS)
        db.commit()

        # Course 2: Web (active)
        c2 = Course(
            title="Web-әзірлеу негіздері",
            description="HTML, CSS және JavaScript арқылы веб-сайттар жасауды үйреніңіз. Нақты жобалармен практикалық тәжірибе.",
            category_id=cat_ids[1],
            is_active=True,
            price=Decimal("35000.00"),
            language="kz",
            created_by=admin_id,
            published_at=datetime.now(timezone.utc),
            image_url="https://cdn.dribbble.com/userupload/28665909/file/original-ca7a072deb149dfe731d8de63491bfed.png?resize=752x&vertical=center",
        )
        db.add(c2)
        db.flush()
        course2_id = c2.id
        m2_1 = CourseModule(course_id=course2_id, title="HTML негіздері", order_number=1, description="HTML тегтері")
        m2_2 = CourseModule(course_id=course2_id, title="CSS стильдері", order_number=2, description="Веб-беттерді безендіру")
        m2_3 = CourseModule(course_id=course2_id, title="JavaScript негіздері", order_number=3, description="Интерактивті функционалдық")
        db.add(m2_1)
        db.add(m2_2)
        db.add(m2_3)
        db.flush()
        _d2 = THEORY_WEB if THEORY_WEB else [""] * 8
        topics2 = [
            (m2_1.id, "HTML тегтері", 1, "/uploads/videos/course2/html-tags.mp4", 294, _d2[0]),
            (m2_1.id, "Формалар", 2, None, None, _d2[1]),
            (m2_1.id, "Семантикалық HTML", 3, None, None, _d2[2]),
            (m2_2.id, "CSS селекторлары", 4, None, None, _d2[3]),
            (m2_2.id, "Flexbox", 5, None, None, _d2[4]),
            (m2_2.id, "Responsive дизайн", 6, None, None, _d2[5]),
            (m2_3.id, "JavaScript айнымалылары", 7, None, None, _d2[6]),
            (m2_3.id, "DOM манипуляциясы", 8, None, None, _d2[7]),
        ]
        for mod_id, title, order, video, dur, desc in topics2:
            t = CourseTopic(course_id=course2_id, module_id=mod_id, title=title, order_number=order, video_url=video, video_duration=dur, description=desc)
            db.add(t)
        db.commit()
        topic2_ids = [t.id for t in db.query(CourseTopic).filter(CourseTopic.course_id == course2_id).order_by(CourseTopic.order_number).all()]
        for idx, tid in enumerate(topic2_ids):
            qs = TOPIC_QUESTIONS_WEB[idx]
            test = Test(topic_id=tid, course_id=course2_id, title=f"Тест {idx+1}", passing_score=70, question_count=len(qs), is_final=0, time_limit_seconds=600)
            db.add(test)
            db.flush()
            _add_questions_to_test(db, test.id, qs)
        final2 = Test(topic_id=None, course_id=course2_id, title="Web негіздері - Қорытынды тест", passing_score=70, question_count=len(WEB_FINAL_QUESTIONS), is_final=1, time_limit_seconds=1200)
        db.add(final2)
        db.flush()
        _add_questions_to_test(db, final2.id, WEB_FINAL_QUESTIONS)
        db.commit()

        # 18 inactive courses (placeholders)
        inactive = [
            ("Машиналық оқыту негіздері", "Жасанды интеллект пен ML алгоритмдері. Жақында.", cat_ids[2], 45000, "https://www.shutterstock.com/image-illustration/robot-hand-holding-ai-ml-600nw-2661516405.jpg"),
            ("React әзірлеу", "Заманауи веб-қосымшалар жасау. Жақында.", cat_ids[1], 40000, "https://images.unsplash.com/photo-1633356122544-f134324a6cee?w=400&q=80"),
            ("Flutter мобильді әзірлеу", "iOS және Android қосымшалары. Жақында.", cat_ids[3], 42000, "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=400&q=80"),
            ("UI/UX дизайн", "Пайдаланушы интерфейсін жобалау. Жақында.", cat_ids[4], 38000, "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&q=80"),
            ("SQL және деректер базасы", "PostgreSQL, MySQL негіздері. Жақында.", cat_ids[2], 32000, "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=400&q=80"),
            ("Docker және контейнерлеу", "DevOps негіздері. Жақында.", cat_ids[0], 48000, "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRIuhHJZ4Dk-nyf6G2z4-VTm__3JSfQ1P21gA&s"),
            ("TypeScript программалау", "JavaScript супер жиыны. Жақында.", cat_ids[0], 36000, "https://images.unsplash.com/photo-1516116216624-53e697fedbea?w=400&q=80"),
            ("Node.js Backend әзірлеу", "Сервер жағын әзірлеу. Жақында.", cat_ids[0], 44000, "https://images.unsplash.com/photo-1627398242454-45a1465c2479?w=400&q=80"),
            ("Vue.js фреймворкі", "Progressive JavaScript фреймворкі. Жақында.", cat_ids[1], 38000, "https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=400&q=80"),
            ("MongoDB NoSQL база", "Құжат-бағытталған деректер базасы. Жақында.", cat_ids[2], 40000, "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?w=400&q=80"),
            ("GraphQL API", "Заманауи API дизайны. Жақында.", cat_ids[0], 42000, "https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=400&q=80"),
            ("Figma дизайн құралы", "Веб-дизайн және прототиптеу. Жақында.", cat_ids[4], 35000, "https://images.unsplash.com/photo-1561070791-2526d30994b5?w=400&q=80"),
            ("Git және GitHub", "Нұсқаларды басқару. Жақында.", cat_ids[0], 25000, "https://images.unsplash.com/photo-1618401471353-b98afee0b2eb?w=400&q=80"),
            ("AWS бұлтты қызметтер", "Amazon Web Services негіздері. Жақында.", cat_ids[0], 55000, "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80"),
            ("Кибер қауіпсіздік негіздері", "Ақпараттық қауіпсіздік. Жақында.", cat_ids[0], 50000, "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=400&q=80"),
            ("Блокчейн технологиясы", "Криптовалюта және смарт-келісімшарттар. Жақында.", cat_ids[2], 60000, "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=400&q=80"),
            ("Agile және Scrum", "Жобаларды басқару әдістемесі. Жақында.", cat_ids[0], 28000, "https://images.unsplash.com/photo-1552664730-d307ca884978?w=400&q=80"),
            ("Тестілеу және QA", "Бағдарламалық қамтаманы тестілеу. Жақында.", cat_ids[0], 38000, "https://images.unsplash.com/photo-1551434678-e076c223a692?w=400&q=80"),
        ]
        for title, desc, cat_id, price, img_url in inactive:
            db.add(Course(title=title, description=desc, category_id=cat_id, is_active=True, price=Decimal(str(price)), language="kz", created_by=admin_id, image_url=img_url, published_at=datetime.now(timezone.utc)))
        db.commit()
        print("Seed completed: users, categories, 2 active courses with modules/topics/tests, 18 mock courses (all open).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
