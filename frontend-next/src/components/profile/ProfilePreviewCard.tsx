"use client";

import type { ReactNode } from "react";
import { Loader2 } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";
import type { SafeProfilePreviewData } from "@/types/profiles";
import { getLocaleForLang, formatDateLocalized } from "@/lib/dateUtils";

type ProfilePreviewCardProps = {
  profile: SafeProfilePreviewData;
  className?: string;
};

type FieldItem = {
  label: string;
  value: ReactNode;
};

type Section = {
  title: string;
  items: FieldItem[];
};

function hasMeaningfulValue(value: unknown): boolean {
  if (value === null || value === undefined) return false;
  if (typeof value === "string") return value.trim().length > 0;
  if (Array.isArray(value)) return value.length > 0;
  return true;
}

function formatList(values?: string[] | null): string | null {
  if (!values || values.length === 0) return null;
  return values.filter(Boolean).join(", ");
}

function formatDate(value: string | null | undefined, lang: string): string | null {
  if (!value) return null;
  return formatDateLocalized(value, lang, { day: "numeric", month: "long", year: "numeric" });
}

function pickRoleLabel(profile: SafeProfilePreviewData, t: (key: any) => string): string {
  if (profile.role === "director") return t("director");
  if (profile.role === "teacher") return t("teacher");
  if (profile.role === "curator") return t("curator");
  if (profile.role === "admin") return t("roleAdmin");
  if (profile.role === "parent") return t("parent");
  if (profile.role === "student") return t("student");
  return profile.role;
}

function mapParentKinshipDegree(value: string | null | undefined, t: (key: any) => string): string {
  if (!value) return "";
  const normalizedValue = value.trim().toLowerCase();
  
  if (normalizedValue === "отец") return t("kinshipFather");
  if (normalizedValue === "мать") return t("kinshipMother");
  if (normalizedValue === "опекун") return t("kinshipGuardian");
  if (normalizedValue === "другое") return t("kinshipOther");
  return value;
}

function mapParentEducationalProcessRole(value: string | null | undefined, t: (key: any) => string): string {
  if (!value) return "";
  const normalizedValue = value.trim().toLowerCase();
  
  if (normalizedValue === "законный представитель") return t("eduRoleLegalRepresentative");
  if (normalizedValue === "опекун") return t("eduRoleGuardian");
  return value;
}

function mapStudyForm(value: string | null | undefined, t: (key: any) => string): string {
  if (!value) return "";
  const normalizedValue = value.trim().toLowerCase();

  if (normalizedValue === "очная") return t("profileStudyFullTime");
  if (normalizedValue === "заочная") return t("profileStudyPartTime");
  if (normalizedValue === "очно-заочная") return t("profileStudyMixed");
  return value;
}

function SectionCard({ title, items, className }: Section & { className?: string }) {
  if (!items.length) return null;

  return (
    <div className={`rounded-2xl border border-gray-200 dark:border-gray-700 bg-gray-50/80 dark:bg-gray-800/60 p-4 ${className ?? ""}`}>
      <h3 className="font-semibold text-gray-800 dark:text-white mb-3">{title}</h3>
      <dl className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {items.map((item) => (
          <div key={item.label} className="min-w-0">
            <dt className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">{item.label}</dt>
            <dd className="text-sm text-gray-700 dark:text-gray-200 break-words">{item.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export function ProfilePreviewCard({ profile, className }: ProfilePreviewCardProps) {
  const { t, lang } = useLanguage();

  const roleLabel = pickRoleLabel(profile, t);
  const memberSince = formatDate(profile.created_at, lang);
  
  // Mapping status to translated string
  let displayStatus = profile.status;
  if (profile.role === "student" && (!profile.status || profile.status === "Активный" || profile.status === "Активен")) {
    displayStatus = t("profileStatusActive");
  } else if (profile.status === "Активный" || profile.status === "Активен") {
    displayStatus = t("profileStatusActive");
  } else if (profile.status === "Неактивный" || profile.status === "Неактивен") {
    displayStatus = t("profileStatusInactive");
  }

  const baseSections: Section[] = [
    {
      title: t("profileBasicInfoSection"),
      items: [
        { label: t("profileFullName"), value: profile.full_name },
        { label: t("role"), value: roleLabel },
        { label: t("profileStatus"), value: displayStatus ?? "—" },
        { label: t("profileCity"), value: profile.city ?? "—" },
      ].filter((item) => hasMeaningfulValue(item.value)) as FieldItem[],
    },
    {
      title: t("profileContactsSection"),
      items: [
        { label: t("profilePersonalEmail"), value: profile.email },
        { label: t("profilePhone"), value: profile.phone ?? "—" },
        { label: t("profileWorkEmail"), value: profile.email_work ?? "" },
        { label: t("profileWorkPhone"), value: profile.phone_work ?? "" },
      ].filter((item) => hasMeaningfulValue(item.value)) as FieldItem[],
    },
  ];

  if (profile.role === "student") {
    baseSections.push({
      title: t("profileEducationInfo"),
      items: [
        { label: t("profileSpecialty"), value: profile.specialty ?? "" },
        { label: t("profileCourse"), value: profile.course != null ? String(profile.course) : "" },
        { label: t("profileGroups"), value: profile.group ?? "" },
        { label: t("profileStudyForm"), value: mapStudyForm(profile.study_form, t) },
        { label: t("profileParent"), value: profile.parent?.full_name ? `${profile.parent.full_name}` : "" },
      ].filter((item) => hasMeaningfulValue(item.value)) as FieldItem[],
    });
  } else if (profile.role === "parent") {
    baseSections.push({
      title: t("profileWorkInfo"),
      items: [
        { label: t("profileWorkPlace"), value: profile.work_place ?? "" },
        { label: t("profilePosition"), value: profile.position ?? "" },
        { label: t("profileEducation"), value: profile.education ?? "" },
        { label: t("profileAcademicDegree"), value: profile.academic_degree ?? "" },
        {
          label: t("profileKinshipDegree"),
          value: mapParentKinshipDegree(profile.kinship_degree, t),
        },
        {
          label: t("profileEducationalProcessRole"),
          value: mapParentEducationalProcessRole(profile.educational_process_role, t),
        },
      ].filter((item) => hasMeaningfulValue(item.value)) as FieldItem[],
    });
  } else if (profile.role === "teacher") {
    baseSections.push({
      title: t("profileWorkInfo"),
      items: [
        { label: t("profilePosition"), value: profile.position ?? "" },
        { label: t("profileDepartment"), value: profile.department ?? "" },
        { label: t("profileEducation"), value: profile.education ?? "" },
        { label: t("profileAcademicDegree"), value: profile.academic_degree ?? "" },
        { label: t("profileOffice"), value: profile.office ?? "" },
        { label: t("profileEmploymentStatus"), value: profile.employment_status ?? "" },
        { label: t("profileEmployeeNumber"), value: profile.employee_number ?? "" },
        { label: t("profileReceptionHours"), value: profile.reception_hours ?? "" },
        { label: t("profileConsultationLocation"), value: profile.consultation_location ?? "" },
        { label: t("profileCuratedCourses"), value: formatList(profile.curated_courses) ?? "" },
        { label: t("profileSubjectsTaught"), value: formatList(profile.subjects_taught) ?? "" },
        { label: t("profileAcademicInterests"), value: profile.academic_interests ?? "" },
      ].filter((item) => hasMeaningfulValue(item.value)) as FieldItem[],
    });
  } else if (profile.role === "admin" || profile.role === "director") {
    baseSections.push({
      title: t("profileAccessInfo"),
      items: [
        { label: t("profilePosition"), value: profile.position ?? "" },
        { label: t("profileDepartment"), value: profile.department ?? "" },
        { label: t("profileEducationLevel"), value: profile.education_level ?? "" },
        { label: t("profileOffice"), value: profile.office ?? "" },
        { label: t("profileSystemRole"), value: profile.system_role ?? "" },
        { label: t("profilePermissions"), value: formatList(profile.permissions) ?? "" },
        { label: t("profileAreasOfResponsibility"), value: formatList(profile.areas_of_responsibility) ?? "" },
      ].filter((item) => hasMeaningfulValue(item.value)) as FieldItem[],
    });
  }

  const extraNotes: string[] = [];
  if (profile.description) extraNotes.push(profile.description);
  if (memberSince) extraNotes.push(`${t("profileMemberSince")} ${memberSince}`);

  const shouldSpanLastSectionFullWidth = baseSections.length % 2 === 1;

  return (
    <div className={className ?? ""}>
      <div className="rounded-[24px] border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg p-5 md:p-6">
        <div className="flex flex-col gap-5">
          <div>
            <p className="text-xs uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">{t("profilePublicPreview")}</p>
            <div className="h-px bg-gray-200 dark:bg-gray-700" />
          </div>
          <div className="flex flex-col md:flex-row md:items-center gap-4">
            <div className="w-20 h-20 rounded-2xl bg-[var(--qit-primary)]/10 flex items-center justify-center overflow-hidden shrink-0">
              {profile.photo_url ? (
                <img src={profile.photo_url} alt="" className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-[var(--qit-primary)] font-semibold text-2xl">
                  {profile.full_name.charAt(0).toUpperCase()}
                </div>
              )}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <span className="inline-flex items-center rounded-full bg-[var(--qit-primary)]/10 px-3 py-1 text-xs font-semibold text-[var(--qit-primary)] dark:text-[#00b0ff]">
                  {roleLabel}
                </span>
                {displayStatus &&
                  (profile.role === "student" ? (
                    <>
                      {/* Desktop/tablet: keep the text badge */}
                      <span className="hidden sm:inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-3 py-1 text-xs font-medium text-gray-600 dark:text-gray-300">
                        {displayStatus}
                      </span>

                      {/* Mobile: round badge with rotating icon */}
                      <span className="sm:hidden inline-flex items-center justify-center rounded-full bg-[var(--qit-primary)]/10 border border-[var(--qit-primary)]/20 w-9 h-9 shrink-0">
                        <Loader2 className="w-4 h-4 text-[var(--qit-secondary)] animate-spin" />
                      </span>
                    </>
                  ) : (
                    <span className="inline-flex items-center rounded-full bg-gray-100 dark:bg-gray-700 px-3 py-1 text-xs font-medium text-gray-600 dark:text-gray-300">
                      {displayStatus}
                    </span>
                  ))}
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 dark:text-white break-words">{profile.full_name}</h2>
              <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1 text-sm text-gray-500 dark:text-gray-400">
                <span className="mobile-safe-text">{profile.email}</span>
                {profile.phone && <span>{profile.phone}</span>}
                {profile.city && <span>{profile.city}</span>}
              </div>
            </div>
          </div>

          {extraNotes.length > 0 && (
            <div className="rounded-2xl bg-gray-50 dark:bg-gray-700/50 px-4 py-3 text-sm text-gray-600 dark:text-gray-300">
              {extraNotes.map((note) => (
                <p key={note} className="break-words">
                  {note}
                </p>
              ))}
            </div>
          )}

          <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
            {baseSections.map((section, index) => (
              <SectionCard
                key={section.title}
                title={section.title}
                items={section.items}
                className={shouldSpanLastSectionFullWidth && index === baseSections.length - 1 ? "xl:col-span-2" : ""}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
