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
    StudentProfile,
)
from app.core.security import get_password_hash
from datetime import datetime, date, timezone
from decimal import Decimal
from app.services.fake_student_profile import fake_student_profile_for_user_id

try:
    from topic_theory_content import DESCRIPTIONS_COURSE_1 as THEORY_PYTHON, DESCRIPTIONS_COURSE_2 as THEORY_WEB
except ImportError:
    THEORY_PYTHON = None
    THEORY_WEB = None

# Format: (question_text, correct_answer "a"|"b"|"c"|"d", option_a, option_b, option_c, option_d)
# Python topic 1: Python дегеніміз не?
QUESTIONS_PYTHON_TOPIC_1 = [
    ("Python тілін кім жасап шығарды?", "a", "Гвидо ван Россум", "Джеймс Гослинг", "Брэндан Эйх", "Ларри Пейдж"),
    ("Python қай жылы алғаш рет жарық көрді?", "c", "1989", "1995", "1991", "2000"),
    ("Python файлының кеңейтімі қандай?", "b", ".pt", ".py", ".pyt", ".txt"),
    ("Python-да мәтінді экранға шығару функциясы қалай аталады?", "a", "print()", "echo()", "console.log()", "out()"),
    ("Python компиляцияланатын тіл ме, әлде интерпретацияланатын тіл ме?", "d", "Екеуі де емес", "Компиляцияланатын", "Машиналық", "Интерпретацияланатын"),
]

# Python topic 2: Айнымалылар және деректер түрлері
QUESTIONS_PYTHON_TOPIC_2 = [
    ("Бүтін сандарды сақтау үшін қандай деректер түрі қолданылады?", "b", "float", "int", "str", "bool"),
    ("Бөлшек сандар қандай типпен белгіленеді?", "a", "float", "int", "decimal", "string"),
    ("Мәтіндік деректер типі қалай аталады?", "c", "char", "text", "str", "word"),
    ("Төмендегілердің қайсысы логикалық (boolean) мән болып табылады?", "b", "1", "True", "'True'", "yes"),
    ("type(5.5) функциясының нәтижесі қандай болады?", "d", "int", "str", "complex", "float"),
]

# Python topic 3: Операторлар
QUESTIONS_PYTHON_TOPIC_3 = [
    ("Python-да дәрежеге шығару операторы қандай?", "c", "^", "//", "**", "%"),
    ("Қалдықты табу үшін қандай оператор қолданылады?", "a", "%", "/", "//", "*"),
    ("Төмендегілердің қайсысы теңдікті тексеру операторы?", "b", "=", "==", "===", "!="),
    ("5 // 2 өрнегінің нәтижесі қандай болады?", "c", "2.5", "1", "2", "3"),
    ("'is' операторы не үшін қолданылады?", "a", "Объектілердің жадтағы мекен-жайын салыстыру үшін", "Мәндерін салыстыру үшін", "Қосу үшін", "Дәрежеге шығару үшін"),
]

# Python topic 4: Шартты операторлар
QUESTIONS_PYTHON_TOPIC_4 = [
    ("Python-да шартты тексеру қалай басталады?", "a", "if", "check", "when", "case"),
    ("Бірнеше шартты тексеру үшін қандай кілт сөз қолданылады?", "b", "else if", "elif", "elseif", "then"),
    ("Егер шарт орындалмаса, қандай блок жұмыс істейді?", "c", "finally", "catch", "else", "except"),
    ("Егер x = 5, онда 'x > 3 and x < 10' өрнегі қандай мән қайтарады?", "a", "True", "False", "5", "None"),
    ("Python-да код блоктарын қалай бөлеміз?", "d", "Жақшалар арқылы {}", "begin/end сөздерімен", "үтірлі нүкте (;) арқылы", "Шегіністер (indentation) арқылы"),
]

# Python topic 5: Циклдар
QUESTIONS_PYTHON_TOPIC_5 = [
    ("Тізімдегі элементтерді бір-бірлеп өту үшін қандай цикл қолданылады?", "b", "while", "for", "do-while", "loop"),
    ("Циклды толығымен тоқтату (үзу) үшін қандай кілт сөз қолданылады?", "c", "stop", "exit", "break", "continue"),
    ("Ағымдағы итерацияны өткізіп жіберу үшін қандай кілт сөз керек?", "a", "continue", "pass", "skip", "next"),
    ("Белгілі бір шарт 'False' болғанша қайталанатын цикл түрі?", "b", "for", "while", "until", "repeat"),
    ("range(3) функциясы қандай сандарды қайтарады?", "c", "1, 2, 3", "0, 1, 2, 3", "0, 1, 2", "3, 2, 1"),
]

TOPIC_QUESTIONS_PYTHON = [
    QUESTIONS_PYTHON_TOPIC_1,
    QUESTIONS_PYTHON_TOPIC_2,
    QUESTIONS_PYTHON_TOPIC_3,
    QUESTIONS_PYTHON_TOPIC_4,
    QUESTIONS_PYTHON_TOPIC_5,
]

PYTHON_FINAL_QUESTIONS = [
    ("Python-да MRO (Method Resolution Order) қай алгоритм негізінде жұмыс істейді?", "c", "Depth-First Search (DFS)", "Breadth-First Search (BFS)", "C3 Linearization", "Dijkstra алгоритмі"),
    ("Егер функцияның дефолттық аргументіне өзгермелі объект (мысалы def func(a=[])) берілсе, не болуы мүмкін?", "a", "Функция әр шақырылған сайын сол бір ғана тізім нысаны қайта қолданылады", "Әр шақыруда жаңа тізім жасалады", "Синтаксистік қате береді", "Тізім автоматты түрде кортежге айналады"),
    ("Decorator (декоратор) жұмыс істеу принципінің ең дәл сипаттамасы?", "b", "Ол сыныптың ішкі айнымалыларын жасырады", "Ол функцияны аргумент ретінде қабылдап, оның мінез-құлқын кеңейтетін басқа функцияны қайтаратын Жоғарғы Ретті Функция", "Ол тек класс әдістерін статикалық ету үшін қолданылады", "Ол функцияның орындалу уақытын ғана өлшеуге арналады"),
    ("Context Manager with блогында ерекше жағдай орын алғанда қалай әрекет етеді?", "d", "Exception-ды елемей, кодты әрі қарай жалғастырады", "__exit__ әдісі шақырылмай, бағдарлама құлайды", "Тек IOError болғанда ғана __exit__ шақырылады", "Қатеге қарамастан __exit__ әдісі міндетті түрде шақырылады, ресурстардың босатылуын қамтамасыз етеді"),
    ("Asyncio кітапханасында Event Loop қандай рөл атқарады?", "a", "Асинхронды тапсырмаларды, I/O операцияларын басқарады және олардың орындалу кезегін оркестрлейді", "Әрбір функция үшін жеке ОС ағынын ашады", "Барлық процессор ядроларын бір уақытта іске қосып, параллель есептеулер жасайды", "Ол тек веб-сұраныстарды кэштеу үшін қолданылады"),
]

# Web topic 1: HTML тегтері
QUESTIONS_WEB_TOPIC_1 = [
    ("HTML сөзінің толық мағынасы қандай?", "a", "Hyper Text Markup Language", "Hyperlinks and Text Markup", "Home Tool Markup Language", "Hyper Tool Language"),
    ("Ең үлкен тақырып (heading) тегін көрсетіңіз.", "d", "<h6>", "<heading>", "<head>", "<h1>"),
    ("Сілтеме жасау үшін қай тег қолданылады?", "b", "<link>", "<a>", "<href>", "<url>"),
    ("Сурет қою үшін қандай тег керек?", "c", "<picture>", "<p>", "<img>", "<image>"),
    ("HTML құжатының негізгі бөлігі қай тегтің ішіне жазылады?", "a", "<body>", "<head>", "<html>", "<main>"),
]

# Web topic 2: Формалар
QUESTIONS_WEB_TOPIC_2 = [
    ("Қолданушыдан мәлімет қабылдау үшін қандай тег қолданылады?", "b", "<receive>", "<input>", "<form>", "<text>"),
    ("Input типтерінің ішінде құпия сөз (password) жазуға арналғаны қандай?", "a", "type='password'", "type='hidden'", "type='secret'", "type='text'"),
    ("Форманы серверге жіберу (submit) үшін қандай батырма типі қолданылады?", "c", "type='send'", "type='push'", "type='submit'", "type='button'"),
    ("Көп жолды мәтін енгізу үшін қай тег қажет?", "d", "<input type='textarea'>", "<text>", "<block>", "<textarea>"),
    ("Тізімнен бірнеше нұсқаны таңдау үшін қандай тип қажет?", "b", "radio", "checkbox", "select", "text"),
]

# Web topic 3: Семантикалық HTML
QUESTIONS_WEB_TOPIC_3 = [
    ("Беттің төменгі бөлігіне (подвал) арналған семантикалық тег қалай аталады?", "a", "<footer>", "<bottom>", "<section>", "<div>"),
    ("Беттің басты навигациялық (меню) бөлігін белгілеу үшін қандай тег қолданылады?", "c", "<menu>", "<header>", "<nav>", "<links>"),
    ("Мақала немесе жаңалық сияқты жеке мағынасы бар басылымға арналған тег?", "b", "<section>", "<article>", "<main>", "<div>"),
    ("Беттің тақырыбы мен логотипі орналасатын жоғарғы бөліктің тегі?", "a", "<header>", "<top>", "<head>", "<h1>"),
    ("Негізгі контентті белгілейтін тегті көрсетіңіз.", "d", "<body>", "<content>", "<section>", "<main>"),
]

# Web topic 4: CSS селекторлары
QUESTIONS_WEB_TOPIC_4 = [
    ("CSS-те класс селекторы қалай жазылады?", "a", ".classname", "#classname", "classname", "*classname"),
    ("ID селекторы қалай жазылады?", "b", ".idname", "#idname", "idname", "$idname"),
    ("Барлық элементтерді таңдайтын әмбебап селектор (universal selector)?", "c", "&", "@", "*", "%"),
    ("CSS сөзінің толық мағынасы қандай?", "a", "Cascading Style Sheets", "Computer Style Sheets", "Creative Style Sheets", "Colorful Style Sheets"),
    ("Элементтің фондық түсін өзгерту үшін қандай қасиет қолданылады?", "b", "color", "background-color", "bg-color", "paint"),
]

# Web topic 5: Flexbox
QUESTIONS_WEB_TOPIC_5 = [
    ("Flexbox макетін қосу үшін элементке қандай қасиет беру керек?", "a", "display: flex;", "display: block;", "layout: flex;", "position: flex;"),
    ("Элементтерді көлденеңінен (негізгі ось бойынша) ортаға туралау үшін қандай қасиет қолданылады?", "b", "align-items: center;", "justify-content: center;", "text-align: center;", "vertical-align: middle;"),
    ("Элементтерді тік ось (көлденең осьті кесіп өтетін) бойынша ортаға туралау үшін?", "c", "justify-content: center;", "margin: auto;", "align-items: center;", "float: center;"),
    ("Flex-элементтері сыймай қалса, келесі қатарға өтуіне рұқсат беру үшін қандай қасиет қажет?", "d", "flex-direction: wrap;", "overflow: auto;", "display: inline-flex;", "flex-wrap: wrap;"),
    ("Flex-бағытын (direction) тік (бағана) қою үшін?", "a", "flex-direction: column;", "flex-direction: vertical", "align-items: column;", "justify-content: column;"),
]

# Web topic 6: Responsive дизайн
QUESTIONS_WEB_TOPIC_6 = [
    ("Респонсив дизайн үшін CSS-те не қолданылады?", "c", "Javascript", "HTML тегтері", "Media queries (@media)", "Тек пайыздар (%)"),
    ("Ұялы телефондардың экран енін (viewport) дұрыс көрсету үшін <head>-ке қосылатын тег?", "a", "<meta name='viewport' content='width=device-width'>", "<meta name='mobile'>", "<responsive=yes>", "<link rel='mobile'>"),
    ("Медиа сұраныс: @media (max-width: 600px) қашан жұмыс істейді?", "b", "Экран ені 600px-тен үлкен болса", "Экран ені 600px-ке дейін болса", "Экран биіктігі 600px болса", "Тек ұялы телефондарда ғана"),
    ("Сұйық (fluid) қаріп өлшемі үшін қандай өлшем бірлігі жиі қолданылады?", "d", "px", "mm", "pt", "vw / vh"),
    ("Сайтты ұялы телефонға бірінші бейімдеп, содан соң үлкен экранға жасау тәсілі?", "c", "Desktop-first", "Responsive-first", "Mobile-first", "Adaptive-design"),
]

# Web topic 7: JavaScript айнымалылары
QUESTIONS_WEB_TOPIC_7 = [
    ("JavaScript-те айнымалы жариялауға арналған жаңа кілт сөздері (ES6)?", "b", "var, const", "let, const", "def, var", "int, float"),
    ("'let' және 'const' айырмашылығы қандай?", "a", "let-ті өзгертуге болады, const-ты болмайды", "const тек сандар үшін", "Айырмашылығы жоқ", "let глобальды болады"),
    ("Деректер типін анықтау үшін қандай оператор қолданылады?", "d", "isType", "instanceof", "checkType", "typeof"),
    ("JavaScript-те массив қалай жарияланады?", "c", "var arr = (1, 2)", "var arr = {1, 2}", "var arr = [1, 2, 3]", "var arr = <1, 2>"),
    ("Теңдікті қатаң (типті де) тексеру операторы қандай?", "b", "==", "===", "=", "!=="),
]

# Web topic 8: DOM
QUESTIONS_WEB_TOPIC_8 = [
    ("DOM-ның толық мағынасы қандай?", "a", "Document Object Model", "Data Object Model", "Document Oriented Model", "Display Object Model"),
    ("ID арқылы элементті тауып алу әдісі?", "c", "getElementsByClass()", "querySelector()", "getElementById()", "findId()"),
    ("Элементке CSS классын қосу үшін қалай жазамыз?", "b", "element.class = 'new'", "element.classList.add('new')", "element.className.add()", "element.style.class = 'new'"),
    ("Батырмаға сырт еткенде оқиға қосу үшін (JS арқылы) не қолданылады?", "d", "element.click = ...", "element.onPress = ...", "element.trigger('click')", "element.addEventListener('click', ...)"),
    ("Элементтің тек мәтінін өзгерту үшін қандай қасиет керек?", "a", "textContent", "innerHTML", "value", "outerHTML"),
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
    ("Service Worker-лердің басты сипаттамасы қандай?", "a", "Олар басты ағыннан тәуелсіз, фондық режимде жұмыс істейтін прокси-сервер рөлін атқарады; кэштеуді және оффлайн жұмысты қамтамасыз етеді", "Дерекқор жүйесі", "ССS кодтарын параллельді өңдеу", "Геолокацияны бақылау"),
    ("CORS механизмі қалай жұмыс істейді және preflight (алдын ала) сұраныс (OPTIONS) қашан жіберіледі?", "b", "Ол сервердің кодтарын қорғайды және OPTIONS әрқашан жіберіледі", "Егер сұраныс 'күрделі' болса (мысалы, арнайы HTTP тақырыптары бар болса), браузер негізгі сұраныс алдында рұқсат сұрау үшін OPTIONS сұранысын жібереді", "IP жасырады және POST-та болады", "Деректерді шифрлау протоколы"),
    ("HTTP/2 хаттамасының HTTP/1.1-ден негізгі өнімділік тұрғысынан айырмашылығы неде?", "d", "Ол тек HTTPS қолдайды", "Тек JSON", "Кэштеу көп аумақты алады", "Ол Мультиплексингті қолдайды: бір TCP байланысы арқылы бір уақытта параллель блокталмастан жүктейді (head-of-line blocking проблемасынсыз)"),
    ("WebSockets және Server-Sent Events (SSE) технологияларының айырмашылығы қандай?", "a", "WebSocket қос бағытты байланыс орнатады, ал SSE тек серверден клиентке қарай бір бағытты (uni-directional) байланыс", "Бинарлық мәліметтер айырмашылығы", "Протокол айырмашылығы: UDP және TCP", "Айырмашылық жоқ"),
    ("Stored XSS шабуылы қалай жүзеге асырылады?", "b", "URL параметрлері арқылы", "Хакер зиянды JavaScript кодын веб-сайттың дерекқорына сақтайды. Кейін бұл деректерді оқыған кез-келген бейкүнә пайдаланушының браузерінде код автоматты түрде орындалады", "Cookies ұрлау арқылы (sniffing)", "Құпия сөздерді жүктеп алу"),
]



def _add_questions_to_test(db, test_id, questions_list):
    """Add question tuples (question_text, correct, a, b, c, d) to test."""
    for i, q in enumerate(questions_list):
        db.add(TestQuestion(test_id=test_id, question_text=q[0], correct_answer=q[1], option_a=q[2], option_b=q[3], option_c=q[4], option_d=q[5], order_number=i + 1))


COURSE_CATEGORIES = [
    ("Программалау", "Программирование", "💻"),
    ("Web-әзірлеу", "Веб-разработка", "🌐"),
    ("Деректер ғылымы", "Наука о данных", "📊"),
    ("Мобильді әзірлеу", "Мобильная разработка", "📱"),
    ("Дизайн", "Дизайн", "🎨"),
]


def _ensure_categories(db):
    """Return list of 5 category ids, creating categories if missing."""
    existing = db.query(CourseCategory).order_by(CourseCategory.id).limit(5).all()
    if len(existing) >= 5:
        return [c.id for c in existing[:5]]
    cat_ids = [c.id for c in existing]
    for name, desc, icon in COURSE_CATEGORIES[len(existing):]:
        c = CourseCategory(name=name, description=desc, icon=icon)
        db.add(c)
        db.flush()
        cat_ids.append(c.id)
    db.commit()
    return cat_ids[:5]


def _seed_courses_only(db, admin_id, cat_ids):
    """Create 2 full courses + 18 placeholder courses. Assumes categories exist."""
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
    m1_3 = CourseModule(course_id=course1_id, title="Функциялар және модульдер", order_number=3, description="Функциялар, сынып типтер және модульдер")
    db.add(m1_3)
    db.flush()
    _d1 = THEORY_PYTHON if THEORY_PYTHON else [""] * 10
    topics1 = [
        # Module 1: Кіріспе (5 тақырып)
        (m1_1.id, "Python дегеніміз не?",         1,  "https://www.youtube.com/watch?v=REPLACE_PYTHON_1",  600, _d1[0] if len(_d1)>0 else ""),
        (m1_1.id, "Айнымалылар және деректер түрлері",  2,  "https://www.youtube.com/watch?v=REPLACE_PYTHON_2",  600, _d1[1] if len(_d1)>1 else ""),
        (m1_1.id, "Операторлар",                     3,  "https://www.youtube.com/watch?v=REPLACE_PYTHON_3",  600, _d1[2] if len(_d1)>2 else ""),
        # Module 2: Басқару құрылымдары (2 тақырып)
        (m1_2.id, "Шартты операторлар",          4,  "https://www.youtube.com/watch?v=REPLACE_PYTHON_4",  600, _d1[3] if len(_d1)>3 else ""),
        (m1_2.id, "Циклдар",                           5,  "https://www.youtube.com/watch?v=REPLACE_PYTHON_5",  600, _d1[4] if len(_d1)>4 else ""),
        # Module 3: Функциялар және модульдер (5 тақырып)
        (m1_3.id, "Функциялар негіздері",         6,  "https://www.youtube.com/watch?v=REPLACE_PYTHON_6",  600, _d1[5] if len(_d1)>5 else ""),
        (m1_3.id, "Тізімдер және кортеждер",      7,  "https://www.youtube.com/watch?v=REPLACE_PYTHON_7",  600, _d1[6] if len(_d1)>6 else ""),
        (m1_3.id, "Сөздіктер және файлдармен жұмыс",  8,  "https://www.youtube.com/watch?v=REPLACE_PYTHON_8",  600, _d1[7] if len(_d1)>7 else ""),
        (m1_3.id, "Сынып типтер негіздері",        9,  "https://www.youtube.com/watch?v=REPLACE_PYTHON_9",  600, _d1[8] if len(_d1)>8 else ""),
        (m1_3.id, "Модульдер және пакеттер",     10, "https://www.youtube.com/watch?v=REPLACE_PYTHON_10", 600, _d1[9] if len(_d1)>9 else ""),
    ]
    topic1_ids = []
    for mod_id, title, order, video, dur, desc in topics1:
        t = CourseTopic(course_id=course1_id, module_id=mod_id, title=title, order_number=order, video_url=video, video_duration=dur, description=desc)
        db.add(t)
        db.flush()
        topic1_ids.append(t.id)
    db.commit()

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
    m2_4 = CourseModule(course_id=course2_id, title="Жобалық қолданбалар", order_number=4, description="Практикалық жобалар")
    db.add(m2_4)
    db.flush()
    _d2 = THEORY_WEB if THEORY_WEB else [""] * 12
    topics2 = [
        # Module 1: HTML негіздері
        (m2_1.id, "HTML тегтері",               1,  "https://www.youtube.com/watch?v=REPLACE_WEB_1",  600, _d2[0]  if len(_d2)>0  else ""),
        (m2_1.id, "Формалар",                    2,  "https://www.youtube.com/watch?v=REPLACE_WEB_2",  600, _d2[1]  if len(_d2)>1  else ""),
        (m2_1.id, "Семантикалық HTML",         3,  "https://www.youtube.com/watch?v=REPLACE_WEB_3",  600, _d2[2]  if len(_d2)>2  else ""),
        # Module 2: CSS стильдері
        (m2_2.id, "CSS селекторлары",          4,  "https://www.youtube.com/watch?v=REPLACE_WEB_4",  600, _d2[3]  if len(_d2)>3  else ""),
        (m2_2.id, "Flexbox",                     5,  "https://www.youtube.com/watch?v=REPLACE_WEB_5",  600, _d2[4]  if len(_d2)>4  else ""),
        (m2_2.id, "Responsive дизайн",         6,  "https://www.youtube.com/watch?v=REPLACE_WEB_6",  600, _d2[5]  if len(_d2)>5  else ""),
        # Module 3: JavaScript негіздері
        (m2_3.id, "JavaScript айнымалылары",  7,  "https://www.youtube.com/watch?v=REPLACE_WEB_7",  600, _d2[6]  if len(_d2)>6  else ""),
        (m2_3.id, "DOM манипуляциясы",       8,  "https://www.youtube.com/watch?v=REPLACE_WEB_8",  600, _d2[7]  if len(_d2)>7  else ""),
        (m2_3.id, "Оқиғалар және функциялар",    9,  "https://www.youtube.com/watch?v=REPLACE_WEB_9",  600, _d2[8]  if len(_d2)>8  else ""),
        # Module 4: Жобалық қолданбалар
        (m2_4.id, "CSS Grid жүйесі",          10, "https://www.youtube.com/watch?v=REPLACE_WEB_10", 600, _d2[9]  if len(_d2)>9  else ""),
        (m2_4.id, "Ънді веб-бет жасау",      11, "https://www.youtube.com/watch?v=REPLACE_WEB_11", 600, _d2[10] if len(_d2)>10 else ""),
        (m2_4.id, "Портфолио жобасы",           12, "https://www.youtube.com/watch?v=REPLACE_WEB_12", 600, _d2[11] if len(_d2)>11 else ""),
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


def seed():
    db = SessionLocal()
    try:
        # Users
        if db.query(User).filter(User.email == "admin@edu.kz").first():
            if "--courses-only" in sys.argv:
                admin_user = db.query(User).filter(User.email == "admin@edu.kz").first()
                admin_id = admin_user.id
                if db.query(Course).count() > 0:
                    print("Courses already exist. Skip.")
                    return
                cat_ids = _ensure_categories(db)
                _seed_courses_only(db, admin_id, cat_ids)
                print("Seed completed: categories (if missing), 2 active courses with modules/topics/tests, 18 mock courses.")
                return
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
        # Realistic Students Data
        STUDENTS_DATA = [
            {
                "email": "student1@edu.kz",
                "full_name": "Айдар Асқар",
                "phone": "+7 701 123 4567",
                "birth_date": date(2005, 5, 12),
                "city": "Алматы",
                "address": "ул. Абая, д. 45, кв. 12",
                "specialty": "Программная инженерия",
                "course": 2,
                "group": "ПИ-21A",
                "gender": "Мужской",
                "nationality": "Казах",
                "identity_card": "ID-01234567",
                "iin": "050512500123",
            },
            {
                "email": "student2@edu.kz",
                "full_name": "Асель Дәулет",
                "phone": "+7 702 987 6543",
                "birth_date": date(2006, 3, 20),
                "city": "Астана",
                "address": "пр-т Мәңгілік Ел, д. 10, кв. 8",
                "specialty": "Информационные системы",
                "course": 1,
                "group": "ИС-24C",
                "gender": "Женский",
                "nationality": "Казах",
                "identity_card": "ID-09876543",
                "iin": "060320600456",
            },
            {
                "email": "student3@edu.kz",
                "full_name": "Нұрбол Ерлан",
                "phone": "+7 705 555 1122",
                "birth_date": date(2004, 11, 30),
                "city": "Шымкент",
                "address": "ул. Рыскулова, д. 156, кв. 42",
                "specialty": "Кибербезопасность",
                "course": 3,
                "group": "КБ-21B",
                "gender": "Мужской",
                "nationality": "Казах",
                "identity_card": "ID-05551122",
                "iin": "041130500789",
            },
            {
                "email": "student4@edu.kz",
                "full_name": "Гүлнар Серік",
                "phone": "+7 747 333 4455",
                "birth_date": date(2005, 8, 15),
                "city": "Караганда",
                "address": "ул. Бухар-Жырау, д. 28, кв. 3",
                "specialty": "Программная инженерия",
                "course": 2,
                "group": "ПИ-21A",
                "gender": "Женский",
                "nationality": "Казах",
                "identity_card": "ID-03334455",
                "iin": "050815600111",
            },
            {
                "email": "student5@edu.kz",
                "full_name": "Бекзат Мұрат",
                "phone": "+7 700 777 8899",
                "birth_date": date(2006, 1, 10),
                "city": "Актобе",
                "address": "ул. Молдагуловой, д. 5, кв. 90",
                "specialty": "Web-разработка",
                "course": 1,
                "group": "ВЕБ-24A",
                "gender": "Мужской",
                "nationality": "Казах",
                "identity_card": "ID-07778899",
                "iin": "060110500222",
            },
        ]

        # Add 30 more students from seed_leaderboard_students list
        EXT_NAMES = [
            "Жандос Қанат", "Дархан Нұрлан", "Аружан Сая", "Ерлан Бекзат",
            "Айгүл Мәдина", "Нұрлан Дастан", "Айдана Серік", "Қайрат Ерлан",
            "Динара Айгүл", "Бекзат Нұрбол", "Асель Гүлнар", "Ерлан Жандос",
            "Мәдина Аружан", "Нұрсұлтан Дархан", "Сая Айдана", "Дастан Қанат",
            "Серік Динара", "Мұрат Бекзат", "Гүлнар Асель", "Қанат Нұрлан",
            "Нұрбол Мұрат", "Айгүл Ерлан", "Бекзат Сая", "Дархан Айдана",
            "Аружан Жандос", "Темірлан Асқар", "Айгерім Нұржан", "Ержан Дәулет",
            "Гүлдана Серік", "Қайсар Мұрат",
        ]
        CITIES = ["Алматы", "Астана", "Шымкент", "Караганда", "Актобе", "Тараз", "Павлодар", "Усть-Каменогорск"]
        SPECS = ["Программная инженерия", "Информационные системы", "Кибербезопасность", "Web-разработка", "Data Science"]
        
        for i, name in enumerate(EXT_NAMES, 6):
            city = CITIES[i % len(CITIES)]
            spec = SPECS[i % len(SPECS)]
            gender = "Женский" if any(x in name for x in ["Аружан", "Айгүл", "Айдана", "Динара", "Асель", "Сая", "Гүлнар", "Айгерім", "Гүлдана"]) else "Мужской"
            STUDENTS_DATA.append({
                "email": f"student{i}@edu.kz",
                "full_name": name,
                "phone": f"+7 707 {i:03d} {i:04d}",
                "birth_date": date(2004 + (i % 3), 1 + (i % 12), 1 + (i % 28)),
                "city": city,
                "address": f"ул. Тестовая, д. {i}, кв. {i*2}",
                "specialty": spec,
                "course": (i % 4) + 1,
                "group": f"{spec[:2].upper()}-{(25 - (i%4))}",
                "gender": gender,
                "nationality": "Казах",
                "identity_card": f"ID-{10000000 + i}",
                "iin": f"0{4 + (i%3)}{(i%12)+1:02d}{(i%28)+1:02d}500{i:03d}",
            })

        for i, s_data in enumerate(STUDENTS_DATA, 1):
            u = User(
                email=s_data["email"],
                password_hash=get_password_hash("student123"),
                full_name=s_data["full_name"],
                role="student",
                parent_id=parent_user.id if i == 1 else None,
                phone=s_data["phone"],
                birth_date=s_data["birth_date"],
                city=s_data["city"],
                address=s_data["address"],
            )
            db.add(u)
            db.flush()
            
            db.add(
                StudentProfile(
                    user_id=u.id,
                    gender=s_data["gender"],
                    nationality=s_data["nationality"],
                    identity_card=s_data["identity_card"],
                    iin=s_data["iin"],
                    specialty=s_data["specialty"],
                    course=s_data["course"],
                    group=s_data["group"],
                    status="Активный",
                    interface_language="Казахский",
                    timezone="UTC+5",
                )
            )
        db.commit()
        db.refresh(admin_user)
        db.refresh(teacher1)
        db.refresh(teacher2)
        admin_id = admin_user.id
        t1_id = teacher1.id
        t2_id = teacher2.id
        student_ids = [db.query(User).filter(User.email == f"student{i}@edu.kz").first().id for i in range(1, 6)]

        # Categories
        cat_ids = []
        for name, desc, icon in COURSE_CATEGORIES:
            c = CourseCategory(name=name, description=desc, icon=icon)
            db.add(c)
            db.flush()
            cat_ids.append(c.id)
        db.commit()

        _seed_courses_only(db, admin_id, cat_ids)
        print("Seed completed: users, categories, 2 active courses with modules/topics/tests, 18 mock courses (all open).")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
