"use client";

import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "@/api/client";
import { useLanguage } from "@/context/LanguageContext";
import { ChevronLeft, Paperclip, CheckCircle, Clock, XCircle, Search, Save, Download, FileText, Check, Users, ChevronRight, PanelLeftClose, PanelLeftOpen } from "lucide-react";
import { useState, useMemo, useEffect } from "react";
import { MagicCard } from "@/components/ui/magic-card";

type RubricCriterion = { id: number; name: string; max_points: number };
type RubricGrade = { criterion_id: number; points: number };
type Submission = {
  id: number | null;
  student_id: number;
  student_name: string;
  submission_text: string | null;
  file_url: string | null;
  file_urls: string[];
  grade: number | null;
  teacher_comment: string | null;
  submitted_at: string | null;
  rubric_grades: RubricGrade[];
  status: "graded" | "pending" | "not_submitted";
};

type AssignmentDetails = {
  title: string;
  description: string;
  max_points: number;
  deadline: string | null;
  group_name: string;
};

export default function AssignmentDetailPage() {
  const { t } = useLanguage();
  const params = useParams();
  const router = useRouter();
  const id = Number(params.id);
  const queryClient = useQueryClient();

  const [selectedStudentId, setSelectedStudentId] = useState<number | null>(null);
  const [filter, setFilter] = useState<"all" | "pending" | "graded" | "not_submitted">("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
  const [grade, setGrade] = useState("");
  const [comment, setComment] = useState("");
  const [rubricGrades, setRubricGrades] = useState<Record<number, string>>({});
  const [showSavedToast, setShowSavedToast] = useState(false);

  const { data, isPending, isError } = useQuery({
    queryKey: ["assignment-submissions", id],
    queryFn: async () => {
      const { data: res } = await api.get<{ submissions: Submission[]; rubric: RubricCriterion[]; assignment: AssignmentDetails }>(
        `/teacher/assignments/${id}/submissions`
      );
      return res;
    },
    enabled: !!id,
  });

  const { t: trans } = useLanguage();

  const submissions = data?.submissions ?? [];
  const rubric = data?.rubric ?? [];
  const assignment = data?.assignment;

  const filteredSubmissions = useMemo(() => {
    return submissions.filter((s) => {
      if (filter !== "all" && s.status !== filter) return false;
      if (searchQuery && !s.student_name.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  }, [submissions, filter, searchQuery]);

  // When a student is selected, update the form state
  const handleSelectStudent = (s: Submission) => {
    setSelectedStudentId(s.student_id);
    setGrade(s.grade !== null ? String(s.grade) : "");
    setComment(s.teacher_comment ?? "");
    const grades: Record<number, string> = {};
    if (rubric.length) {
      rubric.forEach((c) => {
        const rg = s.rubric_grades?.find((g) => g.criterion_id === c.id);
        grades[c.id] = rg != null ? String(rg.points) : "";
      });
    }
    setRubricGrades(grades);
  };

  const selectedSubmission = useMemo(() => {
    return submissions.find((s) => s.student_id === selectedStudentId);
  }, [submissions, selectedStudentId]);

  // Navigation logic
  const currentIndex = useMemo(() => {
    if (selectedStudentId === null) return -1;
    return filteredSubmissions.findIndex(s => s.student_id === selectedStudentId);
  }, [filteredSubmissions, selectedStudentId]);

  const handleNextStudent = () => {
    if (currentIndex < filteredSubmissions.length - 1) {
      handleSelectStudent(filteredSubmissions[currentIndex + 1]);
    }
  };

  const handlePrevStudent = () => {
    if (currentIndex > 0) {
      handleSelectStudent(filteredSubmissions[currentIndex - 1]);
    }
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      
      if (e.key === "ArrowDown" || e.key === "j") handleNextStudent();
      if (e.key === "ArrowUp" || e.key === "k") handlePrevStudent();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [currentIndex, filteredSubmissions]);

  const gradeMutation = useMutation({
    mutationFn: async ({
      subId,
      g,
      c,
      grades,
    }: {
      subId: number;
      g?: number;
      c: string;
      grades?: RubricGrade[];
    }) => {
      await api.put(`/teacher/submissions/${subId}`, {
        grade: g,
        teacher_comment: c,
        grades,
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["assignment-submissions", id] });
      setShowSavedToast(true);
      setTimeout(() => setShowSavedToast(false), 2500);
    },
  });

  const handleGrade = () => {
    if (!selectedSubmission || !selectedSubmission.id) return;
    const hasRubric = rubric.length > 0;
    const grades: RubricGrade[] = hasRubric
      ? rubric.map((c) => ({
          criterion_id: c.id,
          points: parseFloat(rubricGrades[c.id] ?? "0") || 0,
        }))
      : [];
    const numericGrade = grade ? Number(grade) : undefined;
    if (hasRubric || numericGrade != null) {
      gradeMutation.mutate({
        subId: selectedSubmission.id,
        g: numericGrade,
        c: comment,
        grades: hasRubric ? grades : undefined,
      });
    }
  };

  const getStatusIcon = (status: Submission["status"]) => {
    switch (status) {
      case "graded": return <CheckCircle className="w-4 h-4 text-green-500" />;
      case "pending": return <Clock className="w-4 h-4 text-amber-500" />;
      case "not_submitted": return <XCircle className="w-4 h-4 text-red-400" />;
    }
  };

  const getStatusLabel = (status: Submission["status"]) => {
    switch (status) {
      case "graded": return t("teacherSubmissionStatusGraded" as any) || "Graded";
      case "pending": return t("teacherSubmissionStatusPending" as any) || "Pending";
      case "not_submitted": return t("teacherSubmissionStatusNotSubmitted" as any) || "Not submitted";
    }
  };

  if (isPending) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin w-10 h-10 border-2 border-[var(--qit-primary)] border-t-transparent rounded-full" />
      </div>
    );
  }

  if (isError || !assignment) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[400px] p-8 text-center">
        <div className="w-16 h-16 bg-red-100 dark:bg-red-900/20 rounded-full flex items-center justify-center mb-4 text-red-600">
          <XCircle className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold mb-2">{t("errorLoadingSubmissions")}</h2>
        <p className="text-gray-500 mb-6 max-w-md">
          {t("errorFetchingDataDetail")}
        </p>
        <div className="flex gap-4">
          <button
            onClick={() => router.push("/app/teacher?tab=assignments")}
            className="px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-lg hover:bg-gray-200"
          >
            {t("back")}
          </button>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ["assignment-submissions", id] })}
            className="px-4 py-2 bg-[var(--qit-primary)] text-white rounded-lg"
          >
            {t("retry")}
          </button>
        </div>
      </div>
    );
  }

  const allFiles = selectedSubmission ? [
    ...(selectedSubmission.file_url ? [selectedSubmission.file_url] : []),
    ...(selectedSubmission.file_urls ?? [])
  ] : [];

  return (
    <div className="h-[calc(100vh-6rem)] flex flex-col -m-4 sm:-m-6 lg:-m-8 pb-4 sm:pb-6 lg:pb-8">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-4 sm:px-6 flex items-center justify-between shrink-0">
        <div>
          <button
            onClick={() => router.push("/app/teacher?tab=assignments")}
            className="inline-flex items-center gap-2 mb-2 text-sm text-gray-500 dark:text-gray-400 hover:text-[var(--qit-primary)] dark:hover:text-[#00b0ff] transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
            {t("teacherBack")}
          </button>
          <h1 className="text-xl sm:text-2xl font-bold text-gray-800 dark:text-white flex items-center gap-3">
            {assignment.title}
            <span className="text-xs font-medium px-2 py-1 rounded-full bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-300">
              {assignment.group_name}
            </span>
          </h1>
          <div className="mt-1 text-sm text-gray-500 flex gap-4">
            {assignment.deadline && <span>{(t("courseProgressDeadline" as any) || "Deadline")}: {new Date(assignment.deadline).toLocaleString()}</span>}
            <span>{t("teacherScore")}: max {assignment.max_points}</span>
          </div>
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">
        {/* Left Sidebar: Student List */}
        <div className={`border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 flex flex-col shrink-0 h-full overflow-hidden transition-all duration-300 ${isSidebarOpen ? "w-80" : "w-0"}`}>
          <div className="p-4 border-b border-gray-200 dark:border-gray-700 min-w-[320px]">
            <div className="relative mb-3">
              <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder={t("searchPlaceholder" as any) || "Find student..."}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-3 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-[var(--qit-primary)]"
              />
            </div>
            <div className="flex flex-wrap gap-1.5">
              {(["all", "pending", "graded", "not_submitted"] as const).map((f) => (
                <button
                  key={f}
                  onClick={() => setFilter(f)}
                  className={`px-2.5 py-1 text-xs font-medium rounded-full transition-colors ${
                    filter === f 
                      ? "bg-[var(--qit-primary)] text-white" 
                      : "bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
                  }`}
                >
                  {f === "all" ? t("teacherAllStudents" as any) || "All Students" : getStatusLabel(f)}
                </button>
              ))}
            </div>
          </div>
          <div className="flex-1 overflow-y-auto">
            {filteredSubmissions.length === 0 ? (
              <div className="p-8 text-center text-sm text-gray-500">{t("teacherNoSubmissions" as any) || "No submissions"}</div>
            ) : (
              <ul className="divide-y divide-gray-200 dark:divide-gray-700">
                {filteredSubmissions.map((s) => (
                  <li key={s.student_id}>
                    <button
                      onClick={() => handleSelectStudent(s)}
                      className={`w-full text-left p-4 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-center justify-between ${
                        selectedStudentId === s.student_id ? "bg-blue-50 dark:bg-blue-900/20 shadow-inner border-l-4 border-[var(--qit-primary)]" : "border-l-4 border-transparent"
                      }`}
                    >
                      <div className="min-w-0 pr-3">
                        <p className="font-medium text-gray-800 dark:text-white truncate">
                          {s.student_name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 flex items-center gap-1.5">
                          {getStatusIcon(s.status)}
                          {getStatusLabel(s.status)}
                        </p>
                      </div>
                      <div className="shrink-0 text-right">
                        {s.grade != null && <span className="text-sm font-bold text-green-600 dark:text-green-400">{s.grade} / {assignment.max_points}</span>}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        {/* Right Main Area: Submission Details */}
        <div className="flex-1 bg-gray-100 dark:bg-gray-900/80 overflow-y-auto w-full relative">
          
          {/* Quick Header for Actions */}
          <div className="sticky top-0 z-10 bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border-b border-gray-200 dark:border-gray-700 p-2 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className="p-2 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors"
                title={isSidebarOpen ? "Close sidebar" : "Open sidebar"}
              >
                {isSidebarOpen ? <PanelLeftClose className="w-5 h-5" /> : <PanelLeftOpen className="w-5 h-5" />}
              </button>
              {selectedSubmission && (
                <div className="flex items-center gap-2 px-2">
                  <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                    {selectedSubmission.student_name}
                  </span>
                  <div className={`w-2 h-2 rounded-full ${
                    selectedSubmission.status === 'graded' ? 'bg-green-500' : 
                    selectedSubmission.status === 'pending' ? 'bg-amber-500' : 'bg-red-400'
                  }`} />
                </div>
              )}
            </div>

            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 font-medium">
                {currentIndex + 1} / {filteredSubmissions.length}
              </span>
              <div className="flex border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                <button
                  onClick={handlePrevStudent}
                  disabled={currentIndex <= 0}
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-30 transition-colors border-r border-gray-200 dark:border-gray-700"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <button
                  onClick={handleNextStudent}
                  disabled={currentIndex >= filteredSubmissions.length - 1}
                  className="p-2 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-30 transition-colors"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          <div className="p-4 sm:p-6">
            {selectedSubmission ? (
              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 max-w-7xl mx-auto h-full items-start">
              
              {/* File Viewer */}
              <div className="xl:col-span-2 space-y-4">
                <MagicCard className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 relative overflow-hidden">
                  <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4 flex items-center gap-2">
                    <FileText className="w-5 h-5 text-blue-500" />
                    {t("teacherFilePreview" as any) || "File Preview"}
                  </h3>
                  
                  {selectedSubmission.submission_text && (
                    <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-xl mb-4 text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap border border-gray-200 dark:border-gray-600 shadow-sm leading-relaxed">
                      {selectedSubmission.submission_text}
                    </div>
                  )}

                  {allFiles.length > 0 ? (
                    <div className="space-y-4">
                      {allFiles.map((fileUrl, idx) => {
                        const isImage = fileUrl.match(/\.(jpeg|jpg|gif|png|webp)$/i);
                        const isPdf = fileUrl.match(/\.(pdf)$/i);
                        const filename = fileUrl.split('/').pop() || `Attachment ${idx + 1}`;
                        
                        return (
                          <div key={idx} className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden shadow-sm">
                            <div className="bg-gray-50 dark:bg-gray-900 px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
                              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2 truncate pr-4">
                                <Paperclip className="w-4 h-4 shrink-0" />
                                <span className="truncate">{filename}</span>
                              </span>
                              <a 
                                href={fileUrl} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="text-blue-600 dark:text-blue-400 hover:text-blue-800 p-2 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/30 transition-colors shrink-0"
                                title="Download"
                              >
                                <Download className="w-4 h-4" />
                              </a>
                            </div>
                            <div className="bg-gray-100 dark:bg-gray-950 flex items-center justify-center min-h-[300px] p-4 text-center">
                              {isImage ? (
                                <img src={fileUrl} alt="Preview" className="max-w-full max-h-[600px] object-contain rounded-lg shadow-md border border-gray-200 dark:border-gray-700" />
                              ) : isPdf ? (
                                <iframe src={fileUrl} className="w-full h-[600px] border-none bg-white rounded" title={`PDF Preview ${idx}`} />
                              ) : (
                                <div className="text-gray-500 dark:text-gray-400 flex flex-col items-center">
                                  <FileText className="w-16 h-16 mb-4 text-gray-300 dark:text-gray-600" />
                                  <p className="font-medium">{t("profileView")}</p>
                                  <a href={fileUrl} target="_blank" rel="noopener noreferrer" className="mt-3 text-sm text-[var(--qit-primary)] bg-[var(--qit-primary)]/10 px-4 py-2 rounded-lg hover:underline transition-all">
                                    {t("profileDownloadPDF" as any) || "Download file"}
                                  </a>
                                </div>
                              )}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    !selectedSubmission.submission_text && (
                      <div className="py-16 text-center text-gray-500 dark:text-gray-400 border-2 border-dashed border-gray-200 dark:border-gray-700 rounded-xl bg-gray-50/50 dark:bg-gray-900/30">
                        <FileText className="w-12 h-12 mx-auto mb-4 opacity-20" />
                        <p className="font-medium">{t("teacherNoSubmissions" as any) || "No files attached"}</p>
                      </div>
                    )
                  )}
                </MagicCard>
              </div>

              {/* Grading Panel */}
              <div className="xl:col-span-1 space-y-4">
                <MagicCard className="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-200 dark:border-gray-700 p-5 lg:sticky top-4">
                  <div className="flex items-center justify-between border-b border-gray-200 dark:border-gray-700 pb-4 mb-5">
                    <h3 className="text-lg font-semibold text-gray-800 dark:text-white">
                      {t("teacherGrade")}
                    </h3>
                    <div className="text-sm px-2.5 py-1 rounded-full bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 font-medium">
                      max {assignment.max_points}
                    </div>
                  </div>

                  {selectedSubmission.status === "not_submitted" ? (
                    <div className="text-sm text-gray-500 dark:text-gray-400 text-center py-8 bg-gray-50 dark:bg-gray-900/50 rounded-xl border border-gray-200 dark:border-gray-700">
                      <XCircle className="w-10 h-10 mx-auto mb-3 text-red-300 dark:text-red-900/50" />
                      <p className="font-medium">{t("teacherSubmissionStatusNotSubmitted" as any) || "Student has not submitted"}</p>
                    </div>
                  ) : (
                    <div className="space-y-5">
                      {rubric.length > 0 ? (
                        <div className="space-y-4">
                          <p className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
                            {t("teacherRubric")}
                          </p>
                          {rubric.map((c) => (
                            <div key={c.id} className="bg-gray-50/80 dark:bg-gray-900/50 p-3.5 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
                              <label className="text-sm font-medium text-gray-800 dark:text-gray-200 mb-2.5 flex justify-between">
                                <span>{c.name}</span>
                                <span className="text-gray-500 font-normal">max {c.max_points}</span>
                              </label>
                              <div className="relative">
                                <input
                                  type="number"
                                  min={0}
                                  max={c.max_points}
                                  step={0.5}
                                  value={rubricGrades[c.id] ?? ""}
                                  onChange={(e) =>
                                    setRubricGrades((prev) => ({ ...prev, [c.id]: e.target.value }))
                                  }
                                  className="w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg px-3 py-2 bg-white focus:ring-2 focus:ring-[var(--qit-primary)] focus:border-transparent outline-none transition-all font-medium"
                                  placeholder="0"
                                />
                              </div>
                            </div>
                          ))}
                          <div className="pt-3 my-2 flex justify-between items-center text-sm font-bold text-gray-800 dark:text-white border-t border-gray-200 dark:border-gray-700">
                            <span>{t("teacherTotalFromRubric")}:</span>
                            <span className="text-2xl text-[var(--qit-primary)] relative">
                              {rubric.reduce((sum, c) => sum + (parseFloat(rubricGrades[c.id] ?? "0") || 0), 0).toFixed(1)}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <div>
                          <label className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 block">
                            {t("teacherScore")} <span className="text-gray-400 font-normal ml-1">({assignment.max_points} max)</span>
                          </label>
                          <input
                            type="number"
                            min="0"
                            max={assignment.max_points}
                            placeholder="0"
                            value={grade}
                            onChange={(e) => setGrade(e.target.value)}
                            className="w-full text-xl font-medium border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-3 focus:ring-2 focus:ring-[var(--qit-primary)] focus:border-transparent outline-none transition-all shadow-sm"
                          />
                        </div>
                      )}
                      
                      <div className="pt-1">
                        <label className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2 block">
                          {t("teacherComment")}
                        </label>
                        <textarea
                          placeholder={t("teacherCommentPlaceholder" as any) || "Leave a comment for the student..."}
                          value={comment}
                          onChange={(e) => setComment(e.target.value)}
                          rows={4}
                          className="w-full border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-xl px-4 py-3 text-sm focus:ring-2 focus:ring-[var(--qit-primary)] focus:border-transparent outline-none transition-all shadow-sm resize-none"
                        />
                      </div>
                      
                      <button
                        onClick={handleGrade}
                        disabled={gradeMutation.isPending || !selectedSubmission.id}
                        className="w-full flex items-center justify-center gap-2 py-3.5 px-4 mt-2 rounded-xl text-white font-semibold transition-all hover:shadow-lg disabled:opacity-50 disabled:hover:shadow-none"
                        style={{ 
                          background: showSavedToast ? "#10B981" : "linear-gradient(135deg, var(--qit-primary) 0%, #00b0ff 100%)",
                          boxShadow: showSavedToast ? "0 4px 14px rgba(16, 185, 129, 0.4)" : "0 4px 14px rgba(0, 176, 255, 0.4)"
                        }}
                      >
                        {gradeMutation.isPending ? (
                          <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                        ) : showSavedToast ? (
                          <>
                            <Check className="w-5 h-5 flex-shrink-0" />
                            <span>{t("teacherWorkChecked")}</span>
                          </>
                        ) : (
                          <>
                            <Save className="w-5 h-5 flex-shrink-0" />
                            <span>{t("save")} / {t("teacherGrade")}</span>
                          </>
                        )}
                      </button>
                    </div>
                  )}
                </MagicCard>
              </div>

            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-500 dark:text-gray-400 max-w-sm mx-auto">
              <div className="w-20 h-20 bg-gray-200 dark:bg-gray-800 rounded-full flex items-center justify-center mb-6">
                <Users className="w-10 h-10 text-gray-400 dark:text-gray-500" />
              </div>
              <p className="text-xl font-semibold mb-2 text-gray-800 dark:text-gray-200 text-center">{t("teacherPickStudent" as any) || "No student selected"}</p>
              <p className="text-center text-sm">{t("teacherPickStudentDesc" as any) || "Select a student from the sidebar on the left to review their submission and assign a grade."}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  </div>
  );
}
