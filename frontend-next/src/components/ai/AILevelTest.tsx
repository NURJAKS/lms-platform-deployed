"use client";

import { useState } from "react";
import { useLanguage } from "@/context/LanguageContext";
import { useMutation, useQuery } from "@tanstack/react-query";
import { api } from "@/api/client";
import { motion, AnimatePresence } from "motion/react";
import { 
  CheckCircle2, 
  Brain, 
  ChevronRight, 
  Trophy, 
  Target, 
  Loader2, 
  Sparkles,
  ArrowRight,
  Settings2,
  GraduationCap
} from "lucide-react";
import { BlurFade } from "@/components/ui/blur-fade";
import { SparklesText } from "@/components/ui/sparkles-text";
import { useAuthStore } from "@/store/authStore";

interface DiagnosticQuestion {
  id: string;
  level: string;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
}

interface DiagnosticSubmitResponse {
  level: string;
  correct_by_level?: Record<string, number>;
  total_by_level?: Record<string, number>;
}

interface AILevelTestProps {
  onComplete: (level: string) => void;
}

export function AILevelTest({ onComplete }: AILevelTestProps) {
  const { t, lang } = useLanguage();
  const setAuth = useAuthStore(s => s.setAuth);
  const user = useAuthStore(s => s.user);
  const token = useAuthStore(s => s.token);

  const [step, setStep] = useState<"intro" | "quiz" | "calculating" | "result" | "manual">("intro");
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [answers, setAnswers] = useState<Array<{ question_id: string; answer: string }>>([]);
  const [determinedLevel, setDeterminedLevel] = useState<string | null>(null);

  const { data: questions, isLoading: loadingQuestions } = useQuery({
    queryKey: ["diagnostic-questions"],
    queryFn: async () => {
      const { data } = await api.get<DiagnosticQuestion[]>(`/challenge/diagnostic/questions?lang=${lang}`);
      return data;
    },
    enabled: step === "quiz",
    staleTime: Infinity,
  });

  const submitMutation = useMutation({
    mutationFn: async (payload: { answers: Array<{ question_id: string; answer: string }> }) => {
      const { data } = await api.post<DiagnosticSubmitResponse>("/challenge/diagnostic/submit", payload);
      return data;
    },
    onSuccess: (data) => {
      setDeterminedLevel(data.level);
      if (user && token) {
        setAuth({ ...user, ai_level: data.level }, token);
      }
      setStep("result");
    }
  });

  const manualSetMutation = useMutation({
    mutationFn: async (level: string) => {
      const { data } = await api.post<{ level: string }>("/challenge/level", { level });
      return data;
    },
    onSuccess: (data) => {
      setDeterminedLevel(data.level);
      if (user && token) {
        setAuth({ ...user, ai_level: data.level }, token);
      }
      setStep("result");
    }
  });

  const handleStart = () => setStep("quiz");
  const handleManual = () => setStep("manual");

  const handleAnswerSelect = (option: string) => {
    if (!questions) return;
    const q = questions[currentQIndex];
    const newAnswers = [...answers, { question_id: q.id, answer: option }];
    setAnswers(newAnswers);

    if (currentQIndex + 1 < questions.length) {
      setCurrentQIndex(currentQIndex + 1);
    } else {
      setStep("calculating");
      setTimeout(() => {
        submitMutation.mutate({ answers: newAnswers });
      }, 2000);
    }
  };

  const progress = questions ? ((currentQIndex) / questions.length) * 100 : 0;

  if (step === "intro") {
    return (
      <BlurFade>
        <div className="max-w-2xl mx-auto p-6 sm:p-10 rounded-3xl border border-purple-200 dark:border-purple-900/50 bg-white dark:bg-gray-900 shadow-2xl text-center space-y-8">
          <div className="w-20 h-20 bg-purple-100 dark:bg-purple-900/30 rounded-2xl flex items-center justify-center mx-auto text-purple-600 dark:text-purple-400">
            <Brain className="w-12 h-12" />
          </div>
          <div className="space-y-4">
            <SparklesText className="text-3xl font-bold">
              {lang === "kk" ? "Деңгейіңізді анықтайық" : lang === "en" ? "Let's find your level" : "Давайте определим ваш уровень"}
            </SparklesText>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              {lang === "kk" 
                ? "Персоналды оқу жоспарын құру үшін сіздің білім деңгейіңізді білуіміз керек. Бұл тест небәрі 2-3 минут алады." 
                : lang === "en" 
                  ? "To create a personal learning plan, we need to know your knowledge level. This test takes only 2-3 minutes." 
                  : "Чтобы создать персональный план обучения, нам нужно узнать ваш уровень знаний. Этот тест займет всего 2-3 минуты."}
            </p>
          </div>
          <ul className="text-left space-y-3 max-w-md mx-auto">
            <li className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
              <CheckCircle2 className="w-5 h-5 text-green-500" />
              <span>{lang === "kk" ? "9 қысқарақ сұрақ" : lang === "en" ? "9 short questions" : "9 коротких вопросов"}</span>
            </li>
             <li className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
              <Target className="w-5 h-5 text-blue-500" />
              <span>{lang === "kk" ? "Оқу деңгейін дәл анықтау" : lang === "en" ? "Accurate level detection" : "Точное определение уровня"}</span>
            </li>
             <li className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
              <Sparkles className="w-5 h-5 text-purple-500" />
              <span>{lang === "kk" ? "Жеке жоспар алу" : lang === "en" ? "Get personalized plan" : "Получение личного плана"}</span>
            </li>
          </ul>
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <button
              onClick={handleStart}
              className="px-10 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-2xl font-bold text-lg shadow-xl shadow-purple-500/20 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2"
            >
              {lang === "kk" ? "Тестілеуді бастау" : lang === "en" ? "Start Assessment" : "Начать тестирование"}
              <ArrowRight className="w-5 h-5" />
            </button>
            <button
              onClick={handleManual}
              className="px-8 py-4 bg-gray-50 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-2xl font-semibold hover:bg-gray-100 dark:hover:bg-gray-700 transition-all flex items-center justify-center gap-2"
            >
              <Settings2 className="w-5 h-5" />
              {lang === "kk" ? "Өз бетімен таңдау" : lang === "en" ? "Choose manually" : "Выбрать вручную"}
            </button>
          </div>
        </div>
      </BlurFade>
    );
  }

  if (step === "manual") {
    const levels = [
      { 
        id: "beginner", 
        label: t("aiLevelBeginner"), 
        desc: lang === "kk" ? "Программалауды енді бастадым" : lang === "en" ? "I'm just starting out" : "Я только начинаю" 
      },
      { 
        id: "intermediate", 
        label: t("aiLevelIntermediate"), 
        desc: lang === "kk" ? "Негіздерін білемін, тәжірибем бар" : lang === "en" ? "I have some experience" : "У меня есть базовый опыт" 
      },
      { 
        id: "expert", 
        label: t("aiLevelExpert"), 
        desc: lang === "kk" ? "Күрделі тапсырмаларды орындай аламын" : lang === "en" ? "I can solve complex tasks" : "Могу решать сложные задачи" 
      },
    ];

    return (
      <BlurFade>
        <div className="max-w-3xl mx-auto p-10 space-y-10 text-center">
          <div className="space-y-4">
            <h2 className="text-3xl font-bold">
              {lang === "kk" ? "Деңгейіңізді таңдаңыз" : lang === "en" ? "Select your level" : "Выберите ваш уровень"}
            </h2>
            <p className="text-gray-500 max-w-md mx-auto">
              {lang === "kk" ? "Біз сізге ең қолайлы жоспарды дайындаймыз" : lang === "en" ? "We will prepare the most suitable plan for you" : "Мы подготовим наиболее подходящий план для вас"}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
            {levels.map((lvl) => (
              <button
                key={lvl.id}
                disabled={manualSetMutation.isPending}
                onClick={() => manualSetMutation.mutate(lvl.id)}
                className="group relative p-6 rounded-3xl border-2 border-gray-100 dark:border-gray-800 hover:border-purple-600 dark:hover:border-purple-500 hover:bg-white dark:hover:bg-gray-800 shadow-sm hover:shadow-xl transition-all duration-300 text-left flex flex-col gap-4 disabled:opacity-50"
              >
                <div className="w-12 h-12 rounded-2xl bg-purple-50 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400 flex items-center justify-center group-hover:bg-purple-600 group-hover:text-white transition-colors">
                  <GraduationCap className="w-6 h-6" />
                </div>
                <div>
                  <div className="font-bold text-xl mb-1 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                    {lvl.label}
                  </div>
                  <div className="text-sm text-gray-400 leading-tight">
                    {lvl.desc}
                  </div>
                </div>
                {manualSetMutation.isPending && manualSetMutation.variables === lvl.id && (
                  <Loader2 className="absolute top-4 right-4 w-5 h-5 text-purple-600 animate-spin" />
                )}
              </button>
            ))}
          </div>

          <button 
            onClick={() => setStep("intro")}
            className="text-gray-400 hover:text-purple-600 transition-colors text-sm font-medium"
          >
            {lang === "kk" ? "Артқа қайту" : lang === "en" ? "Go back" : "Вернуться назад"}
          </button>
        </div>
      </BlurFade>
    );
  }

  if (step === "quiz") {
    if (loadingQuestions || !questions) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px] gap-4">
          <Loader2 className="w-10 h-10 text-purple-600 animate-spin" />
          <p className="text-gray-500">{t("loading")}</p>
        </div>
      );
    }

    const q = questions[currentQIndex];
    const optionByKey: Record<"a" | "b" | "c" | "d", string> = {
      a: q.option_a,
      b: q.option_b,
      c: q.option_c,
      d: q.option_d,
    };

    return (
      <div className="max-w-3xl mx-auto space-y-8">
        <div className="flex items-center justify-between px-2">
           <div className="text-sm font-bold text-purple-600 dark:text-purple-400 uppercase tracking-widest">
             {lang === "kk" ? "Диагностика" : lang === "en" ? "Diagnostic" : "Диагностика"}
           </div>
           <div className="text-sm text-gray-400 font-mono">
             {currentQIndex + 1} / {questions.length}
           </div>
        </div>
        
        <div className="w-full h-2 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
          <motion.div 
            className="h-full bg-purple-600"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
          />
        </div>

        <AnimatePresence mode="wait">
          <motion.div
            key={currentQIndex}
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50 }}
            className="p-8 sm:p-12 rounded-3xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-xl space-y-10"
          >
            <h3 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white leading-relaxed">
              {q.question_text}
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {(["a", "b", "c", "d"] as const).map((opt) => (
                <button
                  key={opt}
                  onClick={() => handleAnswerSelect(opt)}
                  className="group p-5 text-left rounded-2xl border-2 border-gray-100 dark:border-gray-800 hover:border-purple-600 dark:hover:border-purple-500 hover:bg-purple-50/50 dark:hover:bg-purple-900/10 transition-all active:scale-[0.98] flex items-center gap-4"
                >
                  <span className="w-10 h-10 rounded-xl bg-gray-50 dark:bg-gray-800 group-hover:bg-purple-600 group-hover:text-white flex items-center justify-center font-bold text-gray-500 transition-colors uppercase">
                    {opt}
                  </span>
                  <span className="flex-1 text-gray-700 dark:text-gray-300 font-medium">
                    {optionByKey[opt]}
                  </span>
                </button>
              ))}
            </div>
          </motion.div>
        </AnimatePresence>
      </div>
    );
  }

  if (step === "calculating") {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] space-y-8 p-6 text-center">
        <div className="relative">
          <div className="w-24 h-24 rounded-full border-4 border-purple-100 dark:border-purple-900/30 border-t-purple-600 animate-spin" />
          <Brain className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-10 h-10 text-purple-600 animate-pulse" />
        </div>
        <div className="space-y-4">
          <h2 className="text-2xl font-bold">
            {lang === "kk" ? "Нәтижелерді есептеу..." : lang === "en" ? "Calculating results..." : "Расчет результатов..."}
          </h2>
          <p className="text-gray-500 dark:text-gray-400">
            {lang === "kk" ? "Біз сіздің жауаптарыңызды талдап жатырмыз." : lang === "en" ? "We are analyzing your patterns." : "Мы анализируем ваши паттерны ответов."}
          </p>
        </div>
      </div>
    );
  }

  if (step === "result") {
    const levelLabel = determinedLevel === "expert" ? t("aiLevelExpert") : determinedLevel === "beginner" ? t("aiLevelBeginner") : t("aiLevelIntermediate");
    
    return (
      <BlurFade>
        <div className="max-w-2xl mx-auto p-10 rounded-[32px] border border-green-200 dark:border-green-900/50 bg-white dark:bg-gray-900 shadow-2xl text-center space-y-8">
          <div className="w-24 h-24 bg-green-100 dark:bg-green-900/30 rounded-3xl flex items-center justify-center mx-auto text-green-600 dark:text-green-400 rotate-3">
             <Trophy className="w-14 h-14" />
          </div>
          
          <div className="space-y-2">
            <p className="text-green-600 dark:text-green-400 font-bold uppercase tracking-widest text-sm">
              {lang === "kk" ? "Тест аяқталды!" : lang === "en" ? "Test Completed!" : "Тест завершен!"}
            </p>
            <h2 className="text-3xl font-bold">
              {lang === "kk" ? "Сіздің деңгейіңіз:" : lang === "en" ? "Your level is:" : "Ваш уровень:"}
            </h2>
            <div className="inline-block px-6 py-2 rounded-2xl bg-purple-600 text-white font-black text-2xl mt-4 shadow-lg shadow-purple-500/30">
               {levelLabel}
            </div>
          </div>

          <p className="text-gray-600 dark:text-gray-400">
            {lang === "kk" 
              ? "Керемет! Енді біз сіздің деңгейіңізге сәйкес оқу жоспарын ұсына аламыз." 
              : lang === "en" 
                ? "Great! Now we can provide a learning path tailored to your specific proficiency." 
                : "Отлично! Теперь мы можем предложить план обучения, адаптированный под ваш уровень."}
          </p>

          <button
            onClick={() => onComplete(determinedLevel!)}
            className="w-full px-10 py-5 bg-gray-900 dark:bg-white dark:text-gray-900 text-white rounded-2xl font-bold text-xl shadow-xl hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-3"
          >
            {lang === "kk" ? "Планды көру" : lang === "en" ? "View My Plan" : "Посмотреть план"}
            <ChevronRight className="w-6 h-6" />
          </button>
        </div>
      </BlurFade>
    );
  }

  return null;
}
